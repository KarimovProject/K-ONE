import os

css = """
/* Phase 19.3: Login Page Overrides */

/* Left Brand Panel */
.auth-brand-panel::before {
  content: none !important; /* Remove the rectangular raster background */
}

/* Let the panel retain the gradient */
.auth-brand-panel {
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-items: center !important;
  text-align: center !important;
  padding: 4rem 2rem !important;
}

.auth-brand-art-box {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  margin-bottom: 32px !important;
}

.auth-hero-art-img {
  width: 100% !important;
  max-width: 260px !important;
  max-height: 240px !important;
  object-fit: contain !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* Typography Hierarchy */
.auth-brand-text {
  color: rgba(255, 255, 255, 0.9) !important;
  max-width: 480px !important;
  margin: 0 auto !important;
}

.auth-brand-text h1 {
  font-family: var(--font-display) !important;
  font-size: 36px !important;
  font-weight: 800 !important;
  margin-bottom: 8px !important;
  color: #ffffff !important;
  letter-spacing: -0.02em !important;
}

.auth-brand-text h2 {
  font-family: var(--font-display) !important;
  font-size: 20px !important;
  font-weight: 600 !important;
  margin-bottom: 16px !important;
  color: rgba(255, 255, 255, 0.95) !important;
}

.auth-brand-text p {
  font-size: 15px !important;
  line-height: 1.6 !important;
  color: rgba(255, 255, 255, 0.8) !important;
}


/* Right Login Card */
.login-card {
  max-width: 420px !important;
}

.brand-logo-mobile {
  height: 64px !important;
  width: auto !important;
}

.login-heading h2 {
  font-size: 28px !important;
}

.login-heading p {
  font-size: 15px !important;
}

.login-card .premium-input {
  height: 48px !important;
}

.login-card .btn-primary {
  height: 48px !important;
  background: var(--color-brand-cobalt) !important;
  color: #fff !important;
}

/* Error Message Soft-Red Alert */
.login-card .error-alert {
  background: #FEF2F2 !important;
  border: 1px solid #F87171 !important;
  border-radius: 8px !important;
  padding: 12px 16px !important;
  color: #991B1B !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  margin-bottom: 24px !important;
  font-size: 14.5px !important;
  font-weight: 500 !important;
}

.login-card .error-alert svg {
  color: #EF4444 !important;
  flex: 0 0 auto !important;
}

/* Remove yellow autofill */
.login-card input:-webkit-autofill,
.login-card input:-webkit-autofill:hover,
.login-card input:-webkit-autofill:focus,
.login-card input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 30px white inset !important;
  -webkit-text-fill-color: var(--color-ink) !important;
}

/* Responsive Login */
@media (max-width: 768px) {
  .auth-brand-panel {
    display: none !important;
  }
  .login-card {
    max-width: 100% !important;
    padding: 24px !important;
  }
  .login-card .btn-primary {
    width: 100% !important;
  }
}
"""

with open("C:/IEMS/static/css/workspace.css", "a", encoding="utf-8") as f:
    f.write(css)

update_user = """from django.contrib.auth import get_user_model
U = get_user_model()
u, _ = U.objects.get_or_create(username="acceptance_admin")
u.set_password("K-ONE-admin-2026!")
u.is_active = True
if hasattr(u, "is_staff"):
    u.is_staff = True
if hasattr(u, "is_superuser"):
    u.is_superuser = True
u.save()
print("User updated!")
"""
with open("C:/IEMS/scripts/update_user.py", "w", encoding="utf-8") as f:
    f.write(update_user)
