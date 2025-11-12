from django.urls import path
from pwa import views


urlpatterns = [
    path('', views.index, name="pwa-home"),
    path('home/', views.index, name="pwa-home"),
    path('login/', views.pin_login, name="pwa-login"),
    path('logoff/', views.pin_logout, name="pwa-logout"),

    # EMPLOYEES
    path('employee/', views.employee_home, name="pwa-employee"),
    path('employee/service/<int:obj_id>/', views.employee_service, name="pwa-employee-service"),

    path('employee/service/step1/', views.employee_service_step1, name="pwa-employee-service-step1"),
    path('employee/service/step11/', views.employee_service_step11, name="pwa-employee-service-step11"),

    path('employee/service/new/<int:obj_id>/', views.employee_service_new, name="pwa-employee-service-new"),
    path('employee/service/new/save/', views.employee_service_new_save, name="pwa-employee-service-new-save"),
    path('employee/service/save/', views.employee_service_save, name="pwa-employee-service-save"),

    path('employee/notes/', views.employee_notes, name="pwa-employee-notes"),
    path('employee/note/', views.employee_note, name="pwa-employee-note"),
    path('employee/note/save/', views.employee_note_save, name="pwa-employee-note-save"),

    # INCIDENTS
    path('incidents/incidents', views.incidents, name="pwa-incidents"),
    path('incidents/incidents/add', views.incidents_add, name="pwa-incidents-add"),
    path('incidents/incidents/save', views.incidents_save, name="pwa-incidents-save"),
]

