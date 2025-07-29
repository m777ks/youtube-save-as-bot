from django.db import models

class Users(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')
    sent_links = models.IntegerField(default=0)
    download_limit = models.IntegerField(default=3)

    class Meta:
        db_table = 'users'  # указываем существующую таблицу
        managed = False     # не даём Django управлять миграциями

class Downloads(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    downloaded_at = models.DateTimeField(auto_now_add=True)
    url_orig = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'downloads'
        managed = False

class Logger(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'logger'
        managed = False
