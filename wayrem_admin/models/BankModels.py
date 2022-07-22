from django.db import models


class Banks(models.Model):
    title = models.CharField(max_length=255)
    bank_key = models.CharField(max_length=255, null=True)
    bank_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    account_no = models.CharField(max_length=255, null=True)
    swift_code = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255)
    iban = models.CharField(max_length=255)
    status = models.IntegerField()
    is_deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'banks'
