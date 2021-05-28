from django.db import models

class File(models.Model):
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='documents')
    uploaded_at=models.DateTimeField(auto_now_add=True)