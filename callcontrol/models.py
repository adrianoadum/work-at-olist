from django.db import models
from django.core.validators import RegexValidator

PHONE_REGEX = RegexValidator(
    regex=r'^\d{10,11}$', message="Invalid phone number")


class PhoneCall(models.Model):
    call_id = models.PositiveIntegerField(unique=True)
    source = models.CharField(validators=[PHONE_REGEX], max_length=11)
    destination = models.CharField(validators=[PHONE_REGEX], max_length=11)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    @property
    def start(self):
        record = self.phonecallrecord_set.filter(type='start').last()
        if record:
            return record.timestamp
        return None

    @property
    def end(self):
        record = self.phonecallrecord_set.filter(type='stop').last()
        if record:
            return record.timestamp
        return None

    @property
    def duration(self):
        if self.start and self.end:
            return self.end - self.start
        return None


class PhoneCallRecord(models.Model):
    RECORD_TYPES = (
        ('start', 'Start'),
        ('stop', 'Stop'),
    )
    call = models.ForeignKey(PhoneCall, on_delete=models.PROTECT)
    type = models.CharField(max_length=5, choices=RECORD_TYPES)
    timestamp = models.DateTimeField()
