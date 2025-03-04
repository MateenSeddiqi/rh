import csv

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import NoReverseMatch, path, reverse
from django.utils.html import format_html

from .models import Profile


class GroupAdminCustom(GroupAdmin):
    change_list_template = "users/admin/groups_changelist.html"

    def run_groups_sync_command(self, request):
        try:
            call_command("create_cluster_groups")
        except Exception as e:
            self.message_user(request, f"Something went wrong - {e}", "error")

        self.message_user(request, "Groups synced to their base permissions", "success")

        return HttpResponseRedirect("../")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("sync_groups/", self.run_groups_sync_command),
        ]

        return my_urls + urls


admin.site.unregister(Group)
admin.site.register(Group, GroupAdminCustom)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"
    raw_id_fields = ["organization"]

    filter_horizontal = ("clusters",)


@admin.action(description="Mark selected users as active")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected users as inactive")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


class UserAdminCustom(UserAdmin):
    list_display = (
        "email",
        "username",
        "name",
        "organization",
        "is_active",
        "user_groups",
        "last_login",
        "profile__email_verified_at",
        "date_joined",
    )
    list_select_related = ["profile__organization"]
    date_hierarchy = "last_login"

    inlines = (ProfileInline,)
    actions = [make_active, make_inactive, export_as_csv]

    def user_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    def organization(self, obj):
        return obj.profile.organization

    def name(self, obj):
        try:
            url = reverse("admin:users_profile_change", args=[obj.profile.id])
            rh_url = reverse("profiles-show", args=[obj.username])
        except NoReverseMatch:
            url = "#"
            rh_url = "#"

        return format_html(
            "{} <em>(<a href='{}'>Profile</a></em>) (<em> <a target='_blank' href='{}'> RH-Profile </a></em>)",
            obj.get_full_name(),
            url,
            rh_url,
        )


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)


# ##############################################
# ########## Profile Model Admin ###########
# ##############################################


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_link", "organization", "country", "position", "created_at", "Clusters")
    search_fields = ("user__first_name", "user__username", "organization__code")
    list_filter = ("country", "clusters")
    raw_id_fields = ["organization", "user"]

    filter_horizontal = ("clusters",)

    def Clusters(self, obj):
        clusters = obj.clusters.all()
        return ", ".join([c.title for c in clusters])

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, "🔗here")

    # Hides the profile from admin sidebar
    def has_module_permission(self, request):
        return False


admin.site.register(Profile, ProfileAdmin)
