from django.db import models
from django.core.validators import RegexValidator

PHONE_REGEX = RegexValidator(
    regex=r'^\d{10,11}$', message="Invalid phone number")


class PhoneCall(models.Model):
    call_id = models.PositiveIntegerField(unique=True)
    source = models.CharField(validators=[PHONE_REGEX], max_length=11)
    destination = models.CharField(validators=[PHONE_REGEX], max_length=11)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)


class PhoneCallRecord(models.Model):
    RECORD_TYPES = (
        ('start', 'Start'),
        ('end', 'End'),
    )
    call = models.ForeignKey(PhoneCall, on_delete=models.PROTECT)
    type = models.CharField(max_length=5, choices=RECORD_TYPES)
    timestamp = models.DateTimeField()
