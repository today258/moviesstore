from django.db import models
from django.contrib.auth.models import User
import pycountry

COUNTRY_CHOICES = sorted(
    [(c.alpha_2, c.name) for c in pycountry.countries],
    key=lambda x: x[1],
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nationality = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.user.username} – {self.get_nationality_display() or "No nationality"}'
