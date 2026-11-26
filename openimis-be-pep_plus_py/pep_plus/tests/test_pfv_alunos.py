import os
import tempfile

from django.test import SimpleTestCase

from pep_plus import pfv_alunos as pfv

HEADER = ['NIA do Agregado', 'Encarregado/Beneficiário PFV', 'Vulgo do Beneficiário', 'Distrito', 'Localidade',
          'Nome do Aluno/Membro', 'Idade', 'Sexo', 'Estuda Atualmente? (CSU 2026)', 'Escola (CSU 2026)',
          'Classe/Grau (CSU 2026)', 'Boletin Recebido (SIM/NÃO)']


def _row(**kwargs):
    values = dict(sheet='S', row=2, nia='AA1AA1', guardian='Mãe', district='LOBATA', locality='Guadalupe',
                  name='Ana Costa', age=10, sex='F', studying=True, school='Escola Básica X', class_label='5ªclasse')
    values.update(kwargs)
    return pfv.StudentRow(**values)


class PfvClassesTest(SimpleTestCase):
    def test_class_labels(self):
        self.assertEqual(pfv.class_spec('4ªclasse'), pfv.ClassSpec('4', '4ª Classe', 'EP1', 4, 4))
        self.assertEqual(pfv.class_spec('10ª Classe').nivel, 'ESG2')
        self.assertEqual(pfv.class_spec('6ªclasse').nivel, 'EP2')
        self.assertEqual(pfv.class_spec('9ªclasse').nivel, 'ESG1')
        self.assertEqual(pfv.class_spec('Jardim de Infância').codigo, 'JI')
        self.assertEqual(pfv.class_spec('Creche').codigo, 'CRECHE')
        self.assertEqual(pfv.class_spec('Profissional 2ºano').codigo, 'PROF2')
        self.assertIsNone(pfv.class_spec('SEM INFORMAÇÃO'))
        self.assertIsNone(pfv.class_spec('13ªclasse'))

    def test_existing_class_code(self):
        self.assertEqual(pfv.existing_class_code('1', 'Primeira'), '1')
        self.assertEqual(pfv.existing_class_code('C07', '7ª Classe'), '7')
        self.assertEqual(pfv.existing_class_code('JI', 'Pré-escolar'), 'JI')
        self.assertIsNone(pfv.existing_class_code('EP1', 'Ensino Primário'))

    def test_subjects(self):
        self.assertEqual(pfv.subjects_for(pfv.class_spec('2ªclasse')), ['Língua Portuguesa', 'Matemática'])
        self.assertEqual(pfv.subjects_for(pfv.class_spec('11ªclasse')), ['Língua Portuguesa', 'Matemática'])
        self.assertIn('Química', pfv.subjects_for(pfv.class_spec('8ªclasse')))
        self.assertNotIn('Química', pfv.subjects_for(pfv.class_spec('7ªclasse')))
        self.assertEqual(pfv.subjects_for(pfv.class_spec('Jardim de Infância')), [])
        self.assertEqual(pfv.subject_level(pfv.class_spec('1ªclasse')), 'BASICA')
        self.assertEqual(pfv.subject_level(pfv.class_spec('6ªclasse')), 'BASICA')
        self.assertEqual(pfv.subject_level(pfv.class_spec('7ªclasse')), 'AVANCADA')
        self.assertEqual(pfv.subject_level(pfv.class_spec('12ªclasse')), 'AVANCADA')

    def test_academic_year(self):
        self.assertEqual(pfv.validate_academic_year('2025-2026'), '2025-2026')
        for value in ('2025/2026', '2025-2027', '2026', ''):
            with self.assertRaises(pfv.PlanilhaError):
                pfv.validate_academic_year(value)


class PfvSchoolsTest(SimpleTestCase):
    def test_district_and_level(self):
        rows = [
            _row(school='Escola  Básica X', district='LOBATA', class_label='3ªclasse'),
            _row(school='Escola Básica X', district='LOBATA', class_label='9ªclasse'),
            _row(school='Escola Básica X', district='MÉ-ZÓCHI', class_label='9ªclasse'),
            _row(school='Escola Básica X', district='LOBATA', class_label='Jardim de Infância'),
            _row(school='Jardim Y', district='CAUÉ', class_label='Jardim de Infância'),
            _row(school='Escola Z', studying=False),
            _row(school='SEM INFORMAÇÃO'),
        ]
        schools = pfv.collect_schools(rows)
        self.assertEqual(sorted(schools), ['ESCOLA BASICA X', 'JARDIM Y'])
        school = schools['ESCOLA BASICA X']
        self.assertEqual((school.district, school.nivel), ('LOBATA', 'ESG1'))
        self.assertEqual(schools['JARDIM Y'].nivel, 'OUTRO')

    def test_district_tie_is_deterministic(self):
        rows = [_row(district='LOBATA'), _row(district='CAUÉ')]
        self.assertEqual(pfv.collect_schools(rows)['ESCOLA BASICA X'].district, 'CAUÉ')


class PfvLevelTest(SimpleTestCase):
    def test_predominant_level(self):
        from collections import Counter
        self.assertEqual(pfv.predominant_level(Counter({'EP1': 50, 'ESG1': 3, 'OUTRO': 80})), 'EP1')
        self.assertEqual(pfv.predominant_level(Counter({'EP2': 4, 'EP1': 4})), 'EP1')
        self.assertEqual(pfv.predominant_level(Counter({'OUTRO': 9})), 'OUTRO')
        self.assertEqual(pfv.predominant_level(Counter()), 'OUTRO')


class PfvMemberMatchTest(SimpleTestCase):
    def test_match(self):
        members = [pfv.Candidate(1, 'ANA COSTA', 'F', 10), pfv.Candidate(2, 'RUI COSTA', 'M', 8)]
        self.assertEqual(pfv.match_member(_row(name='Ána  Costa'), members)[0].id, 1)
        self.assertEqual(pfv.match_member(_row(name='Ana Silva'), members), (None, 'não encontrado no agregado'))

    def test_repeated_name_uses_sex_and_age(self):
        members = [pfv.Candidate(1, 'ANA COSTA', 'F', 10), pfv.Candidate(2, 'ANA COSTA', 'F', 3)]
        self.assertEqual(pfv.match_member(_row(age=3), members)[0].id, 2)
        twins = [pfv.Candidate(1, 'ANA COSTA', 'F', 10), pfv.Candidate(2, 'ANA COSTA', 'F', 10)]
        member, reason = pfv.match_member(_row(), twins)
        self.assertIsNone(member)
        self.assertIn('nome repetido', reason)


class PfvPlanilhaTest(SimpleTestCase):
    def _write(self, sheets):
        import openpyxl

        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)
        for title, rows in sheets.items():
            sheet = workbook.create_sheet(title)
            for row in rows:
                sheet.append(row)
        handle, path = tempfile.mkstemp(suffix='.xlsx')
        os.close(handle)
        workbook.save(path)
        self.addCleanup(os.remove, path)
        return path

    def test_read(self):
        path = self._write({
            'LOBATA': [HEADER,
                       ['kw7xc5 ', 'Lurdes', 'Milu', 'LOBATA', 'Agostinho Neto', 'Elsy  Paquete', '10', '2. Feminino',
                        'Sim', 'Escola Básica Agostinho Neto', '5ªclasse', None],
                       [None] * len(HEADER),
                       ['KW7XC5', 'Lurdes', 'Milu', 'LOBATA', 'Agostinho Neto', 'Bebé', '1', '1. Masculino',
                        'SEM INFORMAÇÃO', 'SEM INFORMAÇÃO', 'SEM INFORMAÇÃO', None]],
            # Cantagalo tem colunas a mais (Escola Atual, Classe Atual)
            'CANTAGALO': [HEADER[:10] + ['Escola Atual', 'Classe/Grau (CSU 2026)', 'Classe Atual'],
                          ['KT1YX5', 'Nilza', 'N', 'CANTAGALO', 'Algés', 'Ariel', '8', '1. Masculino', 'Sim',
                           'Escola de Almas', None, '3ªclasse', None]],
        })
        rows = pfv.read_planilha(path)
        self.assertEqual(len(rows), 3)
        first = rows[0]
        self.assertEqual((first.nia, first.name, first.age, first.sex, first.studying, first.ref),
                         ('KW7XC5', 'Elsy Paquete', 10, 'F', True, 'LOBATA:2'))
        self.assertFalse(rows[1].studying)
        self.assertEqual((rows[2].class_label, rows[2].school), ('3ªclasse', 'Escola de Almas'))

    def test_missing_column(self):
        path = self._write({'X': [HEADER[:5]]})
        with self.assertRaises(pfv.PlanilhaError):
            pfv.read_planilha(path)
