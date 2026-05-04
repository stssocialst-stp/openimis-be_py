from django.db import migrations


PEP_ROLES = [
    {
        'name': 'Coordenador Distrital PEP+',
        'rights': [
            159001,  # query pep
            159011, 159012, 159013, 159014,  # parametrização
            159021, 159022, 159023,  # sessão pep
            159031, 159032,  # presença
            159041,  # execução
            159051,  # supervisão
            159061, 159062,  # módulo educacional
            159071, 159072,  # grupo familiar
            159081, 159082,  # relatório distrital
            159091, 159092,  # roteiro reunião
            159101, 159102,  # relatório supervisão
            159111,  # encaminhamento
            159121, 159122,  # coordenação distrital
        ],
    },
    {
        'name': 'Técnico Social PEP+',
        'rights': [
            159001,
            159021, 159022,  # criar/editar sessão
            159031,  # gerir presença
            159041,  # execução
            159071,  # grupo familiar
            159111,  # encaminhamento
        ],
    },
    {
        'name': 'Técnico Administrativo PEP+',
        'rights': [
            159001,
            159061, 159062,  # módulo educacional
            159071, 159072,  # grupo familiar
            159081, 159082,  # relatório distrital
            159091, 159092,  # roteiro reunião
        ],
    },
    {
        'name': 'Técnico Formador PEP+',
        'rights': [
            159001,
            159021, 159022,  # sessão
            159031,  # presença
            159041,  # execução
            159051,  # supervisão
        ],
    },
]


def seed_roles(apps, schema_editor):
    from django.utils import timezone
    from core.models import Role, RoleRight

    now = timezone.now()
    for role_def in PEP_ROLES:
        role, created = Role.objects.get_or_create(
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
    from core.models import Role, RoleRight
    from django.utils import timezone

    names = [r['name'] for r in PEP_ROLES]
    now = timezone.now()
    for role in Role.objects.filter(name__in=names, validity_to__isnull=True):
        RoleRight.objects.filter(role=role, validity_to__isnull=True).update(
            validity_to=now
        )
        role.validity_to = now
        role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0023_fix_policy_renewal_duplicates'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
