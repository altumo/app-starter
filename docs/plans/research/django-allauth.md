# django-allauth Research

Research date: 2026-03-06

---

## 1. Current Version and Installation

### Version

- **Latest stable**: 65.14.2 (released 2026-02-13)
- **Django 5.2 support**: officially added in v65.7.0 (2025-04-03)

### Requirements

- Python 3.8 - 3.13
- Django 4.2+

### Installation

```bash
# Account-only (email/password auth, no social providers)
pip install django-allauth

# With social account providers (Google, GitHub, etc.)
pip install "django-allauth[socialaccount]"

# With headless/API mode (for SPA frontends)
pip install "django-allauth[headless]"

# With MFA support
pip install "django-allauth[mfa]"
```

After installation, run migrations:

```bash
python manage.py migrate
```

---

## 2. Required INSTALLED_APPS

### Minimal (account-only, no social providers)

```python
INSTALLED_APPS = [
    # Django defaults (required by allauth)
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # allauth
    "allauth",
    "allauth.account",
]
```

### With social accounts

```python
INSTALLED_APPS = [
    # ... Django defaults ...
    "django.contrib.sites",        # required for social accounts

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Provider-specific:
    # "allauth.socialaccount.providers.google",
    # "allauth.socialaccount.providers.github",
]

SITE_ID = 1  # required when using django.contrib.sites
```

### Optional add-ons

```python
    "allauth.headless",       # headless/API mode for SPAs
    "allauth.mfa",            # multi-factor authentication (TOTP, WebAuthn, passkeys)
    "allauth.usersessions",   # user session management
```

**Key point**: `django.contrib.sites` and `SITE_ID` are only required when using `allauth.socialaccount`. For account-only (email/password) usage, they are not needed.

---

## 3. Required MIDDLEWARE

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Required by allauth — must come after AuthenticationMiddleware
    "allauth.account.middleware.AccountMiddleware",
]
```

The `AccountMiddleware` is the only allauth-specific middleware. It must be present and should come after Django's `AuthenticationMiddleware`.

---

## 4. Required Settings

### AUTHENTICATION_BACKENDS

```python
AUTHENTICATION_BACKENDS = [
    # Default Django backend (needed for admin login by username)
    "django.contrib.auth.backends.ModelBackend",
    # allauth backend (enables login by email)
    "allauth.account.auth_backends.AuthenticationBackend",
]
```

### TEMPLATES (context processor)

The `request` context processor is required:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",  # REQUIRED by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

### ACCOUNT_* Settings — New-Style (v65.4.0+)

Starting with v65.4.0, allauth introduced `ACCOUNT_LOGIN_METHODS` and `ACCOUNT_SIGNUP_FIELDS` as replacements for the older `ACCOUNT_AUTHENTICATION_METHOD`, `ACCOUNT_EMAIL_REQUIRED`, and `ACCOUNT_USERNAME_REQUIRED`. The old settings still work (backwards-compatible) but the new ones are preferred.

#### For email/password auth (no username):

```python
# New-style settings (v65.4.0+, recommended)
ACCOUNT_LOGIN_METHODS = {"email"}                          # login via email only
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]  # no username field
ACCOUNT_USER_MODEL_USERNAME_FIELD = None                   # custom User has no username

# Email verification
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # "mandatory" | "optional" | "none"

# Other recommended settings
ACCOUNT_UNIQUE_EMAIL = True               # default: True — enforce unique emails
ACCOUNT_SESSION_REMEMBER = True           # default: None — always remember sessions
ACCOUNT_CHANGE_EMAIL = True               # restrict to one email, enable change flow
ACCOUNT_EMAIL_NOTIFICATIONS = True        # send security notifications (password changed, etc.)
ACCOUNT_CONFIRM_EMAIL_ON_GET = False      # default: False — require POST for confirmation (safer)
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[MySite] "
ACCOUNT_PREVENT_ENUMERATION = True        # default: True — don't reveal if account exists
```

#### Equivalent old-style settings (still work, for reference):

```python
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
```

### All ACCOUNT_* Settings Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `ACCOUNT_ADAPTER` | `"allauth.account.adapter.DefaultAccountAdapter"` | Custom adapter class |
| `ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS` | `True` | Redirect logged-in users away from login/signup pages |
| `ACCOUNT_CHANGE_EMAIL` | `False` | When True: one email only, with change flow |
| `ACCOUNT_CONFIRM_EMAIL_ON_GET` | `False` | Auto-confirm on GET (less secure) |
| `ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS` | `3` | Confirmation link expiry |
| `ACCOUNT_EMAIL_NOTIFICATIONS` | `False` | Security notifications (password change, etc.) |
| `ACCOUNT_EMAIL_SUBJECT_PREFIX` | `"[Site] "` | Email subject prefix |
| `ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS` | `True` | Send password reset even for non-existent accounts |
| `ACCOUNT_EMAIL_VERIFICATION` | `"optional"` | `"mandatory"`, `"optional"`, or `"none"` |
| `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED` | `False` | Use code instead of link for verification |
| `ACCOUNT_FORMS` | `{}` | Override built-in forms |
| `ACCOUNT_LOGIN_BY_CODE_ENABLED` | `False` | Enable magic code login (passwordless) |
| `ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS` | `3` | Max code entry attempts |
| `ACCOUNT_LOGIN_BY_CODE_TIMEOUT` | `180` | Code expiry in seconds |
| `ACCOUNT_LOGIN_METHODS` | `{"username"}` | Set of login methods: `"email"` and/or `"username"` |
| `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION` | `False` | Auto-login after email confirmation |
| `ACCOUNT_LOGIN_TIMEOUT` | `900` | Max time for login flow (seconds) |
| `ACCOUNT_LOGOUT_ON_GET` | `False` | Allow logout via GET (less secure) |
| `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE` | `False` | Invalidate sessions on password change |
| `ACCOUNT_MAX_EMAIL_ADDRESSES` | `None` | Max emails per user |
| `ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED` | `False` | Password reset via code instead of link |
| `ACCOUNT_PRESERVE_USERNAME_CASING` | `True` | Keep original username casing |
| `ACCOUNT_PREVENT_ENUMERATION` | `True` | Don't reveal account existence |
| `ACCOUNT_RATE_LIMITS` | (see below) | Rate limiting config |
| `ACCOUNT_REAUTHENTICATION_REQUIRED` | `False` | Require re-auth for account changes |
| `ACCOUNT_REAUTHENTICATION_TIMEOUT` | `300` | Re-auth grace period (seconds) |
| `ACCOUNT_SESSION_REMEMBER` | `None` | `None` (ask), `True` (always), `False` (never) |
| `ACCOUNT_SIGNUP_FIELDS` | `["username*", "email", "password1*", "password2*"]` | Signup form fields |
| `ACCOUNT_SIGNUP_FORM_CLASS` | `None` | Custom signup form for extra fields |
| `ACCOUNT_SIGNUP_FORM_HONEYPOT_FIELD` | `None` | Honeypot field for spam prevention |
| `ACCOUNT_SIGNUP_REDIRECT_URL` | `settings.LOGIN_REDIRECT_URL` | Post-signup redirect |
| `ACCOUNT_UNIQUE_EMAIL` | `True` | Enforce email uniqueness |
| `ACCOUNT_USER_MODEL_EMAIL_FIELD` | `"email"` | Email field name on User model |
| `ACCOUNT_USER_MODEL_USERNAME_FIELD` | `"username"` | Username field name (or `None`) |
| `ACCOUNT_USERNAME_BLACKLIST` | `[]` | Prohibited usernames |
| `ACCOUNT_USERNAME_MIN_LENGTH` | `1` | Min username length |
| `ACCOUNT_USERNAME_VALIDATORS` | `None` | Custom username validators |

### Default Rate Limits

```python
ACCOUNT_RATE_LIMITS = {
    "change_password": "5/m/user",
    "manage_email": "10/m/user",
    "reset_password": "20/m/ip,5/m/key",
    "reauthenticate": "10/m/user",
    "reset_password_from_key": "20/m/ip",
    "signup": "20/m/ip",
    "login": "30/m/ip",
    "login_failed": "10/m/ip,5/5m/key",
    "confirm_email": "1/3m/key",
}
```

Set `ACCOUNT_RATE_LIMITS = False` to disable all rate limiting (useful in tests).

---

## 5. URL Configuration

### urls.py

```python
from django.urls import path, include

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    # ...
]
```

### Available URL Routes

| URL Path | URL Name | View | Description |
|----------|----------|------|-------------|
| `accounts/login/` | `account_login` | `LoginView` | Login page |
| `accounts/logout/` | `account_logout` | `LogoutView` | Logout (POST required) |
| `accounts/signup/` | `account_signup` | `SignupView` | Registration page |
| `accounts/inactive/` | `account_inactive` | — | Inactive account page |
| `accounts/email/` | `account_email` | `EmailView` | Email management |
| `accounts/confirm-email/` | `account_email_verification_sent` | — | "Check your email" page |
| `accounts/confirm-email/<key>/` | `account_confirm_email` | `ConfirmEmailView` | Confirm email link |
| `accounts/password/change/` | `account_change_password` | `PasswordChangeView` | Change password (authenticated) |
| `accounts/password/set/` | `account_set_password` | `PasswordSetView` | Set password (if none exists) |
| `accounts/password/reset/` | `account_reset_password` | `PasswordResetView` | Request password reset |
| `accounts/password/reset/done/` | `account_reset_password_done` | — | Reset email sent |
| `accounts/password/reset/key/<uidb36>-<key>/` | `account_reset_password_from_key` | — | Reset password from link |
| `accounts/password/reset/key/done/` | `account_reset_password_from_key_done` | — | Reset complete |
| `accounts/reauthenticate/` | `account_reauthenticate` | — | Re-authentication |
| `accounts/login/code/` | `account_request_login_code` | — | Request magic login code |
| `accounts/login/code/confirm/` | `account_confirm_login_code` | — | Enter magic login code |
| `accounts/signup/passkey/` | `account_signup_by_passkey` | — | Passkey signup |

---

## 6. Template Override Structure

### How Template Resolution Works

allauth uses Django's template resolution order: `TEMPLATES[0]["DIRS"]` is searched before `APP_DIRS`. Place overrides in your project's `templates/` directory.

### Directory Layout for Overrides

```
templates/
  allauth/
    layouts/
      base.html              # Master layout for all allauth pages
      entrance.html           # Layout for login, signup (extends base.html)
      manage.html             # Layout for account management (extends base.html)
    elements/
      alert.html              # Alert/notification messages
      badge.html              # Labels and badges
      button.html             # Button component
      button_group.html       # Button groups
      field.html              # Single form field
      fields.html             # All form fields
      form.html               # Form container
      h1.html                 # Heading level 1
      h2.html                 # Heading level 2
      hr.html                 # Horizontal rule
      img.html                # Image element
      p.html                  # Paragraph
      panel.html              # Card/panel (title, body, actions)
      provider.html           # Social provider link
      provider_list.html      # Social provider list
      table.html              # Table and sub-elements
  account/
    login.html                # Login page content
    signup.html               # Signup page content
    logout.html               # Logout confirmation page
    email.html                # Email management page
    email_confirm.html        # Email confirmation page
    password_change.html      # Password change form
    password_reset.html       # Password reset request form
    password_set.html         # Set initial password
    password_reset_done.html  # "Reset email sent" page
    password_reset_from_key.html       # Enter new password
    password_reset_from_key_done.html  # Reset complete
    account_inactive.html     # Inactive account message
    verification_sent.html    # "Check your email" page
    # Email templates (plain text and HTML):
    email/
      email_confirmation_message.txt
      email_confirmation_subject.txt
      password_reset_key_message.txt
      password_reset_key_subject.txt
```

### Recommended Override Strategy

allauth provides a "layered" template system. Rather than overriding every `account/*.html` template, override the layout and element templates to style all pages at once:

1. **Override `allauth/layouts/base.html`** to integrate with your project's base template (navigation, CSS, etc.)
2. **Override element templates** (`allauth/elements/button.html`, `field.html`, `form.html`, etc.) to apply your CSS framework classes (e.g., Tailwind CSS)
3. **Override specific `account/*.html` templates** only when you need to change content/structure

### Template Tags

allauth provides custom template tags:

```django
{% load allauth %}
{% element h1 %}Welcome{% endelement %}
{% element form method="post" action=action_url %}
    {% slot body %}...form fields...{% endslot %}
    {% slot actions %}...submit button...{% endslot %}
{% endelement %}
```

Context variables available in element templates:
- `{{ origin }}` — the parent template name (e.g., `account/login`)
- `{{ attrs }}` — attributes passed to the element

---

## 7. Custom User Model with email as USERNAME_FIELD

### Custom User Model Definition

```python
# users/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email is already required as USERNAME_FIELD

    objects = UserManager()

    def __str__(self):
        return self.email
```

### Required Settings

```python
# settings.py

AUTH_USER_MODEL = "users.User"

# Tell allauth there is no username field
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Tell allauth the email field name (default is "email", explicit for clarity)
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"

# New-style login/signup config
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
```

### How It Works

- Setting `ACCOUNT_USER_MODEL_USERNAME_FIELD = None` tells allauth to completely disable all username-related functionality (no username in forms, no username validation, no `populate_username()` calls).
- allauth reads `AUTH_USER_MODEL` from Django settings to determine the User model.
- The `ACCOUNT_LOGIN_METHODS` and `ACCOUNT_SIGNUP_FIELDS` must align: since there is no username, login is by email and signup collects only email + password.
- allauth's `AuthenticationBackend` handles email-based lookups automatically.

### Adapter Customization (optional)

For advanced control over user creation:

```python
# users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """Populate User instance from signup form data."""
        user = super().save_user(request, user, form, commit=False)
        # Add custom fields here
        if commit:
            user.save()
        return user
```

```python
# settings.py
ACCOUNT_ADAPTER = "users.adapters.CustomAccountAdapter"
```

---

## 8. Best Practices for Email/Password Auth

### Recommended Settings

```python
# === Authentication ===
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# === Email Verification ===
ACCOUNT_EMAIL_VERIFICATION = "mandatory"   # require email verification before login
ACCOUNT_UNIQUE_EMAIL = True                # enforce unique emails
ACCOUNT_CONFIRM_EMAIL_ON_GET = False       # require POST (CSRF-safe)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

# === Security ===
ACCOUNT_PREVENT_ENUMERATION = True         # don't reveal if email is registered
ACCOUNT_EMAIL_NOTIFICATIONS = True         # notify on security events
ACCOUNT_SESSION_REMEMBER = True            # always use persistent sessions
ACCOUNT_LOGOUT_ON_GET = False              # require POST for logout (CSRF-safe)
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False  # keep user logged in after password change
ACCOUNT_REAUTHENTICATION_REQUIRED = False  # set True for sensitive apps

# === Rate Limiting ===
# Defaults are sensible; override only if needed
# ACCOUNT_RATE_LIMITS = { ... }

# === Redirects ===
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_SIGNUP_REDIRECT_URL = "/dashboard/"  # defaults to LOGIN_REDIRECT_URL
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
```

### Email Backend Configuration

For development:
```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

For production:
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.SmtpEmailBackend"
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "noreply@example.com"
EMAIL_HOST_PASSWORD = "..."
DEFAULT_FROM_EMAIL = "noreply@example.com"
```

### Security Best Practices

1. **Always use `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`** — prevents account takeover with typo'd emails and ensures email deliverability.
2. **Keep `ACCOUNT_PREVENT_ENUMERATION = True`** — password reset and signup don't reveal whether an email is registered.
3. **Keep `ACCOUNT_LOGOUT_ON_GET = False`** — logout requires POST with CSRF token, preventing CSRF-based logout attacks.
4. **Keep `ACCOUNT_CONFIRM_EMAIL_ON_GET = False`** — email confirmation requires POST, preventing pre-fetch/link-scanner issues.
5. **Enable `ACCOUNT_EMAIL_NOTIFICATIONS = True`** — users get notified of password changes with IP/user-agent info.
6. **Use built-in rate limiting** — defaults protect against brute-force login attempts and signup abuse.
7. **Consider `ACCOUNT_REAUTHENTICATION_REQUIRED = True`** for sensitive operations (email change, password change).

---

## 9. LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL

### How Redirects Work

django-allauth uses Django's standard `LOGIN_REDIRECT_URL` and adds its own redirect settings:

| Setting | Default | When Used |
|---------|---------|-----------|
| `LOGIN_REDIRECT_URL` | `"/accounts/profile/"` | After successful login (Django built-in) |
| `ACCOUNT_SIGNUP_REDIRECT_URL` | `settings.LOGIN_REDIRECT_URL` | After successful signup (if no email verification interrupts) |
| `ACCOUNT_LOGOUT_REDIRECT_URL` | `settings.LOGOUT_REDIRECT_URL` or `"/"` | After logout |
| `ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL` | `None` (falls back to `LOGIN_REDIRECT_URL`) | After email confirmation (authenticated user) |
| `ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS` | `True` | When True, redirects already-logged-in users away from login/signup to `LOGIN_REDIRECT_URL` |

### Configuration

```python
# settings.py
LOGIN_REDIRECT_URL = "/dashboard/"         # where to go after login
ACCOUNT_SIGNUP_REDIRECT_URL = "/onboarding/"  # where to go after signup (optional)
ACCOUNT_LOGOUT_REDIRECT_URL = "/"          # where to go after logout
```

### Important Behaviors

1. **`LOGIN_REDIRECT_URL`** — allauth respects Django's built-in setting. After a successful login (and email verification if mandatory), the user is redirected here. Accepts URL paths or URL names.

2. **`ACCOUNT_SIGNUP_REDIRECT_URL`** — Only used if signup completes without interruption. If `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, the user is redirected to the "check your email" page first, and `LOGIN_REDIRECT_URL` is used after they confirm and log in.

3. **`ACCOUNT_LOGOUT_REDIRECT_URL`** — Falls back to Django's `LOGOUT_REDIRECT_URL` first, then to `"/"` if neither is set.

4. **`next` query parameter** — allauth respects `?next=/some-path/` on login/signup URLs, overriding the default redirect. This is the standard Django behavior.

5. **`ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS`** — When True (default), visiting `/accounts/login/` or `/accounts/signup/` while already authenticated redirects to `LOGIN_REDIRECT_URL`. Set to False if you want authenticated users to see those pages.

---

## 10. Breaking Changes in Recent Versions

### v65.4.0 (2025-02-06)
- Introduced `ACCOUNT_LOGIN_METHODS` to replace `ACCOUNT_AUTHENTICATION_METHOD` (backwards-compatible).
- Introduced `ACCOUNT_SIGNUP_FIELDS` to replace `ACCOUNT_USERNAME_REQUIRED` / `ACCOUNT_EMAIL_REQUIRED` (backwards-compatible).

### v65.13.0 (2025-10-31)
- Headless mode now requires `pip install "django-allauth[headless]"` (extra required).

### v65.7.0 (2025-04-03)
- Added official Django 5.2 support.

---

## Sources

- [django-allauth official docs](https://docs.allauth.org/en/dev/)
- [Quickstart guide](https://docs.allauth.org/en/latest/installation/quickstart.html)
- [Account configuration reference](https://docs.allauth.org/en/dev/account/configuration.html)
- [Advanced usage (custom User model)](https://docs.allauth.org/en/dev/account/advanced.html)
- [Template system](https://docs.allauth.org/en/dev/common/templates.html)
- [Views reference](https://docs.allauth.org/en/dev/account/views.html)
- [Rate limits](https://docs.allauth.org/en/dev/account/rate_limits.html)
- [Release notes](https://docs.allauth.org/en/dev/release-notes/recent.html)
- [Requirements](https://docs.allauth.org/en/latest/installation/requirements.html)
- [URL patterns source](https://github.com/pennersr/django-allauth/blob/main/allauth/account/urls.py)
