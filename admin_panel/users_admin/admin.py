from django.contrib import admin
from .models import Users, Downloads, Logger

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'name', 'status', 'sent_links', 'download_limit', 'created_at')
    search_fields = ('user_id', 'user_name', 'name')
    list_filter = ('status',)

@admin.register(Downloads)
class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'downloaded_at', 'url_orig')
    list_filter = ('user_id',)
    search_fields = ('user_id',)

@admin.register(Logger)
class LoggerAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'user_id', 'user_name', 'type', 'action')
    search_fields = ('user_id', 'user_name', 'type', 'action')
    list_filter = ('user_id',)
