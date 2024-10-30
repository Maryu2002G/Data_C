from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Asignature

@receiver(post_save, sender=Asignature)
def create_group_for_asignature(sender, instance, created, **kwargs):
    if created:  # Solo ejecuta esto si la asignatura fue creada
        group_name = instance.nameAs  # Usa el nombre de la asignatura como nombre del grupo
        Group.objects.get_or_create(name=group_name)
