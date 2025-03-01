from django.contrib import admin

# Register your models here.
from .models import (
    ServiceCategory,
)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_code', 'name')
    search_fields = ('name', 'category_code')
