from django.shortcuts import render, redirect
from django.db.models import CharField
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.postgres.lookups import Unaccent
from django.core.files.base import ContentFile
from datetime import datetime

import base64
import uuid
import subprocess
import threading

from hayek.decorators import group_required_pwa
from hayek.commons import user_in_group, get_or_none, get_param, show_exc, get_local_date
from gestion.models import Employee, Client, Service, Infestation, ServiceType, Incident, Biocide, BiocideType, BiocideWarning
from gestion.models import ServiceBiocide, ServiceBiocideType, ServiceBiocideWarning

CharField.register_lookup(Unaccent)


@group_required_pwa("employees")
def index(request):
    try:
        return redirect(reverse('pwa-employee'))
    except:
        return redirect(reverse('pwa-login'))

def pin_login(request):
    CONTROL_KEY = "SZRf2QMpIfZHPEh0ib7YoDlnnDp5HtjDqbAw"
    msg = ""  
    if request.method == "POST":
        context =  {}
        msg = "Operación no permitida"
        pin = request.POST.get('pin', None)
        control_key = request.POST.get('control_key', None)
        if pin != None and control_key != None:
            if control_key == CONTROL_KEY:
                try:
                    emp = get_or_none(Employee, pin, "pin")
                    login(request, emp.user)
                    request.session['pwa_app_session'] = True
                    return redirect(reverse('pwa-employee'))
                except Exception as e:
                    msg = "Pin no válido"
                    print(e)
            else:
                msg = "Bad control"
    return render(request, "pwa-login.html", {'msg': msg})

def pin_logout(request):
    logout(request)
    return redirect(reverse('pwa-login'))

'''
    EMPLOYEES
'''
@group_required_pwa("employees")
def employee_home(request):
    #context = {"obj": request.user.employee}
    #if user_in_group(request.user, "admins"):
    #    context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/home.html", {"obj": request.user.employee})

@group_required_pwa("employees")
def employee_service(request, obj_id):
    service = get_or_none(Service, obj_id)
    return render(request, "pwa/employees/service.html", {"obj": service, "status_list": ServiceStatus.objects.all()})

@group_required_pwa("employees")
def employee_service_step1(request):
    return render(request, "pwa/employees/step1.html", {})

@group_required_pwa("employees")
def employee_service_step11(request):
    client = get_or_none(Client, get_param(request.GET, "value"), "code")
    return render(request, "pwa/employees/step11.html", {"client": client})

@group_required_pwa("employees")
def employee_service_step2(request):
    client = get_or_none(Client, get_param(request.GET, "obj_id"))
    type_list = ServiceType.objects.all()
    inf_list = Infestation.objects.all()
    context = {"client": client, "type_list": type_list, "inf_list": inf_list}
    return render(request, "pwa/employees/step2.html", context)

@group_required_pwa("employees")
def employee_service_step3(request):
    #print(request.POST)
    try:
        emp = request.user.employee
        client = get_or_none(Client, get_param(request.POST, "client"))
        obj = Service.objects.create(employee=emp, client=client)
        obj.service_type = get_or_none(ServiceType, get_param(request.POST, "type"))
        obj.infestation = get_or_none(Infestation, get_param(request.POST, "infestation"))
        obj.clean_notes = get_param(request.POST, "clean_notes")
        obj.place_notes = get_param(request.POST, "place_notes")
        obj.save()
        context = {
            "obj": obj, 
            "biocide_list": Biocide.objects.all(), 
            "btype_list": BiocideType.objects.all(), 
            "bwarning_list": BiocideWarning.objects.all()
        }
        return render(request, "pwa/employees/step3.html", context)
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

@group_required_pwa("employees")
def employee_service_step4(request):
    #print(request.POST)
    try:
        obj = get_or_none(Service, get_param(request.POST, "obj"))
        for item in request.POST.getlist("biocide"):
            ServiceBiocide.objects.get_or_create(service=obj, biocide=get_or_none(Biocide, item))
        for item in request.POST.getlist("b_type"):
            ServiceBiocideType.objects.get_or_create(service=obj, biocide_type=get_or_none(BiocideType, item))
        for item in request.POST.getlist("b_warn"):
            ServiceBiocideWarning.objects.get_or_create(service=obj, biocide_warning=get_or_none(BiocideWarning, item))
        context = {
            "obj": obj, 
        }
        return render(request, "pwa/employees/step4.html", context)
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

@group_required_pwa("employees")
def employee_service_step5(request):
    #print(request.POST)
    try:
        obj = get_or_none(Service, get_param(request.POST, "obj"))
        ini_date = get_param(request.POST, "ini_date")
        end_date = get_param(request.POST, "end_date")
        ini_time = get_param(request.POST, "ini_time")
        end_time = get_param(request.POST, "end_time")
        try:
            obj.ini_date = get_local_date(ini_date, ini_time)
            obj.end_date = get_local_date(end_date, end_time)
            obj.save()
        except:
            pass
        context = {
            "obj": obj, 
        }
        return render(request, "pwa/employees/step5.html", context)
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

@group_required_pwa("employees")
def employee_service_step6(request):
    #print(request.POST)
    try:
        obj = get_or_none(Service, get_param(request.POST, "obj"))
        signature = get_param(request.POST, "signature")
        if signature:
            # separa el header de la imagen base64
            formato, img_str = signature.split(';base64,')
            ext = formato.split('/')[-1]  # png, jpg, etc.

            # convierte base64 → archivo
            data = ContentFile(base64.b64decode(img_str), name=f"{uuid.uuid4()}.{ext}")
            obj.sign = data
            obj.save()
        context = {
            "obj": obj, 
        }
        return redirect("pwa-employee")
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))


#@group_required_pwa("employees")
#def employee_service_new(request, obj_id=""):
#    obj = get_or_none(Service, obj_id)
#    type_list = ServiceType.objects.all()
#    inf_list = Infestation.objects.all()
#    client_list = Client.objects.all()
#    employee_list = Employee.objects.all()
#    context = {'obj':obj, 'type_list':type_list, 'inf_list':inf_list, 'client_list':client_list, 'employee_list':employee_list}
#    return render(request, "pwa/employees/service_new.html", context)
#
#@group_required_pwa("employees")
#def employee_service_new_save(request):
#    s_type = get_or_none(ServiceType, get_param(request.POST, "service_type"))
#    status = get_or_none(ServiceStatus, get_param(request.POST, "status"))
#    client = get_or_none(Client, get_param(request.POST, "client"))
#    emp = get_or_none(Employee, get_param(request.POST, "employee"))
#    notes = get_param(request.POST, "notes")
#    #charged = get_param(request.GET, "charged")
#
#    obj = get_or_none(Service, get_param(request.POST, "obj_id"))
#    if obj == None:
#        obj = Service.objects.create()
#    obj.service_type = s_type
#    obj.status = status
#    obj.client = client
#    obj.employee = emp
#    obj.notes = notes
#    obj.save()
#    return redirect(reverse("pwa-employee-service-new", kwargs={'obj_id': obj.id}))
#
#@group_required_pwa("employees")
#def employee_service_save(request):
#    service = get_or_none(Service, get_param(request.POST, "service"))
#    status = get_or_none(ServiceStatus, get_param(request.POST, "status"))
#    service.status = status
#    service.emp_notes = get_param(request.POST, "emp_notes")
#    service.save()
#    return redirect(reverse("pwa-employee-service", kwargs={'obj_id': service.id}))

@group_required_pwa("employees")
def employee_notes(request):
    context = {"obj": request.user.employee}
    if user_in_group(request.user, "admins"):
        context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/notes.html", context)

@group_required_pwa("employees")
def employee_note(request):
    return render(request, "pwa/employees/note.html", {})

def transcribe_audio(file, obj_id):
    subprocess.run(["python", "transcribir.py", file, str(obj_id)])

@group_required_pwa("employees")
def employee_note_save(request):
    concept = get_param(request.POST, "concept")
    audio = None
    if "audio" in request.FILES and request.FILES["audio"] != "":
        audio = request.FILES["audio"]
        concept = "Esperando traducción de audio..."
    if concept != "" or audio != None:
        note = Note.objects.create(concept=concept, audio=audio)
        if "audio" in request.FILES and request.FILES["audio"] != "":
            t = threading.Thread(target=transcribe_audio, args=[note.audio.url, note.id], daemon=True)
            t.start()
    return redirect(reverse('pwa-employee'))

'''
    INCIDENTS
'''
@group_required_pwa("employees")
def incidents(request):
    now = datetime.now()
    idate = now.replace(hour=0, minute=0)
    edate = now.replace(hour=23, minute=59)
    item_list = Incident.objects.filter(owner=request.user, creation_date__range=(idate, edate))
    return render(request, "pwa/incidents/incidents.html", {'item_list': item_list})

@group_required_pwa("employees")
def incidents_add(request):
    return render(request, "pwa/incidents/incidents-form.html", {})

@group_required_pwa("employees")
def incidents_save(request):
    try:
        code = get_random_str(9)
        subject = get_param(request.POST, "subject")
        description = get_param(request.POST, "description")
        incident = Incident.objects.create(code=code, subject=subject, description=description, owner=request.user)
        return redirect("pwa-incidents")
    except Exception as e:
        return (render(request, "error_exception.html", {'exc':show_exc(e)}))

