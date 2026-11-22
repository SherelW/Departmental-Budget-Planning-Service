from django.db import models


class Department(models.Model):
    """Подразделение."""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название подразделения",
    )
    head = models.CharField(
        max_length=200,
        verbose_name="Руководитель",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
