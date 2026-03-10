from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Auto-create a UserProfile whenever a User is saved (signup, createsuperuser, admin)."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
