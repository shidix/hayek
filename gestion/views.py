from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q
from django.db.models import CharField
from django.contrib.postgres.lookups import Unaccent
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from zoneinfo import ZoneInfo
from datetime import datetime
import calendar
import os, csv

from hayek.decorators import group_required
from hayek.commons import get_float, get_int, get_or_none, get_param, get_session, set_session, show_exc, generate_qr, csv_export
from .models import Employee, Client, Service, ServiceType, Infestation, Incident

CharField.register_lookup(Unaccent)
ACCESS_PATH="{}/gestion/assistances/client/".format(settings.MAIN_URL)


def init_session_date(request, key):
    #if not key in request.session:
    set_session(request, key, datetime.now().strftime("%Y-%m-%d"))

def get_local_date(date, time):
    d = datetime.strptime("{} {}".format(date, time), "%Y-%m-%d %H:%M")
    d = d.replace(tzinfo=ZoneInfo("Atlantic/Canary"))
    d = d.astimezone(ZoneInfo("UTC"))
    return d 


'''
    SERVICES
'''
def get_services(request, deleted=False):
    value = get_session(request, "s_name")
    s_type = get_session(request, "s_type")
    status = get_session(request, "s_status")
    charged = get_session(request, "s_charged")
    value = get_session(request, "s_name")
    i_date = datetime.strptime("{} 00:00".format(get_session(request, "s_idate")), "%Y-%m-%d %H:%M")
    e_date = datetime.strptime("{} 23:59".format(get_session(request, "s_edate")), "%Y-%m-%d %H:%M")

    kwargs = {"ini_date__gte": i_date, "ini_date__lte": e_date, 'deleted': deleted}
    if value != "":
        kwargs["employee__name__icontains"] = value
    if s_type != "":
        kwargs["service_type__id"] = s_type
    if status != "":
        kwargs["status__id"] = status
    if charged == "0":
        kwargs["charged"] = False
    if charged == "1":
        kwargs["charged"] = True

    print(kwargs)
    return Service.objects.filter(**kwargs).order_by("-ini_date")

@group_required("admins",)
def index(request):
    init_session_date(request, "s_idate")
    init_session_date(request, "s_edate")
    context = {
        "item_list": get_services(request), 
        #"notes": get_notes(request), 
        "type_list": ServiceType.objects.all(), 
        "infestation_list": Infestation.objects.all()
    }
    return render(request, "index.html", context)

@group_required("admins",)
def services_list(request):
    deleted = True if get_param(request.GET, "deleted") == "True" else False
    return render(request, "services-list.html", {"item_list": get_services(request, deleted)})

@group_required("admins",)
def services_search(request):
    set_session(request, "s_name", get_param(request.GET, "s_name"))
    set_session(request, "s_idate", get_param(request.GET, "s_idate"))
    set_session(request, "s_edate", get_param(request.GET, "s_edate"))
    set_session(request, "s_type", get_param(request.GET, "s_type"))
    set_session(request, "s_status", get_param(request.GET, "s_status"))
    set_session(request, "s_charged", get_param(request.GET, "s_charged"))
    return render(request, "services-list.html", {"item_list": get_services(request)})

@group_required("admins",)
def services_form(request):
    obj = get_or_none(Service, get_param(request.GET, "obj_id"))
    type_list = ServiceType.objects.all()
    inf_list = Infestation.objects.all()
    client_list = Client.objects.all()
    employee_list = Employee.objects.all()
    print(employee_list)
    context = {'obj':obj, 'type_list':type_list, 'infestation_list':inf_list, 'client_list':client_list, 'emp_list':employee_list}
    return render(request, "services-form.html", context)

@group_required("admins",)
def services_form_save(request):
    obj = get_or_none(Service, get_param(request.GET, "obj_id"))
    if obj == None:
        obj = Service.objects.create()
    #s_type = get_or_none(ServiceType, get_param(request.GET, "service_type"))
    #status = get_or_none(ServiceStatus, get_param(request.GET, "status"))
    client = get_or_none(Client, get_param(request.GET, "client"))
    emp = get_or_none(Employee, get_param(request.GET, "employee"))
    charged = get_param(request.GET, "charged")
    ini_date = get_param(request.GET, "ini_date")
    end_date = get_param(request.GET, "end_date")
    ini_time = get_param(request.GET, "ini_time")
    end_time = get_param(request.GET, "end_time")

    #obj.service_type = s_type
    #obj.status = status
    obj.ini_date = get_local_date(ini_date, ini_time)
    obj.end_date = get_local_date(end_date, end_time)
    obj.client = client
    obj.employee = emp
    obj.save()
    return render(request, "services-list.html", {"item_list": get_services(request)})

@group_required("admins",)
def services_remove(request):
    obj = get_or_none(Service, request.GET["obj_id"])
    if obj != None:
        obj.delete()
    return render(request, "services-list.html", {"item_list": get_services(request)})

@group_required("admins",)
def services_remove_soft(request):
    obj = get_or_none(Service, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.deleted = True
        obj.save()
    return render(request, "services-list.html", {"item_list": get_services(request)})

'''
    EMPLOYEES
'''
def get_employees(request):
    search_value = get_session(request, "s_emp_name")
    search_comp = get_session(request, "s_emp_comp")
    kwargs = {}
    if search_value != "" or search_comp != "":
        if search_value != "":
            kwargs["name__unaccent__icontains"] = search_value
        if search_comp != "":
            kwargs["timetables__client__name__unaccent__icontains"] = search_comp
        return Employee.objects.filter(**kwargs)
    return Employee.objects.all()

@group_required("Administradores",)
def employees(request):
    init_session_date(request, "s_emp_idate")
    init_session_date(request, "s_emp_edate")
    return render(request, "employees/employees.html", {"items": get_employees(request)})

@group_required("Administradores",)
def employees_list(request):
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("Administradores",)
def employees_search(request):
    set_session(request, "s_emp_name", get_param(request.GET, "s_emp_name"))
    set_session(request, "s_emp_comp", get_param(request.GET, "s_emp_comp"))
    set_session(request, "s_emp_idate", get_param(request.GET, "s_emp_idate"))
    set_session(request, "s_emp_edate", get_param(request.GET, "s_emp_edate"))
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("Administradores",)
def employees_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Employee, obj_id)
    if obj == None:
        obj = Employee.objects.create()
    return render(request, "employees/employees-form.html", {'obj': obj, 'client_list': Client.objects.all()})

@group_required("Administradores",)
def employees_remove(request):
    obj = get_or_none(Employee, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        if obj.user != None:
            obj.user.delete()
        obj.delete()
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("Administradores",)
def employees_save_email(request):
    try:
        obj = get_or_none(Employee, get_param(request.GET, "obj_id"))
        obj.email = get_param(request.GET, "value")
        obj.save()
        obj.save_user()
        return HttpResponse("Saved!")
    except Exception as e:
        return HttpResponse("Error: {}".format(e))

'''
    CLIENTS
'''
def get_clients(request):
    search_value = get_session(request, "s_cli_name")
    filters_to_search = ["name__unaccent__icontains",]
    full_query = Q()
    if search_value != "":
        for myfilter in filters_to_search:
            full_query |= Q(**{myfilter: search_value})
    return Client.objects.filter(full_query).order_by("-id")[:50]

@group_required("Administradores",)
def clients(request):
    return render(request, "clients/clients.html", {"items": get_clients(request)})

@group_required("Administradores",)
def clients_list(request):
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("Administradores",)
def clients_search(request):
    set_session(request, "s_cli_name", get_param(request.GET, "s_cli_name"))
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("Administradores",)
def clients_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Client, obj_id)
    new = False
    if obj == None:
        obj = Client.objects.create()
        url = "{}{}".format(ACCESS_PATH, obj.id)
        path = os.path.join(settings.BASE_DIR, "static", "images", "logo-asistencia-canaria.jpg")
        img_data = ContentFile(generate_qr(url, path))
        obj.qr.save('qr_{}.png'.format(obj.id), img_data, save=True)
        new = True
    return render(request, "clients/clients-form.html", {'obj': obj, 'new': new, 'emp_list': Employee.objects.all()})

@group_required("Administradores",)
def clients_remove(request):
    obj = get_or_none(Client, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.qr.delete(save=True)
        obj.delete()
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("Administradores",)
def clients_assistances(request, obj_id):
    return render(request, "clients/clients-assistances.html", {"obj": get_or_none(Client, obj_id)})

'''
    EMPLOYEES
'''
@group_required("Administradores",)
def employee(request, obj_id):
    idate = datetime.today().replace(day=1)
    last_day = calendar.monthrange(idate.year, idate.month)[1]
    edate = idate.replace(day=last_day)
    set_session(request, "s_employee_idate", idate.strftime("%Y-%m-%d"))
    set_session(request, "s_employee_edate", edate.strftime("%Y-%m-%d"))
    emp = get_or_none(Employee, obj_id)
    return render(request, "employee/clients.html", {"obj": emp})

@group_required("Administradores",)
def employee_search(request):
    obj_id = get_param(request.GET, "obj_id")
    set_session(request, "s_employee_idate", get_param(request.GET, "s_employee_idate"))
    set_session(request, "s_employee_edate", get_param(request.GET, "s_employee_edate"))
    return redirect(reverse('employee', kwargs={'obj_id': obj_id}))

@group_required("Administradores",)
def employee_search_client(request):
    try:
        value = get_param(request.GET, "value")
        obj = get_or_none(Employee, get_param(request.GET, "obj_id"))
        items = []
        if value != "":
            items = Client.objects.filter(name__unaccent__icontains=value)
        return render(request, "employee/client-search-list.html", {'items': items, 'obj': obj, 'value':value})
    except Exception as e:
        return render(request, "error_exception.html", {'exc':show_exc(e)})

@group_required("Administradores",)
def employee_form_timetable(request):
    obj = get_or_none(Employee, get_param(request.GET, "obj_id"))
    if obj != None:
        client = get_or_none(Client, get_param(request.GET, "client_id"))
        days = request.GET.getlist("day")
        ini = get_param(request.GET, "ini")
        end = get_param(request.GET, "end")
        for day in days:
            ClientTimetable.objects.create(client=client, employee=obj, day=day, ini=ini, end=end)
    return redirect(reverse('employee', kwargs={'obj_id': obj.id}))
    #return render(request, "employees/employees-form-timetable.html", {'obj': obj, 'client_list': Client.objects.all()})

@group_required("Administradores",)
def employee_form_timetable_remove(request, obj_id):
    obj = get_or_none(ClientTimetable, obj_id)
    emp = None
    if obj != None:
        emp = obj.employee
        obj.delete()
    return redirect(reverse('employee', kwargs={'obj_id': emp.id}))


'''
    INCIDENTS
'''
def get_incidents(request):
    i_date = datetime.strptime("{} 00:00".format(get_session(request, "s_inc_idate")), "%Y-%m-%d %H:%M")
    e_date = datetime.strptime("{} 23:59".format(get_session(request, "s_inc_edate")), "%Y-%m-%d %H:%M")
    status = get_session(request, "s_inc_status")
    emp = get_session(request, "s_inc_emp")

    kwargs = {"creation_date__range": (i_date, e_date),}
    if status != "": 
        kwargs['closed'] = True if status == "True" else False
    if emp != "": 
        user_list = [item.user for item in Employee.objects.filter(name__unaccent__icontains=emp)]
        kwargs['owner__in'] = user_list
    return Incident.objects.filter(**kwargs)

@group_required("Administradores",)
def incidents(request):
    init_session_date(request, "s_inc_idate")
    init_session_date(request, "s_inc_edate")
    set_session(request, "s_inc_status", "False")
    return render(request, "incidents/incidents.html", {"items": get_incidents(request)})

@group_required("Administradores",)
def incidents_list(request):
    item_list = get_incidents(request)
    return render(request, "incidents/incidents-list.html", {"items": item_list})

@group_required("Administradores",)
def incidents_search(request):
    set_session(request, "s_inc_idate", get_param(request.GET, "s_inc_idate"))
    set_session(request, "s_inc_edate", get_param(request.GET, "s_inc_edate"))
    set_session(request, "s_inc_status", get_param(request.GET, "s_inc_status"))
    set_session(request, "s_inc_emp", get_param(request.GET, "s_inc_emp"))
    item_list = get_incidents(request)
    return render(request, "incidents/incidents-list.html", {"items": item_list,})

@group_required("Administradores",)
def incidents_form(request):
    obj = get_or_none(Incident, get_param(request.GET, "obj_id"))
    if obj == None:
        return render(request, "error_exception.html", {'exc': 'Object not found!'})
    return render(request, "incidents/incidents-form.html", {'obj': obj,})


