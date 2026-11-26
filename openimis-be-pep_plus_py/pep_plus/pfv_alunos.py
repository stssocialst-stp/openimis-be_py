"""
Alunos do PFV — planilha de seguimento de boletins de matrícula (tirada do CSU 2026).

Leitura da planilha e regras de mapeamento (classes, disciplinas, escolas, correspondência
com os membros do agregado). Só as funções *_cache tocam na base de dados.
"""
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field

COL_NIA = 'NIA do Agregado'
COL_GUARDIAN = 'Encarregado/Beneficiário PFV'
COL_DISTRICT = 'Distrito'
COL_LOCALITY = 'Localidade'
COL_NAME = 'Nome do Aluno/Membro'
COL_AGE = 'Idade'
COL_SEX = 'Sexo'
COL_STUDYING = 'Estuda Atualmente? (CSU 2026)'
COL_SCHOOL = 'Escola (CSU 2026)'
COL_CLASS = 'Classe/Grau (CSU 2026)'
REQUIRED_COLUMNS = (COL_NIA, COL_GUARDIAN, COL_DISTRICT, COL_LOCALITY, COL_NAME,
                    COL_AGE, COL_SEX, COL_STUDYING, COL_SCHOOL, COL_CLASS)

NO_INFORMATION = 'SEM INFORMACAO'
ACADEMIC_YEAR = re.compile(r'^(\d{4})-(\d{4})$')

# Níveis (choices de Classe/Escola/Aluno), por ordem crescente
LEVELS = ('EP1', 'EP2', 'ESG1', 'ESG2')
LEVEL_OTHER = 'OUTRO'

# Disciplinas por classe (lista enviada pela DPSSF em 25/11/2026 — só 5ª a 9ª)
SUBJECTS_BY_CLASS = {
    5: ['Ciências Naturais e Sociais', 'Expressões Motora', 'Expressões Musical', 'Expressões Plástica',
        'Língua Francesa', 'Língua Portuguesa', 'Matemática'],
    6: ['Ciências Naturais e Sociais', 'Expressões Motora', 'Expressões Musical', 'Expressões Plástica',
        'Língua Francesa', 'Língua Portuguesa', 'Matemática'],
    7: ['Ciências Naturais', 'Geografia', 'História', 'Língua Francesa', 'Língua Inglesa',
        'Língua Portuguesa', 'Matemática', 'Física', 'Educação Visual e Oficinal', 'Educação p/ Saúde',
        'Educação Física'],
    8: ['Ciências Naturais', 'Geografia', 'História', 'Língua Francesa', 'Língua Inglesa',
        'Língua Portuguesa', 'Matemática', 'Física', 'Educação Visual e Oficinal', 'Educação Ambiental',
        'Educação Física', 'Química'],
    9: ['Ciências Naturais', 'Geografia', 'História', 'Língua Francesa', 'Língua Inglesa',
        'Língua Portuguesa', 'Matemática', 'Física', 'Educação Visual e Oficinal', 'Formação Cívica',
        'Educação Física', 'Química'],
}
# Enquanto não chega a lista completa, as restantes classes (1ª–4ª, 10ª–12ª) ficam com estas
CORE_SUBJECTS = ['Língua Portuguesa', 'Matemática']

DISTRICT_ALIASES = {
    'AGUAGRANDE': ['AGUAGRANDE'],
    'MEZOCHI': ['MEZOCHI'],
    'CANTAGALO': ['CANTAGALO'],
    'LEMBA': ['LEMBA'],
    'LOBATA': ['LOBATA'],
    'CAUE': ['CAUE'],
    'PAGUE': ['PAGUE', 'PRINCIPE', 'RAP', 'REGIAOAUTONOMADOPRINCIPE'],
    'RAP': ['PAGUE', 'PRINCIPE', 'RAP', 'REGIAOAUTONOMADOPRINCIPE'],
}


class PlanilhaError(Exception):
    pass


# ────────────────────────────────────────────────────────────
# Normalização
# ────────────────────────────────────────────────────────────

def strip_accents(value):
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()


def normalize_name(value):
    """Sem acentos, maiúsculas, espaços simples."""
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', strip_accents(str(value)).upper()).strip()


def normalize_key(value):
    """Só letras e dígitos: 'MÉ-ZÓCHI' → 'MEZOCHI'."""
    return re.sub(r'[^A-Z0-9]', '', normalize_name(value))


def clean_text(value):
    """Texto para gravar: sem espaços repetidos nas pontas ou no meio."""
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()


def has_information(value):
    return normalize_name(value) not in ('', NO_INFORMATION)


def sex_code(value):
    key = normalize_name(value)
    if key in ('M', '1. MASCULINO', 'MASCULINO'):
        return 'M'
    if key in ('F', '2. FEMININO', 'FEMININO'):
        return 'F'
    return ''


def to_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def validate_academic_year(value):
    """'2025-2026' — dois anos seguidos."""
    match = ACADEMIC_YEAR.match((value or '').strip())
    if not match or int(match.group(2)) != int(match.group(1)) + 1:
        raise PlanilhaError(f"Ano lectivo inválido: '{value}' (formato AAAA-AAAA, ex.: 2025-2026)")
    return value.strip()


# ────────────────────────────────────────────────────────────
# Classes, níveis e disciplinas
# ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ClassSpec:
    codigo: str
    nome: str
    nivel: str
    ordem: int
    numero: int = None  # 1–12 para as classes do ensino geral


def level_for_number(number):
    if 1 <= number <= 4:
        return 'EP1'
    if 5 <= number <= 6:
        return 'EP2'
    if 7 <= number <= 9:
        return 'ESG1'
    if 10 <= number <= 12:
        return 'ESG2'
    return LEVEL_OTHER


def class_spec(label):
    """'4ªclasse' / '4ª Classe' / '4' → 4ª Classe; Jardim, Creche e Profissional à parte."""
    key = normalize_name(label)
    if not key or key == NO_INFORMATION:
        return None
    match = re.match(r'^(\d{1,2})\s*[AO]?\s*(CLASSE)?$', key)
    if match:
        number = int(match.group(1))
        if 1 <= number <= 12:
            return ClassSpec(str(number), f'{number}ª Classe', level_for_number(number), number, number)
        return None
    if 'CRECHE' in key:
        return ClassSpec('CRECHE', 'Creche', LEVEL_OTHER, -1)
    if 'JARDIM' in key:
        return ClassSpec('JI', 'Jardim de Infância', LEVEL_OTHER, 0)
    match = re.match(r'^PROFISSIONAL\s*(\d)', key)
    if match:
        year = int(match.group(1))
        return ClassSpec(f'PROF{year}', f'Profissional {year}º ano', LEVEL_OTHER, 12 + year)
    return None


def existing_class_code(codigo, nome):
    """Código ClassSpec de uma Classe já registada (pelo código ou, se não servir, pelo nome)."""
    for value in (codigo, nome):
        spec = class_spec(value)
        if spec:
            return spec.codigo
    key = normalize_key(codigo)
    for spec_code in ('CRECHE', 'JI', 'PROF1', 'PROF2', 'PROF3'):
        if key == spec_code:
            return spec_code
    return None


def subjects_for(spec):
    """Disciplinas de uma classe: lista DPSSF (5ª–9ª) ou Português + Matemática (1ª–4ª, 10ª–12ª)."""
    if spec.numero is None:
        return []
    return SUBJECTS_BY_CLASS.get(spec.numero, CORE_SUBJECTS)


def subject_level(spec):
    """
    Nível das disciplinas de uma classe (DPSSF, 26/11/2026 — opção B): Ensino Básico (1ª–6ª) → BASICA,
    Ensino Secundário (7ª–12ª) → AVANCADA. Uma disciplina dos dois ciclos (ex.: Matemática) tem um
    registo por nível.
    """
    return 'BASICA' if spec.numero is not None and spec.numero <= 6 else 'AVANCADA'


def predominant_level(levels):
    """
    Nível com mais alunos (Counter nível → alunos), ignorando Jardim/Creche/Profissional quando
    há alunos do ensino geral; empate → o nível mais baixo. Só Jardim/Creche/Profissional → OUTRO.
    """
    general = {level: count for level, count in levels.items() if level in LEVELS and count}
    if not general:
        return LEVEL_OTHER
    return sorted(general.items(), key=lambda item: (-item[1], LEVELS.index(item[0])))[0][0]


# ────────────────────────────────────────────────────────────
# Planilha
# ────────────────────────────────────────────────────────────

@dataclass
class StudentRow:
    sheet: str
    row: int
    nia: str
    guardian: str
    district: str
    locality: str
    name: str
    age: int
    sex: str
    studying: bool
    school: str
    class_label: str

    @property
    def ref(self):
        return f'{self.sheet}:{self.row}'


def read_planilha(path):
    import openpyxl

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = []
    try:
        for sheet in workbook.worksheets:
            iterator = sheet.iter_rows(values_only=True)
            header = next(iterator, None)
            if not header:
                continue
            columns = {clean_text(value): index for index, value in enumerate(header) if value is not None}
            missing = [name for name in REQUIRED_COLUMNS if name not in columns]
            if missing:
                raise PlanilhaError(f"Folha '{sheet.title}': faltam as colunas {', '.join(missing)}")

            def cell(values, name):
                index = columns[name]
                return values[index] if index < len(values) else None

            for number, values in enumerate(iterator, start=2):
                if not values or all(value in (None, '') for value in values):
                    continue
                rows.append(StudentRow(
                    sheet=sheet.title,
                    row=number,
                    nia=clean_text(cell(values, COL_NIA)).upper(),
                    guardian=clean_text(cell(values, COL_GUARDIAN)),
                    district=clean_text(cell(values, COL_DISTRICT)),
                    locality=clean_text(cell(values, COL_LOCALITY)),
                    name=clean_text(cell(values, COL_NAME)),
                    age=to_int(cell(values, COL_AGE)),
                    sex=sex_code(cell(values, COL_SEX)),
                    studying=normalize_name(cell(values, COL_STUDYING)) == 'SIM',
                    school=clean_text(cell(values, COL_SCHOOL)),
                    class_label=clean_text(cell(values, COL_CLASS)),
                ))
    finally:
        workbook.close()
    return rows


# ────────────────────────────────────────────────────────────
# Escolas
# ────────────────────────────────────────────────────────────

@dataclass
class SchoolSpec:
    nome: str
    key: str
    districts: Counter = field(default_factory=Counter)
    levels: Counter = field(default_factory=Counter)

    @property
    def district(self):
        """Distrito com mais alunos (desempate alfabético, para ser determinístico)."""
        if not self.districts:
            return ''
        return sorted(self.districts.items(), key=lambda item: (-item[1], item[0]))[0][0]

    @property
    def nivel(self):
        return predominant_level(self.levels)


def collect_schools(rows):
    """Escolas dos alunos que estudam: nome, distrito e nível — os da maioria dos seus alunos."""
    schools = {}
    for row in rows:
        if not row.studying or not has_information(row.school):
            continue
        key = normalize_name(row.school)
        school = schools.setdefault(key, SchoolSpec(nome=row.school, key=key))
        school.districts[row.district] += 1
        spec = class_spec(row.class_label)
        if spec:
            school.levels[spec.nivel] += 1
    return schools


# ────────────────────────────────────────────────────────────
# Correspondência com os membros do agregado
# ────────────────────────────────────────────────────────────

@dataclass
class Candidate:
    id: object
    name_key: str
    sex: str = ''
    age: int = None
    member_key: str = ''


def match_member(row, candidates):
    """(candidato, None) ou (None, motivo). Nome igual; se repetido, desempata por sexo e idade."""
    name_key = normalize_name(row.name)
    same_name = [c for c in candidates if c.name_key == name_key]
    if not same_name:
        return None, 'não encontrado no agregado'
    if len(same_name) == 1:
        return same_name[0], None
    narrowed = [c for c in same_name if c.sex == row.sex and c.age == row.age]
    if len(narrowed) == 1:
        return narrowed[0], None
    return None, f'nome repetido no agregado ({len(same_name)} membros)'


# ────────────────────────────────────────────────────────────
# Localizações (base de dados)
# ────────────────────────────────────────────────────────────

def build_location_cache():
    """
    (distritos, localidades): distritos por chave normalizada ('MEZOCHI', 'RAP', ...);
    localidades por (id do distrito, chave) — só quando o nome é único dentro do distrito.
    """
    from location.models import Location

    locations = list(Location.objects.filter(validity_to__isnull=True).only('id', 'name', 'type', 'parent_id'))
    by_id = {location.id: location for location in locations}
    by_key = {}
    for location in locations:
        key = normalize_key(location.name)
        if key not in by_key or location.type == 'D':
            by_key[key] = location
    districts = {}
    for district, accepted in DISTRICT_ALIASES.items():
        for key in accepted:
            if key in by_key:
                districts[district] = by_key[key]
                break

    district_ids = {location.id for location in districts.values()}
    found = defaultdict(list)
    for location in locations:
        if location.id in district_ids:
            continue
        parent_id, seen = location.parent_id, set()
        while parent_id and parent_id not in district_ids and parent_id not in seen:
            seen.add(parent_id)
            parent = by_id.get(parent_id)
            parent_id = parent.parent_id if parent else None
        if parent_id in district_ids:
            found[(parent_id, normalize_key(location.name))].append(location)
    localities = {key: items[0] for key, items in found.items() if len(items) == 1}
    return districts, localities
