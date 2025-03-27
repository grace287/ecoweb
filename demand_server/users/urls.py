

import users.views as users_views
from django.urls import path


urlpatterns = [
    path("signup/", users_views.SignupView.as_view(), name="signup"),
    path("login/", users_views.LoginView.as_view(), name="login"),
    path("logout/", users_views.LogoutView.as_view(), name="logout"),
    path("signup/success/", users_views.SignupSuccessView.as_view(), name="signup_success"),
    path("check-username-duplicate/", users_views.CheckUsernameDuplicateView.as_view(), name="check_username_duplicate"),
    path("check-email-duplicate/", users_views.CheckEmailDuplicateView.as_view()),
    path("profile/", users_views.ProfileView.as_view()),
    path("profile/edit/", users_views.ProfileView.as_view()),
    path("profile/change-password/", users_views.PasswordChangeView.as_view()),
    path("profile/customization/update/", users_views.CustomizationUpdateView.as_view(), name="customization_update"),

    
]
