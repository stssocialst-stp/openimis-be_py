from django.db import migrations


# 4 roles PEP+ alinhados com o documento (secção 7 do documento Ké-Nón)
PEP_DOC_ROLES = [
    {
        'name': 'Coordenação Geral PEP+',
        'rights': [
            159001,
            159011, 159012, 159013, 159014,
            159021, 159022, 159023,
            159031, 159032,
            159041,
            159051,
            159061, 159062,
            159071, 159072,
            159081, 159082,
            159091, 159092,
            159101, 159102,
            159111,
            159121, 159122,
        ],
    },
    {
        'name': 'Supervisão PEP+',
        'rights': [
            159001,
            159051,        # supervisão
            159101, 159102,  # relatório supervisão
        ],
    },
    {
        'name': 'Coordenação PEP+',
        'rights': [],  # sem rights — apenas nomes no sistema
    },
    {
        'name': 'Técnicos Formadores PEP+',
        'rights': [
            159001,
            159021, 159022,  # planeamento de sessões
            159031,          # presenças
            159041,          # execução
        ],
    },
]

# 3 roles para o Módulo Educacional (= Assiduidade Escolar, secção 5 do documento)
ME_ROLES = [
    {
        'name': 'Supervisora Geral — Módulo Educacional',
        'rights': [159001],  # só leitura
    },
    {
        'name': 'Administrador — Módulo Educacional',
        'rights': [159001, 159061, 159062],  # CRUD completo
    },
    {
        'name': 'Operador de Dados — Módulo Educacional',
        'rights': [159001, 159061],  # inserção mas sem eliminar
    },
]

ALL_ROLES = PEP_DOC_ROLES + ME_ROLES


def seed_roles(apps, schema_editor):
    from django.utils import timezone
    from core.models import Role, RoleRight

    now = timezone.now()
    for role_def in ALL_ROLES:
        role, _ = Role.objects.get_or_create(
            name=role_def['name'],
            validity_to__isnull=True,
            defaults={
                'is_system': 0,
                'is_blocked': False,
                'audit_user_id': -1,
                'validity_from': now,
            },
        )
        for right_id in role_def['rights']:
            RoleRight.objects.get_or_create(
                role=role,
                right_id=right_id,
                validity_to__isnull=True,
                defaults={
                    'audit_user_id': -1,
                    'validity_from': now,
                },
            )


def unseed_roles(apps, schema_editor):
    from django.utils import timezone
    from core.models import Role, RoleRight

    names = [r['name'] for r in ALL_ROLES]
    now = timezone.now()
    for role in Role.objects.filter(name__in=names, validity_to__isnull=True):
        RoleRight.objects.filter(role=role, validity_to__isnull=True).update(validity_to=now)
        role.validity_to = now
        role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0024_seed_pep_roles'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
