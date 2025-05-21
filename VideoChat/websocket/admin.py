
from django.contrib import admin
from .models import CallSession

# Register your models here.
@admin.register(CallSession)
class CallSessionAdmin(admin.ModelAdmin):
    list_display = ("caller", "receiver", "is_active", "started_at", "ended_at")
    list_filter = ("is_active", "started_at")
