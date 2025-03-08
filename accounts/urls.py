from django.urls import path
from . import views

app_name = 'accounts'  # Make sure this is here

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verify/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update-password/', views.update_password, name='update_password'),
]