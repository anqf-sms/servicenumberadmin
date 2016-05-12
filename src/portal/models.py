from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator

from django.db.models.signals import *
from django.dispatch.dispatcher import receiver

from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

# pybeanstalk imports
import beanstalkc
import simplejson
from django.utils import timezone


class ServiceNumber(models.Model):
    securidial  = models.CharField(max_length=32, verbose_name="Service Number", validators=[RegexValidator(r'^13\d{8}$','Enter a valid service number','invalid')])
    remote_r = models.CharField(max_length=32, verbose_name="Remote R", blank=True)
    remote_l = models.CharField(max_length=32, verbose_name="Remote L", blank=True)
    def did_number(self):
        did_records = self.did_records.filter(begin_date_time__lte=timezone.now()).order_by('-pk')
        return did_records.first().did_number
    def __unicode__(self):
          return '{} -> {}'.format(self.securidial, self.did_number())

class DidRecord(models.Model):
    service = models.ForeignKey(ServiceNumber, related_name="did_records", on_delete=models.CASCADE,)
    did_number = models.CharField(max_length=32, verbose_name="DID Number", validators=[RegexValidator(r'^04\d{8}$','Enter a valid backend number','invalid')])
    begin_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, related_name="did_records", )
    created = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
          return '{}'.format(self.did_number)

class ServiceSetting(models.Model):
    service = models.ForeignKey(ServiceNumber, related_name="settings", on_delete=models.CASCADE,)
    port_type = models.CharField(max_length=16, verbose_name="Port Type", choices=(('tcp', 'tcp'), ('serial', 'serial'),))
    port = models.CharField(max_length=8, verbose_name="Port")
    remote_as_ip = models.GenericIPAddressField(verbose_name="AS IP")
    remote_receiver_ip = models.GenericIPAddressField(verbose_name="Receiver IP")
    json_setting = models.CharField(max_length=256, verbose_name="Json Setting", blank = True)
    description = models.CharField(max_length=128, verbose_name="Description", blank=True)



def publish_data(service):
    if True:
        did_records = service.did_records.all().order_by('-begin_date_time')
        data = {
            'table': 'cmssetting',
            'id': service.securidial,
            "remote_r": service.remote_r,
            "remote_l": service.remote_l,
            'did_records':[
                {
                    'did_number': r.did_number,
                    'begin_date_time': str(r.begin_date_time), #timezone.localtime()
                    'end_date_time': None if r.end_date_time is None else str(r.end_date_time),
                    'created_by': r.created_by.username,
                    'created': str(r.created.replace(microsecond=0)),
                } for r in did_records
            ],
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
        print '#'*20, simplejson.dumps(data)
        beanstalk = beanstalkc.Connection(host='127.0.0.1', port=11300)
        beanstalk.use('cms.setting.update')
        beanstalk.using(), beanstalk.tubes()
        beanstalk.put(simplejson.dumps(data))
    # except:
    #     pass


from threading import Thread
import time
def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = False
        t.start()
    return decorator

@postpone
def refine_end_date_time(service):
    time.sleep(0.5)

    did_records = service.did_records.all().order_by('-begin_date_time')

    for idx in range(len(did_records)):
        did_record = did_records[idx]
        # print '@'*10, did_record.begin_date_time, did_record.end_date_time
        if idx == 0:
            did_record.end_date_time = None
        else:
            # print 'bang!'
            did_record.end_date_time = did_records[idx-1].begin_date_time
        # print '@'*10, did_record.begin_date_time, did_record.end_date_time
        did_record.save()

    publish_data(service)


@receiver(post_save, sender=ServiceNumber)
def ServiceNumber_post_save_works(sender, instance, **kwargs):
    print '========ServiceNumber saved'
    refine_end_date_time(instance)


@receiver(pre_save, sender=ServiceSetting)
def ServiceSetting_pre_save_works(sender, instance, **kwargs):
    #print '@'*20, instance
    instance.port = instance.port.lower()
    #print '@'*20, instance

@receiver(post_save, sender=ServiceSetting)
def ServiceSetting_post_save_works(sender, instance, **kwargs):
    print '======== ServiceSetting saved'
    publish_data(instance.service)



