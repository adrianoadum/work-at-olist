from django.core.validators import RegexValidator
from django.db import models

PHONE_REGEX = RegexValidator(
    regex=r'^\d{10,11}$', message="Invalid phone number")


class PhoneCall(models.Model):
    call_id = models.PositiveIntegerField(unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    @property
    def source(self):
        source = self.phonecallparticipant_set.filter(type='source').last()
        if source:
            return source.phone_number
        return None

    @property
    def destination(self):
        destination = self.phonecallparticipant_set.filter(
            type='destination').last()
        if destination:
            return destination.phone_number
        return None

    @property
    def start(self):
        record = self.phonecallrecord_set.filter(type='start').last()
        if record:
            return record.timestamp
        return None

    @property
    def end(self):
        record = self.phonecallrecord_set.filter(type='end').last()
        if record:
            return record.timestamp
        return None

    @property
    def duration(self):
        if self.start and self.end:
            return self.end - self.start
        return None


class PhoneCallParticipant(models.Model):
    PARTICIPANT_TYPES = (
        ('source', 'Source'),
        ('destination', 'Destination'),
    )
    call = models.ForeignKey(PhoneCall, on_delete=models.PROTECT)
    type = models.CharField(max_length=11, choices=PARTICIPANT_TYPES)
    phone_number = models.CharField(
        validators=[PHONE_REGEX], max_length=11, null=True)


class PhoneCallRecord(models.Model):
    RECORD_TYPES = (
        ('start', 'Start'),
        ('end', 'End'),
    )
    call = models.ForeignKey(PhoneCall, on_delete=models.PROTECT)
    type = models.CharField(max_length=5, choices=RECORD_TYPES)
    timestamp = models.DateTimeField()


class Pricing(models.Model):
    name = models.CharField(max_length=255)
    period_start = models.TimeField()
    period_end = models.TimeField()
    standing_price = models.DecimalField(max_digits=5, decimal_places=2)
    price_per_minute = models.DecimalField(max_digits=5, decimal_places=2)
