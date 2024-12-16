from django.db import models

class Recipe(models.Model):
    class RecipeStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    title = models.CharField(max_length=255, blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    steps = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=16,
        choices=RecipeStatus.choices,
        default=RecipeStatus.PENDING
    )
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else f"Le Recipe {self.id}"