import simplejson

from django.shortcuts import render
from django.http import HttpResponse

from portal.models import *


def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = simplejson.dumps(objects)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                response =  HttpResponse(data, "text/javascript")
                response["Access-Control-Allow-Origin"] = "*"
                return response
        except:
            data = simplejson.dumps(str(objects))
        response = HttpResponse(data, "application/json")
        response["Access-Control-Allow-Origin"] = "*"
        return response
    return decorator



@json_response
def get_service_settings(request):
    settings = ServiceSetting.objects.all().order_by('-pk')
    rslt = [{'id': s.pk,
             'service': s.service,
             'port_type': s.port_type,
             'port': s.port,
             'as_ip': s.as_ip,
             'receiver_ip': s.receiver_ip,
             'json_setting': s.json_setting,
             'description': s.description,
            }
            for s in settings]
    return rslt

