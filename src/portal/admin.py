from django.contrib import admin
from django import forms

from django.core.exceptions import ValidationError

from portal.models import *
from django.utils import timezone


class ServiceSettingInlineAdmin(admin.TabularInline):
    model = ServiceSetting
    max_num = 2
    extra = 2


class DidAdminInline(admin.TabularInline):
    verbose_name = 'History DID'
    verbose_name_plural = 'History DID'
    model = DidRecord
    readonly_fields = ('did_number', 'begin_date_time', 'end_date_time', 'created_by', 'created', )
    extra = 0
    can_delete = False
    empty_value_display = '- not set -'
    def has_add_permission(self, request):
        return False
    def get_queryset(self, request):
        qs = super(DidAdminInline, self).get_queryset(request)
        return qs.filter(begin_date_time__lte=timezone.now()).order_by('-begin_date_time')

# class DidAdminInlineFormSet(forms.BaseInlineFormSet):
#     def clean(self):
#         print '#'*10, 'clean called'
#         super(DidAdminInlineFormSet, self).clean()
#         for form in self.forms:
#             if not hasattr(form, 'cleaned_data'):
#                 continue
#             print '@'*10, form
#             data = self.cleaned_data
#             for r in data:
#                 print '>>>', r
#                 if r != {}:
#                     if r['begin_date_time']<timezone.now():
#                         raise forms.ValidationError([{'begin_date_time': 'Past time is not allowed.'}])


#             #Always return the cleaned data, whether you have changed it or not.
#             #return data

class DidAddForm(forms.ModelForm):
    timeline = forms.DateTimeField(initial=timezone.now, label='timeline', widget = forms.HiddenInput())
    class Meta:
        model = DidRecord
        fields = ('did_number', 'begin_date_time')

    def has_changed(self, *args, **kwargs):
        # print '@'*100
        org_changed = super(DidAddForm, self).has_changed(*args, **kwargs)
        if len(self.changed_data)==1 and self.changed_data[0]=='timeline':
            changed = False
        else:
            changed = org_changed
        # print '@'*100, org_changed, changed, self.changed_data
        return changed

    def clean(self):
        # print '$'*100
        # print 'pk=', repr(self.instance.pk), 'did_number=', repr(self.instance.did_number), 'begin_date_time=', repr(self.instance.begin_date_time)
        cleaned_data = super(DidAddForm, self).clean()
        begin_date_time = cleaned_data.get('begin_date_time')
        timeline = cleaned_data.get('timeline')
        if begin_date_time is not None and begin_date_time<timeline:
            raise forms.ValidationError({'begin_date_time': ['Past time not allowed.',]})
        # del cleaned_data['timeline']
        return cleaned_data


class AddDidAdminInline(admin.TabularInline):
    verbose_name = 'New DID'
    verbose_name_plural = 'New DID'
    model = DidRecord
    form = DidAddForm
    extra = 1
    max_num = 1
    def get_queryset(self, request):
        qs = super(AddDidAdminInline, self).get_queryset(request)
        return qs.filter(begin_date_time__gte=timezone.now())

class ServiceNumberAdmin(admin.ModelAdmin):
    model = ServiceNumber
    list_display = ('securidial', 'did_number', 'remote_r', 'remote_l', )
    inlines = (ServiceSettingInlineAdmin, AddDidAdminInline, DidAdminInline, )
    save_on_top = True

    def __init__(self, *args, **kwargs):
        super(ServiceNumberAdmin, self).__init__(*args, **kwargs)

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            for f in formset:
                if hasattr(f.instance, 'created_by_id') and f.instance.created_by_id is None:
                    f.instance.created_by_id = request.user.pk
            self.save_formset(request, form, formset, change=change)

class ServiceSettingAdmin(admin.ModelAdmin):
    class Meta:
        model = ServiceSetting
    list_display = ('id', 'service', 'port_type', 'port', 'remote_as_ip', 'remote_receiver_ip', 'json_setting', 'description')
    list_display_links = ('id',)


# Register your models here.

admin.site.register(ServiceNumber, ServiceNumberAdmin)
#admin.site.register(ServiceSetting, ServiceSettingAdmin)
