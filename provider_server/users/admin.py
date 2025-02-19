from django.contrib import admin
from .models import ServiceCategory, CustomUser, Attachment

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_code', 'name']  # 'code'를 'category_code'로 변경
    list_display_links = ['category_code', 'name']  # 'code'를 'category_code'로 변경
    search_fields = ['category_code', 'name']  # 'code'를 'category_code'로 변경
    ordering = ['category_code']  # 'code'를 'category_code'로 변경

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'company_name', 'is_approved']
    list_filter = ['is_approved']
    search_fields = ['username', 'email', 'company_name']

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['user__username']