from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce


def sum_planned(path="items__planned"):
    """Сумма плановых значений по связанным статьям; без статей – 0."""
    return Coalesce(
        Sum(path),
        Value(0),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
