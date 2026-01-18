from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import gettext_lazy as _ 

import datetime


def sub_hours(hour1, hour2):
    """
    Resta dos objetos time y devuelve la diferencia como timedelta
    """
    now = datetime.datetime.now().date()

    datetime1 = datetime.datetime.combine(now, hour1)
    datetime2 = datetime.datetime.combine(now, hour2)

    diff = datetime1 - datetime2
    return int(diff.total_seconds() / 60)

def hours_mins(minutes):
    hours=0
    if minutes > 59:
        hours += minutes // 60
        minutes = minutes % 60
    return hours, minutes

'''
    AUX
'''

'''
    EMPLOYEE
'''
class Employee(models.Model):
    pin = models.CharField(max_length=20, verbose_name = _('PIN'), default="")
    dni = models.CharField(max_length=20, verbose_name = _('DNI'), default="")
    name = models.CharField(max_length=200, verbose_name = _('Razón Social'), default="")
    phone = models.CharField(max_length=50, verbose_name = _('Teléfono de contacto'), null=True, default = '0000000000')
    email = models.EmailField(verbose_name = _('Email de contacto'), default="", null=True)
    user = models.OneToOneField(User, verbose_name='Usuario', on_delete=models.CASCADE, null=True, blank=True, related_name='employee')

    def __str__(self):
        return self.name

    def save_user(self):
        if self.user == None:
            self.user = User.objects.create_user(username=self.email, email=self.email)
            self.save()
            group = Group.objects.get(name='employees') 
            group.user_set.add(self.user)
        else:
            self.user.username = self.email
            self.user.save()

#    def worked_time(self, ini_date, end_date):
#        try:
#            idate = "{} 00:00".format(ini_date)
#            edate = "{} 23:59".format(end_date)
#            item_list = self.assistances.filter(ini_date__gte=idate, end_date__lte=edate)
#            #item_list = self.assistances.filter(ini_date__gte=ini_date, end_date__lte=end_date)
#            hours = 0
#            minutes = 0
#            for item in item_list:
#                if item.finish:
#                    diff = item.end_date - item.ini_date
#                    days, seconds = diff.days, diff.seconds
#                    hours += seconds // 3600
#                    minutes += (seconds % 3600) // 60
#                    #hours = days * 24 + seconds // 3600
#                    #seconds = seconds % 60
#            if minutes > 59:
#                hours += minutes // 60
#                minutes = minutes % 60
#            return hours, minutes
#            #return "{}:{}".format(hours, minutes) 
#            #return "{} horas y {}  minutos".format(hours, minutes) 
#        except Exception as e:
#            print(e)
#            return 0, 0
#
#    def client_worked_time(self, client, ini_date, end_date):
#        idate = "{} 00:00".format(ini_date)
#        edate = "{} 23:59".format(end_date)
#        item_list = self.assistances.filter(ini_date__gte=idate, end_date__lte=edate, client__id=client)
#        hours = 0
#        minutes = 0
#        for item in item_list:
#            if item.finish:
#                diff = item.end_date - item.ini_date
#                days, seconds = diff.days, diff.seconds
#                hours += seconds // 3600
#                minutes += (seconds % 3600) // 60
#                #hours = days * 24 + seconds // 3600
#                #seconds = seconds % 60
#        if minutes > 59:
#            hours += minutes // 60
#            minutes = minutes % 60
#        return hours, minutes
# 
#    def client_work(self, client):
#        item_list = self.timetables.filter(client__id=client)
#        mins = 0
#        for item in item_list:
#            try:
#                mins += sub_hours(item.end, item.ini)
#            except Exception as e:
#                mins += 0
#        return hours_mins(mins)
 
    def clients(self):
        dic = {}
        for item in self.timetables.all():
            if item.client.name not in dic.keys():
                dic[item.client.name] = []
            dic[item.client.name].append({"day":item.week_day, "ini":item.ini, "end":item.end, "id":item.id, "client":item.client.id})
        return dic

    def client_list(self, qr_access=""):
        if qr_access != "":
            return self.timetables.filter(client__qr_access=qr_access).order_by("client").distinct("client")
        return self.timetables.all().order_by("client").distinct("client")

    class Meta:
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')
        ordering = ["name"]

'''
    CLIENTS
'''
def upload_form_qr(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "clients/qr/%s" % (instance.id)
    return '/'.join(['%s' % (folder), datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class Client(models.Model):
    qr_access = models.BooleanField(default=False, verbose_name=_('Acceso QR'));
    inactive = models.BooleanField(default=False, verbose_name=_('Desactivado'));
    code = models.CharField(max_length=200, verbose_name = _('Code'), default="")
    name = models.CharField(max_length=200, verbose_name = _('Razón Social'), default="")
    phone = models.CharField(max_length=50, verbose_name = _('Teléfono de contacto'), null=True, default='0000000000')
    email = models.EmailField(verbose_name = _('Email de contacto'), default="", null=True)
    address = models.TextField(verbose_name = _('Dirección'), null=True, default='')
    observations = models.TextField(verbose_name = _('Observaciones'), null=True, default='')
    qr = models.ImageField(upload_to=upload_form_qr, blank=True, verbose_name="QR", help_text="Select file to upload")

    def __str__(self):
        return self.name

    def assigned_work(self):
        item_list = self.timetables.filter(client__id=self.id)
        mins = 0
        for item in item_list:
            try:
                mins += sub_hours(item.end, item.ini)
            except Exception as e:
                mins += 0
        return hours_mins(mins)
 
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')

class ClientTimetable(models.Model):
    day = models.IntegerField(verbose_name = _('Día'), default=0)
    ini = models.TimeField(max_length=10, verbose_name = _('Hora de inicio'), default=datetime.time(8,0,0))
    end = models.TimeField(max_length=10, verbose_name = _('Hora de fin'), default=datetime.time(8,0,0))
    client = models.ForeignKey(Client,verbose_name=_('Cliente'),on_delete=models.SET_NULL,null=True,related_name="timetables")
    employee = models.ForeignKey(Employee,verbose_name=_('Empleado'),on_delete=models.SET_NULL,null=True,related_name="timetables")

    #def __str__(self):
    #    return self.name

    @property
    def week_day(self):
        wd = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return wd[self.day]

    class Meta:
        verbose_name = _('Horario')
        verbose_name_plural = _('Horarios')
        ordering = ["day",]

'''
    SERVICES TYPE
'''
class ServiceType(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")

    class Meta:
        verbose_name = _('Tipo de servicio')
        verbose_name_plural = _('Tipos de servicios')

'''
    CLIENTS CONTRACTS
'''
class ClientContract(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    porta = models.IntegerField(verbose_name = _('Portacebos'), default=0)
    ini = models.DateField(max_length=10, verbose_name = _('Hora de inicio'), default=datetime.datetime.today())
    end = models.DateField(max_length=10, verbose_name = _('Hora de fin'), default=datetime.datetime.today())
    client = models.ForeignKey(Client,verbose_name=_('Cliente'),on_delete=models.SET_NULL,null=True,related_name="contracts")

    #def __str__(self):
    #    return self.name

    def get_service_value(self, service):
        ccst = ClientContractServiceType.objects.filter(contract=self, service_type=service).first()
        return 0 if ccst == None else ccst.services

    class Meta:
        verbose_name = _('Contrato')
        verbose_name_plural = _('Contratos')
        ordering = ["ini",]

class ClientContractServiceType(models.Model):
    services = models.IntegerField(verbose_name = _('Número de servicios'), default=0)
    contract = models.ForeignKey(ClientContract,verbose_name=_('Contrato Cliente'),on_delete=models.SET_NULL,null=True,related_name="service_types")
    service_type = models.ForeignKey(ServiceType,verbose_name=_('Tipo de servicio'),on_delete=models.SET_NULL,null=True,related_name="client_contracts")

    #def __str__(self):
    #    return self.name

    def create_services(self):
        ini = self.contract.ini
        end = self.contract.end
        if isinstance(ini, str):
            ini = datetime.datetime.strptime(ini, "%Y-%m-%d")
        if isinstance(end, str):
            end = datetime.datetime.strptime(end, "%Y-%m-%d")

        delta = end - ini
        step = delta / (self.services)
        for i in range(self.services):
            date = ini + i * step
            #print(f'client={self.contract.client}, ini_date={date}, end_date={date}, service_type={self.service_type}')
            s = Service.objects.create(client=self.contract.client, contract=self.contract, ini_date=date, end_date=date, service_type=self.service_type)

    def get_services(self):
        return Service.objects.filter(contract=self.contract, service_type=self.service_type, ini_date__range=(self.contract.ini,self.contract.end)).order_by("id")

    class Meta:
        verbose_name = _('Servicio del contrato')
        verbose_name_plural = _('Servicios del Contrato')


'''
    SERVICES 
'''
class Infestation(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")

    class Meta:
        verbose_name = _('Plaga')
        verbose_name_plural = _('Plagas')

class Biocide(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")

    class Meta:
        verbose_name = _('Biocida')
        verbose_name_plural = _('Biocidas')

class BiocideType(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")

    class Meta:
        verbose_name = _('Tipo de biocida')
        verbose_name_plural = _('Tipos de biocidas')

class BiocideWarning(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")

    class Meta:
        verbose_name = _('Peligrosidad')
        verbose_name_plural = _('Peligrosidad')

def upload_sign(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "signatures/%s" % (instance.id)
    return '/'.join(['%s' % (folder), datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class Service(models.Model):
    deleted = models.BooleanField(default=False, verbose_name=_('Borrado'), null=True);
    ini_date = models.DateTimeField(default=datetime.datetime.now(), null=True, verbose_name=_('Inicio'))
    end_date = models.DateTimeField(default=datetime.datetime.now(), null=True, verbose_name=_('Fin'))
    place_notes = models.TextField(verbose_name = _('Notas'), null=True, default='')
    clean_notes = models.TextField(verbose_name = _('Notas del empleado'), null=True, default='')
    sign = models.ImageField(upload_to=upload_sign, blank=True, verbose_name="Firma", help_text="Select file to upload")

    infestation = models.ForeignKey(Infestation, verbose_name=_('Agente a combatir'), on_delete=models.SET_NULL, null=True)
    service_type = models.ForeignKey(ServiceType, verbose_name=_('Tipo de servicio'), on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, verbose_name=_('Cliente'), on_delete=models.SET_NULL, null=True, related_name="services")
    contract = models.ForeignKey(ClientContract,verbose_name=_('Contrato'),on_delete=models.SET_NULL,null=True,related_name="services")
    employee = models.ForeignKey(Employee,verbose_name=_('Empleado'),on_delete=models.SET_NULL,null=True,related_name="services")

    class Meta:
        verbose_name = _('Servicio')
        verbose_name_plural = _('Servicios')

class ServiceBiocide(models.Model):
    biocide = models.ForeignKey(Biocide, verbose_name=_('Biocida'), on_delete=models.SET_NULL, null=True, related_name="services")
    service = models.ForeignKey(Service, verbose_name=_('Servicio'), on_delete=models.CASCADE, null=True, related_name="biocides")

    class Meta:
        verbose_name = _('Servicio Biocida')
        verbose_name_plural = _('Servicios Biocidas')

class ServiceBiocideType(models.Model):
    biocide_type = models.ForeignKey(BiocideType, verbose_name=_('Tipo biocida'), on_delete=models.SET_NULL, null=True, related_name="services")
    service = models.ForeignKey(Service, verbose_name=_('Servicio'), on_delete=models.CASCADE, null=True,related_name="biocides_types")

    class Meta:
        verbose_name = _('Servicio Tipo Biocida')
        verbose_name_plural = _('Servicios Tipos Biocidas')

class ServiceBiocideWarning(models.Model):
    biocide_warning = models.ForeignKey(BiocideWarning, verbose_name=_('Peligrosidad'), on_delete=models.SET_NULL, null=True, related_name="services")
    service = models.ForeignKey(Service, verbose_name=_('Servicio'), on_delete=models.CASCADE, null=True, related_name="biocides_warnings")

    class Meta:
        verbose_name = _('Servicio Peligrosidad')
        verbose_name_plural = _('Servicios Peligrosidad')


'''
    Incidents
'''
class Incident(models.Model):
    closed = models.BooleanField(default=False, verbose_name = _('Estado'))
    code = models.CharField(max_length=10, verbose_name=_('Código'))
    subject = models.CharField(max_length=255, verbose_name=_('Asunto'))
    description = models.TextField(verbose_name=_('Descripción'), default='', blank=True, null=True)
    creation_date = models.DateTimeField(default=datetime.datetime.now(), verbose_name=_('Creado el'))
    closed_date = models.DateTimeField(default=datetime.datetime.max, blank=True, null=True, verbose_name=_('Cerrado el'))

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, verbose_name=_('Creada por'))

    @property
    def employee(self):
        return Employee.objects.filter(user=self.owner).first()

    class Meta:
        verbose_name = _('Incidente')
        verbose_name_plural = _('Incidentes')
        ordering = ['-creation_date']

    def __str__(self):
        return self.subject

