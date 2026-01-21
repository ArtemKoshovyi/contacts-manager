from django.contrib import admin
# ИСПРАВЛЕНО: убрана 's' в конце
from .models import Contact, ContactStatusChoice

@admin.register(ContactStatusChoice)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "status", "created_at")