"""
Management command: backfill_profiles

Creates a UserProfile for every User that doesn't already have one.

Usage:
    python3 manage.py backfill_profiles
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create missing UserProfile records for all existing users.'

    def handle(self, *args, **options):
        created_count = 0
        for user in User.objects.all():
            _, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(f'  Created profile for: {user.username}')

        if created_count:
            self.stdout.write(
                self.style.SUCCESS(f'Done – created {created_count} profile(s).')
            )
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles.'))
