from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField

REGIONS_BRAZIL = [
    ('NORTE', 'Norte'),
    ('NORDESTE', 'Nordeste'),
    ('CENTRO-OESTE', 'Centro-Oeste'),
    ('SUDESTE', 'Sudeste'),
    ('SUL', 'Sul'),
]


FORMAT_CHOICES = [
    ('presencial', 'Presencial'),
    ('remoto', 'Remoto'),
]

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(
        User, 
        related_name='projects_created',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    is_remote = models.BooleanField(default=False) 
    accepted_regions = ArrayField(
        models.CharField(max_length=20, choices=REGIONS_BRAZIL),
        default=list
    )
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='online'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    vacancies = models.PositiveIntegerField() 
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='projects_updated'
    )

    def __str__(self):
        return self.name