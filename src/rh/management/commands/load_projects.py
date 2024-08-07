import os
from pathlib import Path

import pandas as pd
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from rh.models import (
    TargetLocation,
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    BeneficiaryType,
    Location,
    Cluster,
    Currency,
    Donor,
    GrantType,
    ImplementationModalityType,
    Indicator,
    Organization,
    PackageType,
    Project,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Import Projects"

    def _load_target_locations(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/target_locations.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)

        locations = df.to_dict(orient="records")
        for index, location in enumerate(locations):
            project = Project.objects.filter(old_id=location.get("project_id", "")).first()
            country = Location.objects.filter(code="AF").first()
            province = Location.objects.filter(code=location.get("admin1pcode", "").strip()).first()
            district = Location.objects.filter(code=location.get("admin2pcode", "").strip()).first()
            activity_plans = project.activityplan_set.all()
            for activity_plan in activity_plans:
                target_location, created = TargetLocation.objects.get_or_create(
                    project_id=project.id,
                    is_active=True,
                    state="in-progress",
                    activity_plan_id=activity_plan.id,
                    country_id=country.id,
                    province_id=province.id,
                    district_id=district.id,
                )
                target_location.save()

    def _load_activity_plans(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/activity_plans.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)

        plans = df.to_dict(orient="records")
        for index, plan in enumerate(plans):
            project = Project.objects.filter(old_id=plan.get("project_id", "")).first()
            activity_domain = ActivityDomain.objects.filter(code=plan.get("activity_type_id", "").strip()).first()
            activity_type = ActivityType.objects.filter(code=plan.get("activity_description_id", "").strip()).first()
            activity_detail = ActivityDetail.objects.filter(code=plan.get("activity_type_id", "").strip()).first()
            indicator = Indicator.objects.filter(name=plan.get("indicator_id", "").strip()).first()
            package_type = PackageType.objects.filter(name=plan.get("package_type_name", "")).first()
            unit_type = UnitType.objects.filter(name=plan.get("unit_type_name", "")).first()
            grant_type = GrantType.objects.filter(name=plan.get("grant_type_name", "")).first()
            transfer_category = TransferCategory.objects.filter(name=plan.get("transfer_category_name", "")).first()
            transfer_mechanism_type = TransferMechanismType.objects.filter(
                name=plan.get("mpc_mechanism_type_name", "")
            ).first()
            implement_modility_type = ImplementationModalityType.objects.filter(
                name=plan.get("mpc_delivery_type_name", "")
            ).first()
            beneficiary = BeneficiaryType.objects.filter(code=plan.get("beneficiary_type_id", "")).first()
            hrp_beneficiary = BeneficiaryType.objects.filter(code=plan.get("hrp_beneficiary_type_id", "")).first()

            activity_plan, created = ActivityPlan.objects.get_or_create(
                project_id=project.id,
                state="in-progress",
                activity_domain_id=activity_domain.id,
                activity_type_id=activity_type.id,
                activity_detail_id=activity_detail.id if activity_detail else None,
                indicator_id=indicator.id,
                beneficiary_id=beneficiary.id if beneficiary else None,
                hrp_beneficiary_id=hrp_beneficiary.id if hrp_beneficiary else None,
                beneficiary_category=plan.get("beneficiary_category_id", ""),
                total_set_target=plan.get("total_beneficiaries", 0),
                package_type_id=package_type.id if package_type else None,
                unit_type_id=unit_type.id if unit_type else None,
                grant_type_id=grant_type.id if grant_type else None,
                transfer_category_id=transfer_category.id if transfer_category else None,
                transfer_mechanism_type_id=transfer_mechanism_type.id if transfer_mechanism_type else None,
                implement_modility_type_id=implement_modility_type.id if implement_modility_type else None,
            )
            activity_plan.save()

    def _load_projects(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/projects.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)

        projects = df.to_dict(orient="records")

        for index, project_vals in enumerate(projects):
            # Convert the naive datetime to an aware datetime using the timezone
            aware_start_date = timezone.make_aware(project_vals.get("project_start_date", "test"))
            aware_end_date = timezone.make_aware(project_vals.get("project_end_date", "test"))

            project_code = project_vals.get("project_code")
            if not project_code:
                project_code = f"TEST-CODE-{index}"

            project, created = Project.objects.get_or_create(
                title=project_vals.get("project_title", "test"),
                code=project_code,
                start_date=aware_start_date,
                end_date=aware_end_date,
                state="in-progress",
                is_hrp_project=True if project_vals.get("project_hrp_project", False) == 1 else False,
                hrp_code=project_vals.get("project_hrp_code", "test"),
                budget=project_vals.get("project_budget", 0),
                description=project_vals.get("project_description", "test"),
                old_id=project_vals.get("_id", "test"),
            )

            # Set ManyToMany field values and related field values
            if created:
                cluster = Cluster.objects.filter(code=project_vals.get("cluster_id"))
                project.clusters.set(cluster)

                activity_types = project_vals.get("activity_type").split(",")
                activity_domains = ActivityDomain.objects.filter(code__in=activity_types)
                project.activity_domains.set(activity_domains)

                implementing_partners = project_vals.get("implementing_partners")
                if not implementing_partners:
                    project.implementing_partners.set([])
                else:
                    implementing_partners = project_vals.get("implementing_partners").split(",")
                    partners = Organization.objects.filter(code__in=implementing_partners)
                    project.implementing_partners.set(partners)

                programme_partners = project_vals.get("programme_partners")
                if not programme_partners:
                    project.programme_partners.set([])
                else:
                    partners = programme_partners.split(",")
                    organizations = Organization.objects.filter(code__in=partners)
                    project.programme_partners.set(organizations)

                project_donors = project_vals.get("project_donor")
                if project_donors:
                    donors_list = project_donors.split(",")
                    donors = Donor.objects.filter(code__in=donors_list)
                    project.donors.set(donors)

                users = User.objects.filter(
                    Q(username=project_vals.get("username", "test")) | Q(email=project_vals.get("email", "test"))
                )

                if users.exists():
                    user = users.first()
                    project.user = user
                    project.organization = user.profile.organization

                budget_currencies = Currency.objects.filter(
                    name=project_vals.get("project_budget_currency", "usd").upper()
                )
                if budget_currencies.exists():
                    budget_currency = budget_currencies.first()
                    project.budget_currency = budget_currency

                project.save()
        self.stdout.write(self.style.SUCCESS(f"{len(projects)} Projects - created successfully"))

    def _import_data(self):
        # Import Projects
        self._load_projects()
        self._load_activity_plans()
        self._load_target_locations()

    def handle(self, *args, **options):
        self._import_data()
