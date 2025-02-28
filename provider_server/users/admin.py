from django.contrib import admin
from .models import  Attachment, ProviderUser


@admin.register(ProviderUser)
class ProviderUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'company_name', 'is_approved']
    list_filter = ['is_approved']
    search_fields = ['username', 'email', 'company_name']

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_type', 'file', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['user__username']