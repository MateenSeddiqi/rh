from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods, require_POST
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting

from ..filters import ActivityPlansFilter
from ..forms import (
    ActivityPlanForm,
    CashInKindDetailForm,
)
from ..models import (
    ActivityPlan,
    CashInKindDetail,
    DisaggregationLocation,
    ImplementationModalityType,
    Indicator,
    Project,
    TargetLocation,
    TransferMechanismType,
    UnitType,
)


@require_http_methods(["POST"])
def update_activity_plan_state(request, pk):
    new_state = request.POST.get("state", None)
    if new_state is None:
        messages.error(request, "Invalid input, state is required!")
        return HttpResponse(status=200)

    activity_plan = ActivityPlan.objects.get(id=pk)
    activity_plan.state = new_state
    activity_plan.save()
    messages.success(request, f"Activity Plan state updated to '{new_state}' !")

    return HttpResponse(200)


@login_required
def hx_show_indicator_details(request):
    try:
        indicator_id = request.POST.get("indicator", None)
        indicator = get_object_or_404(Indicator, pk=indicator_id)

        food = indicator.food
        package = indicator.package

        form = CashInKindDetailForm(indicator=indicator)
        context = {"cashinkind_form": form, "indicator": indicator}

        if indicator.implement_category and str(indicator.implement_category) == "Cash":
            return render(request, "rh/activity_plans/partials/_cash_in_kind_form_with_cash_sections.html", context)
        elif indicator.implement_category and str(indicator.implement_category) == "In Kind" and food:
            return render(request, "rh/activity_plans/partials/_cash_in_kind_form_with_food_sections.html", context)
        elif package:
            return render(request, "rh/activity_plans/partials/_cash_in_kind_form_with_package_sections.html", context)
        else:
            return HttpResponse("<p>No additional details required for this indicator.</p>")
    except Exception:
        pass

    return HttpResponse("<p>No additional details required for this indicator.</p>")


@login_required
def update_activity_plan(request, pk):
    """Update an existing activity plan"""
    activity_plan = get_object_or_404(ActivityPlan.objects.select_related("project"), pk=pk)
    # Get the related CashInKindDetail instance, or None if it doesn't exist
    cashinkind_instance = CashInKindDetail.objects.filter(activity_plan=activity_plan).first()

    if request.method == "POST":
        form = ActivityPlanForm(request.POST, instance=activity_plan)
        cashinkind_form = CashInKindDetailForm(
            request.POST, instance=cashinkind_instance, indicator=activity_plan.indicator
        )
        if form.is_valid() and cashinkind_form.is_valid():
            form.save()
            cashinkind_details = cashinkind_form.save(commit=False)
            cashinkind_details.activity_plan = activity_plan
            cashinkind_details.save()

            messages.success(
                request,
                mark_safe(
                    f'The Activity Plan "<a class="underline" href="{reverse("activity-plans-update", args=[activity_plan.pk])}">{activity_plan}</a>" was changed successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect("activity-plans-update", pk=activity_plan.pk)
            elif "_save" in request.POST:
                return redirect("activity-plans-list", project=activity_plan.project.pk)
            elif "_addanother" in request.POST:
                return redirect("activity-plans-create", project=activity_plan.project.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanForm(instance=activity_plan)
        cashinkind_form = CashInKindDetailForm(instance=cashinkind_instance, indicator=activity_plan.indicator)

    return render(
        request,
        "rh/activity_plans/activity_plan_form.html",
        {"form": form, "project": activity_plan.project, "cashinkind_form": cashinkind_form},
    )


@login_required
def create_activity_plan(request, project):
    """Create a new activity plan for a specific project"""
    project = get_object_or_404(Project, pk=project)

    if request.method == "POST":
        form = ActivityPlanForm(request.POST, project=project)
        cash_in_kind_form = CashInKindDetailForm(request.POST)

        # Validate both forms
        if form.is_valid() and cash_in_kind_form.is_valid():
            activity_plan = form.save(commit=False)
            activity_plan.project = project
            activity_plan.save()

            # Save CashInKindForm details if needed
            cash_in_kind_detail = cash_in_kind_form.save(commit=False)
            cash_in_kind_detail.activity_plan = activity_plan
            cash_in_kind_detail.save()

            messages.success(
                request,
                mark_safe(
                    f'The Activity Plan "<a class="underline" href="{reverse("activity-plans-update", args=[activity_plan.pk])}">{activity_plan}</a>" was added successfully.',
                ),
            )
            if "_save" in request.POST:
                return redirect("activity-plans-list", project=project.pk)
            elif "_addanother" in request.POST:
                return redirect("activity-plans-create", project=project.pk)
        else:
            messages.error(request, "There are errors in the form. Please check and try again.")
    else:
        form = ActivityPlanForm(project=project)
        cash_in_kind_form = CashInKindDetailForm()

    return render(
        request,
        "rh/activity_plans/activity_plan_form.html",
        {"form": form, "cash_in_kind_form": cash_in_kind_form, "project": project},
    )


@login_required
@require_http_methods(["DELETE"])
def delete_activity_plan(request, pk):
    """Delete the specific activity plan"""
    activity_plan = get_object_or_404(ActivityPlan, pk=pk)

    if activity_plan.activityplanreport_set.exists():
        # TODO: handle this better in the frontend
        messages.error(
            request, "Cannot delete activity plan with existing reports. Instead change the status to Archived."
        )
        return HttpResponse(status=200)

    activity_plan.delete()

    messages.success(request, "Activity plan and its target locations has been delete.")

    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        return HttpResponseClientRedirect(reverse("activity-plans-list", args=[activity_plan.project.id]))
    return HttpResponse(status=200)


@require_POST
@login_required
def copy_activity_plan(request, pk):
    """Copy only the activity plan not whole project"""
    new_activity_plan = get_object_or_404(ActivityPlan, pk=pk)

    target_locations = TargetLocation.objects.filter(activity_plan=new_activity_plan)
    cash_details = CashInKindDetail.objects.get(activity_plan=new_activity_plan)

    new_activity_plan.id = None
    new_activity_plan.state = "draft"

    new_activity_plan.save()

    cash_details.id = None
    cash_details.activity_plan = new_activity_plan
    cash_details.save()

    for location in target_locations:
        disagg_locations = DisaggregationLocation.objects.filter(
            target_location=location,
        )

        location.id = None
        location.state = "draft"
        location.activity_plan = new_activity_plan

        location.save()

        for dl in disagg_locations:
            dl.id = None
            dl.target_location = location

            dl.save()

    messages.success(request, "Activity plan and its Target Locations copied")

    return redirect("activity-plans-update", pk=new_activity_plan.id)


@login_required
def list_activity_plans(request, project):
    """List Activity Plans for a specific project
    url: projects/<pk:project>/activity-plans
    """
    project = get_object_or_404(Project, pk=project)

    ap_filter = ActivityPlansFilter(
        request.GET,
        request=request,
        queryset=ActivityPlan.objects.filter(project=project)
        .select_related("activity_domain", "activity_type", "indicator", "hrp_beneficiary")
        .annotate(target_location_count=Count("targetlocation"))
        .order_by("-updated_at"),
        project=project,
    )

    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)

    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(ap_filter.qs, per_page=per_page)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    activity_plans = paginator.get_page(page)
    activity_plans.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {"project": project, "activity_plans": activity_plans, "activity_plans_filter": ap_filter}

    return render(request, "rh/activity_plans/activity_plans_list.html", context)


# HTMX GET Request views
@login_required
def update_indicator_type(request):
    """Indicator related types fields"""
    indicator_id = request.GET.get("indicator")
    indicator = get_object_or_404(Indicator, pk=indicator_id)
    indicator_implement = indicator.implement_category
    implementation_type = ImplementationModalityType.objects.filter(type=indicator_implement)

    return render(request, "rh/projects/views/_indicator_types.html", {"options": implementation_type})


def get_transfer_mechanism_types(request):
    """Get transfer mechanism types"""
    implement_type_id = request.GET.get("implement_modality_type")
    implement_types = get_object_or_404(ImplementationModalityType, pk=implement_type_id)
    transfer_mechanism = TransferMechanismType.objects.filter(modality=implement_types)

    return render(request, "rh/projects/views/_indicator_types.html", {"options": transfer_mechanism})


def get_unit_types(request):
    """Get unit types"""
    transfer_mechanism_id = request.GET.get("transfer_mechanism_type")
    transfer_mechanism = get_object_or_404(TransferMechanismType, pk=transfer_mechanism_id)
    unit_types = UnitType.objects.filter(modality=transfer_mechanism.modality)

    return render(request, "rh/projects/views/_indicator_types.html", {"options": unit_types})
