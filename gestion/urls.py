from django.urls import path
from . import views, auto_views

urlpatterns = [ 
    path('home', views.index, name='index'),
    path('services/list', views.services_list, name='services-list'),
    path('services/search', views.services_search, name='services-search'),
    path('services/form', views.services_form, name='services-form'),
    path('services/form-save', views.services_form_save, name='services-form-save'),
    path('services/remove', views.services_remove, name='services-remove'),
    path('services/remove-soft', views.services_remove_soft, name='services-remove-soft'),

    #---------------------- EMPLOYEES -----------------------
    path('employees', views.employees, name='employees'),
    path('employees/list', views.employees_list, name='employees-list'),
    path('employees/search', views.employees_search, name='employees-search'),
    path('employees/form', views.employees_form, name='employees-form'),
    path('employees/remove', views.employees_remove, name='employees-remove'),
    path('employees/save-email', views.employees_save_email, name='employees-save-email'),

    #---------------------- EMPLOYEE -----------------------
    path('employee/<int:obj_id>', views.employee, name='employee'),
    path('employee/search', views.employee_search, name='employee-search'),
    path('employee/search-client', views.employee_search_client, name='employee-search-client'),
    path('employee/form/timetable', views.employee_form_timetable, name='employee-form-timetable'),
    path('employee/form/timetable/remove/<int:obj_id>', views.employee_form_timetable_remove, name='employee-form-timetable-remove'),

    #------------------------- CLIENTS -----------------------
    path('clients', views.clients, name='clients'),
    path('clients/list', views.clients_list, name='clients-list'),
    path('clients/search', views.clients_search, name='clients-search'),
    path('clients/form', views.clients_form, name='clients-form'),
    path('clients/remove', views.clients_remove, name='clients-remove'),
    path('clients/assistances/<int:obj_id>', views.clients_assistances, name='clients-assistances'),

    #---------------------- INCIDENTS -----------------------
    path('incidents', views.incidents, name='incidents'),
    path('incidents/list', views.incidents_list, name='incidents-list'),
    path('incidents/search', views.incidents_search, name='incidents-search'),
    path('incidents/form', views.incidents_form, name='incidents-form'),

    #---------------------- AUTO -----------------------
    path('autosave_field/', auto_views.autosave_field, name='autosave_field'),
    path('autoremove_obj/', auto_views.autoremove_obj, name='autoremove_obj'),
]

