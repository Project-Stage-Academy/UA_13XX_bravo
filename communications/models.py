from django.db import models


class ChatRoom(models.Model):  # Create your models here.
    id = models.AutoField(primary_key=True)
    company_id_1 = models.ForeignKey(
        "companies.CompanyProfile",
        on_delete=models.SET_NULL,
        related_name="company1",
        null=True,
    )
    company_id_2 = models.ForeignKey(
        "companies.CompanyProfile",
        on_delete=models.SET_NULL,
        related_name="company2",
        null=True,
    )
    mongo_room_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("company_id_1", "company_id_2")

    def __str__(self):
        return f"{self.company_id_1} - {self.company_id_2}"
