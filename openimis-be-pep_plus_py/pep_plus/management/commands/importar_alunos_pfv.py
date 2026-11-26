"""
Management command: importar_alunos_pfv

Regista no PEP+ os alunos do PFV a partir da planilha de seguimento de boletins de matrícula
(extraída do CSU 2026), por esta ordem e na mesma transacção:

  1. Classes      — as da planilha (Creche, Jardim, 1ª–12ª, Profissional); as que já existem
                    (pelo código ou pelo nome) são reutilizadas.
  2. Disciplinas  — 5ª–9ª pela lista da DPSSF; 1ª–4ª e 10ª–12ª com Língua Portuguesa e Matemática
                    até chegar a lista completa. Nível: Básica (1ª–6ª) / Avançada (7ª–12ª), com um
                    registo por nível. Ligações Classe↔Disciplina só são acrescentadas.
  3. Escolas      — nome da planilha; distrito = distrito com mais alunos dessa escola;
                    nível = nível com mais alunos dessa escola (só Jardim/Creche → OUTRO).
                    As que já existem (pelo nome) não são alteradas.
  4. Alunos       — só as linhas "Estuda actualmente = Sim". O aluno é ligado ao membro do agregado
                    já importado do CSU (NIA + nome; nome repetido desempata por sexo e idade).
                    Nunca cria indivíduos. Aluno já existente: actualizado guardando a versão
                    anterior no histórico; com outro ano lectivo → conflito, sem alteração.

Requer a importação do CSU 2026 (import_csu_2026) já feita.

Uso:
    python manage.py importar_alunos_pfv planilha.xlsx --ano-lectivo 2025-2026 --dry-run --relatorio rel.csv
    python manage.py importar_alunos_pfv planilha.xlsx --ano-lectivo 2025-2026 --username admin
    python manage.py importar_alunos_pfv planilha.xlsx --ano-lectivo 2025-2026 --so-parametrizacao
"""
import csv
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pep_plus import pfv_alunos as pfv
from pep_plus.models import Aluno, Classe, ClasseDisciplina, Disciplina, Escola


class _DryRunRollback(Exception):
    pass


class _Report:
    def __init__(self):
        self.counts = Counter()
        self.conflicts = Counter()
        self.rows = []

    def add(self, section, detail, row=None):
        self.rows.append((section, row.ref if row else '', row.nia if row else '', row.name if row else '', detail))

    def conflict(self, row, reason, detail=None):
        self.conflicts[reason] += 1
        self.add('CONFLITO', f'{reason}: {detail}' if detail else reason, row)

    def export(self, path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as handle:
            writer = csv.writer(handle, delimiter=';')
            writer.writerow(['secção', 'folha:linha', 'NIA', 'nome', 'detalhe'])
            writer.writerows(self.rows)


class Command(BaseCommand):
    help = 'Regista classes, disciplinas, escolas e alunos do PFV a partir da planilha de boletins de matrícula.'

    def add_arguments(self, parser):
        parser.add_argument('excel_path', type=str, help='Planilha de seguimento de boletins de matrícula (XLSX)')
        parser.add_argument('--ano-lectivo', type=str, required=True,
                            help='Ano lectivo dos dados escolares da planilha (ex.: 2025-2026)')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Simula tudo e desfaz no fim')
        parser.add_argument('--username', type=str, default='admin',
                            help='Username openIMIS para auditoria (default: admin)')
        parser.add_argument('--so-parametrizacao', action='store_true', default=False,
                            help='Só classes, disciplinas e escolas (sem alunos)')
        parser.add_argument('--nia', type=str, nargs='*', default=None,
                            help='Registar só os alunos destes NIA (a parametrização é sempre completa)')
        parser.add_argument('--relatorio', type=str, default=None,
                            help='Exportar escolas, conflitos e avisos para este CSV')

    def handle(self, *args, **options):
        from core.models import User

        try:
            academic_year = pfv.validate_academic_year(options['ano_lectivo'])
            rows = pfv.read_planilha(options['excel_path'])
        except (pfv.PlanilhaError, OSError) as exc:
            raise CommandError(str(exc))
        user = User.objects.filter(username=options['username']).first()
        if not user:
            raise CommandError(f"Utilizador não encontrado: {options['username']}")

        dry_run = options['dry_run']
        report = _Report()
        students = [row for row in rows if row.studying]
        report.counts['linhas na planilha'] = len(rows)
        report.counts['linhas sem estudar (ignoradas)'] = len(rows) - len(students)
        if options['nia']:
            wanted = {nia.strip().upper() for nia in options['nia']}
            students = [row for row in students if row.nia in wanted]

        self.audit_user_id = user.id_for_audit
        self.report = report
        try:
            with transaction.atomic():
                districts, localities = pfv.build_location_cache()
                classes = self._ensure_classes(rows)
                self._ensure_subjects(classes)
                schools = self._ensure_schools(rows, districts)
                if not options['so_parametrizacao']:
                    self._import_students(students, classes, schools, districts, localities, academic_year)
                if dry_run:
                    raise _DryRunRollback()
        except _DryRunRollback:
            pass

        self._print(dry_run)
        if options['relatorio']:
            report.export(options['relatorio'])
            self.stdout.write(f"Relatório: {options['relatorio']}")

    # ── 1. Classes ──────────────────────────────────────────

    def _ensure_classes(self, rows):
        existing = defaultdict(list)
        for classe in Classe.objects.filter(validity_to__isnull=True):
            code = pfv.existing_class_code(classe.codigo, classe.nome)
            if code:
                existing[code].append(classe)

        specs = {}
        for row in rows:
            spec = pfv.class_spec(row.class_label)
            if spec:
                specs[spec.codigo] = spec
            elif row.studying:
                self.report.add('AVISO', f"classe não reconhecida: '{row.class_label}'", row)
        for number in range(1, 13):  # as 12 classes do ensino geral, mesmo sem alunos na planilha
            spec = pfv.class_spec(str(number))
            specs.setdefault(spec.codigo, spec)

        classes = {}
        for code, spec in sorted(specs.items(), key=lambda item: item[1].ordem):
            found = existing.get(code, [])
            if len(found) > 1:
                self.report.add('AVISO', f"{len(found)} classes registadas para '{spec.nome}'; usada a de código {found[0].codigo}")
            if found:
                classes[code] = (found[0], spec)
                self.report.counts['classes já existentes'] += 1
                continue
            classe = Classe(nome=spec.nome, codigo=spec.codigo, nivel=spec.nivel, ordem=spec.ordem, ativo=True)
            classe.audit_user_id = self.audit_user_id
            classe.save()
            classes[code] = (classe, spec)
            self.report.counts['classes criadas'] += 1
        return classes

    # ── 2. Disciplinas ──────────────────────────────────────

    def _ensure_subjects(self, classes):
        existing = defaultdict(list)
        for disciplina in Disciplina.objects.filter(validity_to__isnull=True):
            existing[(pfv.normalize_name(disciplina.nome), disciplina.nivel)].append(disciplina)

        subjects = {}
        for classe, spec in classes.values():
            level = pfv.subject_level(spec)
            for name in pfv.subjects_for(spec):
                key = (pfv.normalize_name(name), level)
                if key not in subjects:
                    if existing.get(key):
                        subjects[key] = existing[key][0]
                        self.report.counts['disciplinas já existentes'] += 1
                    else:
                        disciplina = Disciplina(nome=name, nivel=level, ativo=True)
                        disciplina.audit_user_id = self.audit_user_id
                        disciplina.save()
                        subjects[key] = disciplina
                        self.report.counts['disciplinas criadas'] += 1
                _, created = ClasseDisciplina.objects.get_or_create(classe=classe, disciplina=subjects[key])
                if created:
                    self.report.counts['ligações classe–disciplina criadas'] += 1

    # ── 3. Escolas ──────────────────────────────────────────

    def _ensure_schools(self, rows, districts):
        existing = defaultdict(list)
        for escola in Escola.objects.filter(validity_to__isnull=True):
            existing[pfv.normalize_name(escola.nome)].append(escola)

        schools = {}
        for key, spec in sorted(pfv.collect_schools(rows).items()):
            found = existing.get(key, [])
            if len(found) > 1:
                self.report.add('AVISO', f"{len(found)} escolas registadas com o nome '{spec.nome}'; usada a primeira")
            if found:
                schools[key] = found[0]
                self.report.counts['escolas já existentes'] += 1
                continue
            district = districts.get(pfv.normalize_key(spec.district))
            escola = Escola(nome=spec.nome, nivel=spec.nivel, distrito=district, ativo=True)
            escola.audit_user_id = self.audit_user_id
            escola.save()
            schools[key] = escola
            self.report.counts['escolas criadas'] += 1
            spread = ', '.join(f'{name} {count}' for name, count in spec.districts.most_common())
            levels = ', '.join(f'{name} {count}' for name, count in spec.levels.most_common())
            self.report.add('ESCOLA', f"{spec.nome} | distrito: {spec.district or '-'}"
                                      f"{'' if district else ' (não encontrado no sistema)'} | nível: {spec.nivel}"
                                      f" | alunos por distrito: {spread} | alunos por nível: {levels}")
            if len(spec.districts) > 1:
                self.report.counts['escolas com alunos de vários distritos'] += 1
        return schools

    # ── 4. Alunos ───────────────────────────────────────────

    def _import_students(self, students, classes, schools, districts, localities, academic_year):
        candidates = self._load_members({row.nia for row in students})
        current = defaultdict(list)
        member_ids = [c.id for group in candidates.values() for c in group]
        for start in range(0, len(member_ids), 1000):
            for aluno in Aluno.objects.filter(validity_to__isnull=True,
                                              individual_id__in=member_ids[start:start + 1000]):
                current[aluno.individual_id].append(aluno)
        used = {}
        next_code = self._child_code_generator()

        for row in students:
            member, reason = pfv.match_member(row, candidates.get(row.nia, []))
            if not member:
                self.report.conflict(row, reason if row.nia in candidates else 'NIA sem membros no sistema')
                continue
            if member.id in used:
                self.report.conflict(row, 'membro já ligado a outra linha', used[member.id])
                continue
            used[member.id] = row.ref

            spec = pfv.class_spec(row.class_label)
            classe = classes[spec.codigo][0] if spec else None
            escola = schools.get(pfv.normalize_name(row.school))
            district = districts.get(pfv.normalize_key(row.district))
            locality = localities.get((district.id, pfv.normalize_key(row.locality))) if district else None
            if not district:
                self.report.counts['alunos sem distrito no sistema'] += 1
            elif not locality:
                self.report.counts['alunos sem localidade no sistema'] += 1
            values = {
                'id_membro_crianca': member.member_key or None,
                'nome_encarregado': row.guardian or None,
                'sexo': row.sex or None,
                'distrito_id': district.id if district else None,
                'localidade_id': locality.id if locality else None,
                'escola_id': escola.id if escola else None,
                'classe_id': classe.id if classe else None,
                'escolaridade_actual': spec.nivel if spec else None,
                'ano_lectivo': academic_year,
                'ativo': True,
            }
            try:
                with transaction.atomic():
                    self._save_student(row, member, current.get(member.id, []), values, next_code)
            except Exception as exc:  # erro numa linha não pára as restantes
                self.report.conflict(row, 'erro', exc)

    def _save_student(self, row, member, existing, values, next_code):
        if len(existing) > 1:
            self.report.conflict(row, f'{len(existing)} alunos activos para o mesmo indivíduo')
            return
        if not existing:
            aluno = Aluno(individual_id=member.id, id_da_crianca=next_code(), **values)
            aluno.audit_user_id = self.audit_user_id
            aluno.save()
            self.report.counts['alunos criados'] += 1
            return

        aluno = existing[0]
        if aluno.ano_lectivo and aluno.ano_lectivo != values['ano_lectivo']:
            self.report.conflict(row, f'aluno já registado com o ano lectivo {aluno.ano_lectivo}')
            return
        changed = {name: value for name, value in values.items() if getattr(aluno, name) != value}
        if not changed:
            self.report.counts['alunos sem alterações'] += 1
            return
        aluno.save_history()
        for name, value in changed.items():
            setattr(aluno, name, value)
        aluno.audit_user_id = self.audit_user_id
        aluno.save()
        self.report.counts['alunos actualizados'] += 1
        self.report.add('ACTUALIZADO', 'campos: ' + ', '.join(sorted(changed)), row)

    def _load_members(self, nias):
        """NIA → membros (Individuals não eliminados com json_ext.agregado_id = NIA)."""
        from individual.models import Individual

        members = defaultdict(list)
        nias = sorted(nias)
        for start in range(0, len(nias), 500):
            chunk = nias[start:start + 500]
            queryset = (Individual.objects
                        .filter(is_deleted=False, json_ext__agregado_id__in=chunk)
                        .values_list('id', 'first_name', 'last_name', 'json_ext'))
            for individual_id, first_name, last_name, json_ext in queryset:
                json_ext = json_ext or {}
                csu = json_ext.get('csu2026') or {}
                members[str(json_ext.get('agregado_id')).strip().upper()].append(pfv.Candidate(
                    id=individual_id,
                    name_key=pfv.normalize_name(f'{first_name or ""} {last_name or ""}'),
                    sex=pfv.sex_code(json_ext.get('sexo')),
                    age=pfv.to_int((csu.get('respostas') or {}).get('idade')),
                    member_key=csu.get('member_key') or '',
                ))
        return members

    @staticmethod
    def _child_code_generator():
        """Mesmo formato do AlunoService (CRI-<ano>-00001), sem uma consulta por aluno."""
        from pep_plus.services import AlunoService

        first = AlunoService._generate_id_da_crianca()
        prefix, sequence = first.rsplit('-', 1)
        state = {'next': int(sequence)}

        def next_code():
            code = f"{prefix}-{str(state['next']).zfill(5)}"
            state['next'] += 1
            return code
        return next_code

    # ── Resumo ──────────────────────────────────────────────

    def _print(self, dry_run):
        title = 'SIMULAÇÃO (nada foi gravado)' if dry_run else 'IMPORTAÇÃO'
        self.stdout.write(f'\n=== {title} — alunos PFV ===')
        for name, value in self.report.counts.items():
            self.stdout.write(f'  {name}: {value}')
        if self.report.conflicts:
            self.stdout.write(f'  conflitos: {sum(self.report.conflicts.values())}')
            for reason, value in self.report.conflicts.most_common():
                self.stdout.write(f'    - {reason}: {value}')
