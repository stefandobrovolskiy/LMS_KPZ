from django.urls import path
from . import views

app_name = 'users'  # Для namespacing URL-ів

urlpatterns = [
    # path('register/', views.register, name='register'),  # Реєстрацію вимкнено
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]