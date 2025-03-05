from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.admin_login, name='login'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path("companies/pending/", views.pending_companies, name="pending_companies"),
    path('api/', include('api.urls')),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('approve-requests/', views.approve_provider_requests, name='approve_requests'),
    path('generate-fake-data/', views.generate_fake_data_view, name='generate_fake_data'),
]