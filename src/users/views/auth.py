from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from ..decorators import unauthenticated_user
from ..forms import (
    ProfileCreateForm,
    UserRegisterForm,
)
from ..tokens import account_activation_token


#############################################
########### Authentication Views #############
#############################################
def activate_account(request, uidb64, token):
    """Activate User account"""
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        messages.error(request, f"{e} - Something went wrong!")
        return redirect("login")

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        user.profile.email_verified_at = datetime.now()
        user.profile.save()

        messages.success(request, "Thank you for your email confirmation, you can login now into your account.")
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect("login")


def send_account_activation_email(request, user, to_email):
    """Email verification for resigtration"""
    current_site = get_current_site(request)
    mail_subject = "Email Activation link"
    message = loader.render_to_string(
        "users/emails/activation_email_template.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )

    email = EmailMultiAlternatives(mail_subject, "Testing", to=[to_email])
    email.attach_alternative(message, "text/html")
    if email.send():
        template = loader.get_template("users/auth/activation_email_done.html")
        context = {"user": user, "to_email": to_email}
        return HttpResponse(template.render(context, request))
    else:
        messages.error(
            request,
            f"""Problem sending email to <b>{to_email}</b>m check if you typed it correctly.""",
        )


@unauthenticated_user
def register_view(request):
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)
        p_form = ProfileCreateForm(request.POST)
        if u_form.is_valid() and p_form.is_valid():
            username = u_form.cleaned_data.get("username")
            email = u_form.clean_email()

            # Registration with email confirmation step.
            if settings.DEBUG:
                # If development mode then go ahead and create the user.
                user = u_form.save()
                user_profile = p_form.save(commit=False)
                user_profile.user = user

                user_profile.save()
                p_form.save_m2m()

                user.groups.add(Group.objects.get(name="ORG_USER"))

                messages.success(request, f"Account created successfully for {username}.")
                return redirect("login")
            else:
                # If production mode send a verification email to the user for account activation
                user = u_form.save(commit=False)
                user.is_active = False
                user.save()
                user_profile = p_form.save(commit=False)
                user_profile.user = user

                user_profile.save()
                p_form.save_m2m()

                user.groups.add(Group.objects.get(name="ORG_USER"))

                return send_account_activation_email(request, user, email)
        # else:
        #     for error in list(u_form.errors.values()):
        #         messages.error(request, error)
        #     for error in list(p_form.errors.values()):
        #         messages.error(request, error)
    else:
        u_form = UserRegisterForm()
        p_form = ProfileCreateForm()

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "users/auth/signup.html", context)


@unauthenticated_user
def login_view(request):
    template = loader.get_template("users/auth/login.html")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST.get("password")
        user = authenticate(request, username=email, email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.last_login:
                    messages.success(request, f"Welcome back {user}")
                else:
                    messages.success(request, f"Welcome {user} ! You've successfully logged in.")
                if "next" in request.POST:
                    return redirect(request.POST.get("next"))
                return redirect("landing")
            else:
                if not user.profile.email_verified_at:
                    # User is not verified, send them another verification email
                    send_account_activation_email(request, user, user.email)
                    messages.info(
                        request,
                        "Your account is not verified. We have sent you an email with instructions to verify your account.",
                    )
                else:
                    messages.error(request, "This account is deactivated. Please contact support.")
        else:
            messages.error(request, "Enter correct email or password.")
    context = {}
    return HttpResponse(template.render(context, request))


def logout_view(request):
    """User Logout View"""
    messages.info(request, f"{request.user} logged out.")
    logout(request)
    return redirect("/login")
