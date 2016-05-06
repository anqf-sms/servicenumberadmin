from django.contrib import admin

from portal.models import *


class ServiceNumberAdmin(admin.ModelAdmin):
    # class Meta:
    #     model = ServiceNumber
    list_display = ('service_number', 'backend_number', 'remote_r', 'remote_l', )

class ServiceSettingAdmin(admin.ModelAdmin):
    class Meta:
        model = ServiceSetting
    list_display = ('id', 'service', 'port_type', 'port', 'as_ip', 'receiver_ip', 'json_setting', 'description')
    list_display_links = ('id',)


# Register your models here.

admin.site.register(ServiceNumber, ServiceNumberAdmin)
admin.site.register(ServiceSetting, ServiceSettingAdmin)
