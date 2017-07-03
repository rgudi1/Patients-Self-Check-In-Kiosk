from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    url(r'^accounts/profile/reports$', views.ReportsView.as_view(), name='reports'),

    url(r'^accounts/profile/complete/(?P<appointment_id>\d+)$', views.CompleteSessionView.as_view(), name='complete_session'),

    url(r'^accounts/profile/dashboard$', views.DashboardView.as_view(), name='dashboard_appointments'),

    url(r'^accounts/profile/success/(?P<room_id>\d+)$', views.SucessAndSurveyView.as_view(), name='success_and_survery'),

    url(r'^accounts/profile/update_info/(?P<patient_id>\d+)$',views.UpdateDemographsView.as_view(), name="update_demographic_information"),

    url(r'^accounts/profile/',views.CheckInFormView.as_view(), name="search_appointment"),

    url(r'', include('social.apps.django_app.urls', namespace='social')),

]

urlpatterns += staticfiles_urlpatterns()
