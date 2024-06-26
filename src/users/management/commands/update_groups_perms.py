from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update permissions of all groups according to their base group permissions."

    def handle(self, *args, **options):
        groups = Group.objects.exclude(name__in=["ORG_LEAD", "ORG_USER", "CLUSTER_LEAD", "iMMAP_IMO"])

        cluster_lead_perms = Group.objects.get(name="CLUSTER_LEAD").permissions.all()

        for group in groups:
            if group.name.endswith("_CLUSTER_LEADS"):
                cluster_group_permissions = list(cluster_lead_perms)
                group.permissions.add(*cluster_group_permissions)
