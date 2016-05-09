from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator

from django.db.models.signals import *
from django.dispatch.dispatcher import receiver

# pybeanstalk imports
from beanstalk import serverconn
from beanstalk import job
import simplejson


# Create your models here.

class ServiceNumber(models.Model):
    securidial  = models.CharField(max_length=32, verbose_name="Service Number", validators=[RegexValidator(r'^13\d{8}$','Enter a valid service number','invalid')])
    caller_number = models.CharField(max_length=32, verbose_name="Backend Number", validators=[RegexValidator(r'^04\d{8}$','Enter a valid backend number','invalid')])
    remote_r = models.CharField(max_length=32, verbose_name="Remote R", blank=True)
    remote_l = models.CharField(max_length=32, verbose_name="Remote L", blank=True)
    def __unicode__(self):
          return '{} -> {}'.format(self.securidial, self.caller_number)

class ServiceSetting(models.Model):
    service = models.ForeignKey(ServiceNumber, related_name="settings", on_delete=models.CASCADE,)
    port_type = models.CharField(max_length=3, verbose_name="Port Type", choices=(('TCP', 'TCP'), ('COM', 'COM'),))
    port = models.CharField(max_length=8, verbose_name="Port")
    remote_as_ip = models.GenericIPAddressField(verbose_name="AS IP")
    remote_receiver_ip = models.GenericIPAddressField(verbose_name="Receiver IP")
    json_setting = models.CharField(max_length=256, verbose_name="Json Setting", blank = True)
    description = models.CharField(max_length=128, verbose_name="Description", blank=True)


connection = serverconn.ServerConn('127.0.0.1', 11300)
connection.job = job.Job

def publish_data(service):
    data = {
        'table': 'cmssetting',
        'id': service.pk,
        'callerid': {
            'securidial': service.securidial,
            'caller_number': service.caller_number,
            "remote_r": service.remote_r,
            "remote_l": service.remote_l,
        },
        'callerid_as_settings': [
            {
                'type': setting.port_type,
                'port': setting.port,
                'remote_as_ip': setting.remote_as_ip,
                'remote_receiver_ip': setting.remote_receiver_ip,
                'json_setting': setting.json_setting,
                'description': setting.description,
            } for setting in service.settings.all()
        ],
    }
    print '#'*20, data
    myjob = job.Job(data=simplejson.dumps(data), conn=connection)
    myjob.Queue()

@receiver(post_save, sender=ServiceNumber)
def ServiceNumber_post_save_works(sender, instance, **kwargs):
    publish_data(instance)

@receiver(post_save, sender=ServiceSetting)
def ServiceSetting_post_save_works(sender, instance, **kwargs):
    print '#'*20, instance
    service = instance.service
    publish_data(instance)

# {
#     "table": "cmssetting",
#     "id": 13451234,
#     "callerid": {
#         "securidial": 13451234,
#         "caller_number": "0312345678",
#         "remote_r": 0,
#         "remote_l": 1
#     },
#     "callerid_as_settings": [
#         {
#             "type": "tcp",
#             "port": 9307,
#             "remote_as_ip": "10.100.0.2",
#             "remote_receiver_ip": "192.168.10.100",
#             "cms_description": "test"
#         }
#     ]
# }

