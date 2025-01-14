from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from rh.models import Cluster
from users.utils import assign_default_permissions_to_group


class Command(BaseCommand):
    help = "Create groups for existing organizations and clusters."

    def _cluster_groups(self):
        clusters = Cluster.objects.all()

        for cluster in clusters:
            cluster_group_name = f"{cluster.code.upper()}_CLUSTER_LEADS"
            group, _ = Group.objects.get_or_create(name=cluster_group_name)

            assign_default_permissions_to_group(source_group_name="BASE_CLUSTER_LEAD", target_group=group)

    def handle(self, *args, **options):
        self._cluster_groups()
