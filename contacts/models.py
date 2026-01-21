from django.db import models

class ContactStatusChoice(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"

class Contact(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    city = models.CharField(max_length=80)
    
    status = models.ForeignKey(
        ContactStatusChoice, 
        on_delete=models.PROTECT, 
        related_name="contacts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"