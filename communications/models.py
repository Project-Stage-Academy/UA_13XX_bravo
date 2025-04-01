from django.db import models


class ChatRoom(models.Model):  # Create your models here.
    id = models.AutoField(primary_key=True)
    company_id_1 = models.ForeignKey(
        "companies.CompanyProfile",
        on_delete=models.CASCADE,
        related_name="company1",
        null=True,
    )
    company_id_2 = models.ForeignKey(
        "companies.CompanyProfile",
        on_delete=models.CASCADE,
        related_name="company2",
        null=True,
    )
    mongo_room_id = models.CharField(max_length=255, unique=True, help_text="MongoDB Room ObjectId or key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("company_id_1", "company_id_2")

    def save(self, *args, **kwargs):
        """Ensure (A, B) and (B, A) are treated as the same room."""
        if self.company_id_1 and self.company_id_2:
            if self.company_id_1.id > self.company_id_2.id:
                self.company_id_1, self.company_id_2 = self.company_id_2, self.company_id_1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company_id_1} - {self.company_id_2}"
