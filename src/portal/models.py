from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class ServiceNumber(models.Model):
    service_number  = models.CharField(max_length=32, verbose_name="Service Number", validators=[RegexValidator(r'^13\d{8}$','Enter a valid service number','invalid')])
    backend_number = models.CharField(max_length=32, verbose_name="Backend Number", validators=[RegexValidator(r'^04\d{8}$','Enter a valid backend number','invalid')])
    remote_r = models.CharField(max_length=32, verbose_name="Remote R", blank=True)
    remote_l = models.CharField(max_length=32, verbose_name="Remote L", blank=True)
    def __unicode__(self):
          return '{} -> {}'.format(self.service_number, self.backend_number)

class ServiceSetting(models.Model):
    service = models.ForeignKey(ServiceNumber, related_name="settings", on_delete=models.CASCADE,)
    port_type = models.CharField(max_length=3, verbose_name="Port Type", choices=(('TCP', 'TCP'), ('COM', 'COM'),))
    port = models.CharField(max_length=8, verbose_name="Port")
    as_ip = models.GenericIPAddressField(verbose_name="AS IP")
    receiver_ip = models.GenericIPAddressField(verbose_name="Receiver IP")
    json_setting = models.CharField(max_length=8, verbose_name="Json Setting", blank = True)
    description = models.CharField(max_length=128, verbose_name="Description", blank=True)

