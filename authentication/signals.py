from django.dispatch import receiver
from django.utils.timezone import now
from .models import Authentication
from django.dispatch import Signal

# Custom signal for user login
custom_user_logged_in = Signal()

@receiver(custom_user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    auth_instance, created = Authentication.objects.get_or_create(user=user)
    auth_instance.last_login_time = now()
    auth_instance.failed_attempts = 0  # Reset failed attempts
    auth_instance.is_locked = False  # Unlock if previously locked
    auth_instance.locked_at = None  # Reset lock time
    auth_instance.save()
