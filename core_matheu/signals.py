from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .constants import ROLE_GROUPS


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    for group_name in ROLE_GROUPS:
        Group.objects.get_or_create(name=group_name)
