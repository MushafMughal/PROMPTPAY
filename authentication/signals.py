from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth.signals import user_logged_in
from .models import Authentication

@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    auth_instance, created = Authentication.objects.get_or_create(user=user)
    auth_instance.last_login_time = now()
    auth_instance.failed_attempts = 0  # Reset failed attempts on successful login
    auth_instance.is_locked = False  # Unlock if previously locked
    auth_instance.save()
