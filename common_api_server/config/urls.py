from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('admin/', admin.site.urls),
    path('estimates/', include("estimates.urls")),
    path('services/', include("services.urls")),
    # path('api/', include('api.urls')),
    # path('auth/', include('authentication.urls')),  # authentications -> authentication
]
