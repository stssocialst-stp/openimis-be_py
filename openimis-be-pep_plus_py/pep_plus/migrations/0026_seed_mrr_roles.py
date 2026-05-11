from django.db import migrations


# Right IDs do módulo grievance_social_protection
# 127000 — query tickets
# 127001 — create ticket
# 127002 — update ticket
# 127003 — delete ticket
# 127004 — query comments
# 127005 — create comment
# 127006 — resolve grievance

MRR_ROLES = [
    {
        'name': 'Salvaguarda',
        'rights': [127000, 127001, 127002, 127004, 127005, 127006],
    },
    {
        'name': 'Ponto Focal do MRR',
        'rights': [127000, 127001, 127002, 127004, 127005, 127006],
    },
    {
        'name': 'Conselheiro Técnico',
        'rights': [127000, 127004],
    },
    {
        'name': 'Directora da DPSSF',
        'rights': [127000, 127004],
    },
    {
        'name': 'Chefe de Departamento',
        'rights': [127000, 127001, 127004, 127005, 127006],
    },
    {
        'name': 'Coordenador MRR',
        'rights': [127000, 127001, 127004, 127005, 127006],
    },
    {
        'name': 'Consultor MRR',
        'rights': [127000, 127001, 127004, 127005, 127006],
    },
    {
        'name': 'Técnico Social MRR',
        'rights': [127000, 127001],
    },
    {
        'name': 'Ponto Focal MRR',
        'rights': [127000, 127001],
    },
    {
        'name': 'População MRR',
        'rights': [127001],  # apenas inserir reclamações, requer autenticação
    },
]


def seed_mrr_roles(apps, schema_editor):
    from django.utils import timezone
    from core.models import Role, RoleRight

    now = timezone.now()
    for role_def in MRR_ROLES:
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


def unseed_mrr_roles(apps, schema_editor):
    from django.utils import timezone
    from core.models import Role, RoleRight

    names = [r['name'] for r in MRR_ROLES]
    now = timezone.now()
    for role in Role.objects.filter(name__in=names, validity_to__isnull=True):
        RoleRight.objects.filter(role=role, validity_to__isnull=True).update(validity_to=now)
        role.validity_to = now
        role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pep_plus', '0025_add_pep_roles_and_me_roles'),
    ]

    operations = [
        migrations.RunPython(seed_mrr_roles, unseed_mrr_roles),
    ]
