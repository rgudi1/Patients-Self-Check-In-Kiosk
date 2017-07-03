# Create your views here.

from django.shortcuts import render, render_to_response
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, FormView
from django.template import RequestContext
from drchrono.forms import SearchAppointmentForm, PatientInfoForm
from drchrono.models import AppointmentHistoryModel
from drchrono.api import DrChrono_API
from drchrono.shorthands import DrChrono_Shortcuts
from django.core.urlresolvers import reverse
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart, PieChart, BarChart
from collections import Counter

from dateutil import parser
import requests, datetime


from django.contrib.auth import (
	authenticate,
	get_user_model,
	login,
	logout,
)


class CheckInFormView(View):
    form_class = SearchAppointmentForm
    template_name = 'check_in.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
	# The following handles the POST request to the get the appointment details
	api_request = DrChrono_API(get_user_access_token(self.request.user))
	form = self.form_class(request.POST)
	if form.is_valid():
    		cd = form.cleaned_data
		firstname = cd['firstname']
		lastname = cd['lastname']
		ssn = cd['ssn']
		api_response = api_request.get_patient_id(firstname=firstname, lastname=lastname, ssn=ssn)
		if api_response is None:
			print("Not present")
			return render(request, self.template_name, {'form': form, 'cred': DrChrono_Shortcuts.Validations.INVALID_CREDENTIALS})
		else:
			api_response_2 = api_request.get_today_appointments_by_name(firstname=firstname, lastname=lastname, ssn=ssn,full=False)
			return render(request, self.template_name, {'form': form, 'appointment_details':api_response_2, 'patient_id':api_response })
	return render(request, self.template_name, {'form': form})
        


class UpdateDemographsView(FormView):
    print("1")
    form_class = PatientInfoForm
    template_name = 'demographics.html'

    def dispatch(self, request, *args, **kwargs):
	print("2")
        self.api_request = DrChrono_API(get_user_access_token(request.user))
	self.patient_id = int(self.kwargs['patient_id'])
	self.patient_info = self.api_request.get_patient_info_by_id(self.patient_id)
        return super(UpdateDemographsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
	print("3")
        context = super(UpdateDemographsView, self).get_context_data(**kwargs)
        context['patient_info'] = self.patient_info
        return context    

    def get_initial(self):
	print(self.patient_info)
	return self.patient_info

    def form_valid(self, form):
        data = form.cleaned_data
	patient_id = self.patient_id
	doctor_id = self.patient_info['doctor']
	data.update({'doctor': doctor_id})
	self.patient_updated_info = self.api_request.update_patient_info_by_id(self.patient_id, data)
	name = data['first_name'] +" "+ data['last_name']
	print(self.patient_updated_info)
	if self.patient_updated_info.status_code != DrChrono_Shortcuts.ErrorCodes.SUCCESS:
		print("Exception while updating patient info")
		return HttpResponseRedirect(reverse('update_demographic_information', args=[patient_id]))
	else:
		self.appointment = self.api_request.get_today_appointments_by_name(firstname=data['first_name'], lastname= data['last_name'], full = True)
		appointment_id = self.appointment['id']
		print(self.appointment)
		self.appointment['status'] = DrChrono_Shortcuts.Statuses.ARRIVED
                update_response = self.api_request.update_patient_appointment_by_id(appointment_id, self.appointment)
		if update_response.status_code != DrChrono_Shortcuts.ErrorCodes.SUCCESS:
			print("Exception while updating patient appt")
			return HttpResponseRedirect(reverse('update_demographic_information', args=[patient_id]))
		else:
		        #If this successful, create and update the DB table using a Model class with - patient_id, doctor_id, Status=Arrived
			myModel = AppointmentHistoryModel.objects.get(appointment_id=appointment_id,patient_id=str(patient_id))
			if not myModel:
				ahmodel = AppointmentHistoryModel(name=name,appointment_id=appointment_id,patient_id=patient_id, status = DrChrono_Shortcuts.Statuses.ARRIVED, appointment_start_time = parser.parse(self.appointment['scheduled_time']), duration = self.appointment['duration'])
				try:
		        	        ahmodel.save()
				except Exception as e:
					#print("Exception while saving", str(e), e.__class__)
					return HttpResponseRedirect(reverse('update_demographic_information', args=[patient_id]))
			else:
				myModel.status=DrChrono_Shortcuts.Statuses.ARRIVED
				myModel.appointment_start_time = parser.parse(self.appointment['scheduled_time'])
				myModel.duration = self.appointment['duration']
				myModel.statusTime = datetime.datetime.now()
				myModel.save()
			return HttpResponseRedirect(reverse('success_and_survery', args = [self.appointment['office']] ))


class SucessAndSurveyView(FormView):
    template_name = 'successAndSurvey.html'
    def get(self, request, *args, **kwargs):
	room_id = kwargs['room_id']
        return render(request, self.template_name, {'room_id':room_id})

class DashboardView(FormView):
    template_name = 'dashboard.html'
    def get(self, request, *args, **kwargs):
	current_appointment, appointments = get_all_appointments_and_save(request)
	print("+++",AppointmentHistoryModel.objects.all().filter(appointment_id=2006))
        return render(request, self.template_name,{'current_appointment':current_appointment, 'appointments':appointments})
    def post(self, request, *args, **kwargs):
	if  "refresh" in request.POST:
		current_appointment, appointments = get_all_appointments_and_save(request)
		#no_show_send_email()
	        return render(request, self.template_name,{'current_appointment':current_appointment,'appointments':appointments})
	elif "begin" in request.POST:
		appointment_id = request.POST.get("appointment_id")
		patient_id = request.POST.get("patient_id")
		p=AppointmentHistoryModel.objects.get(appointment_id=appointment_id,patient_id=patient_id)
		p.status = DrChrono_Shortcuts.Statuses.IN_SESSION
		p.session_start_time = datetime.datetime.now()
		p.save()
		return HttpResponseRedirect(reverse('complete_session', args=[appointment_id]))

		
class CompleteSessionView(FormView):
    template_name = 'completeSession.html'
    def get(self, request, *args, **kwargs):
	appointment_id = kwargs['appointment_id']
	current_appointment=AppointmentHistoryModel.objects.get(appointment_id=appointment_id)
        return render(request, self.template_name, {'current_appointment':current_appointment, 'completed_appointment':None})
    def post(self, request, *args, **kwargs):
		appointment_id = kwargs['appointment_id']	
		p=AppointmentHistoryModel.objects.get(appointment_id=appointment_id)
		prev_appointment = p
		p.status = DrChrono_Shortcuts.Statuses.COMPLETE
		p.session_end_time = datetime.datetime.now()
		p.save()
		curr=AppointmentHistoryModel.objects.get(appointment_id=appointment_id)
		self.api_request = DrChrono_API(get_user_access_token(request.user))
                update_response = self.api_request.get_patient_appointment_by_id(appointment_id)
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")	
		print(update_response)
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
	        return render(request, self.template_name, {'current_appointment':prev_appointment, 'completed_appointment':curr})

class ReportsView(FormView):
    template_name = 'reports.html'
    def get(self, request, *args, **kwargs):
	appointments = AppointmentHistoryModel.objects.values()
	wait_time_count = 0
	wait_time_duration = 0
	delay_time_count = 0
	delay_time_duration = 0
	no_show = 0
	extra_time = 0
	extra_time_duration = 0
	d=0
	e=0
	for j in appointments:
		print([j['statusTime'], j['status'], j['session_start_time'],j['session_end_time'], j['appointment_start_time']])
		print("\n")
		if j['session_end_time'] is not None:
			d = j['session_end_time'] - j['session_start_time']
			d = divmod(d.days * 86400 + d.seconds, 60)
			d = d[0]
			e = j['session_end_time'] - j['appointment_start_time']
			e = divmod(e.days * 86400 + e.seconds, 60)
			e = e[0]
		if j['session_end_time'] is not None:
			wait_time_count = wait_time_count + 1
			diff = j['session_start_time'] - j['statusTime']
			datetime.timedelta(0, 8, 562000)
    			m_s = divmod(diff.days * 86400 + diff.seconds, 60)
    			wait_time_duration = wait_time_duration + m_s[0] # Patients Wait TIme = Session Start Time - Status Change Time
		if j['statusTime'] is not None and j['statusTime'] > j['appointment_start_time'] :
			delay_time_count = delay_time_count + 1
			diff = j['statusTime'] - j['appointment_start_time']
			datetime.timedelta(0, 8, 562000)
    			m_s = divmod(diff.days * 86400 + diff.seconds, 60)
    			delay_time_duration = delay_time_duration + m_s[0] # Patients Delay TIme = Appointment Start Time - Status Change Time
		if j['status'] not in [ DrChrono_Shortcuts.Statuses.ARRIVED , DrChrono_Shortcuts.Statuses.IN_SESSION, DrChrono_Shortcuts.Statuses.COMPLETE, DrChrono_Shortcuts.Statuses.NOT_CONFIRMED , DrChrono_Shortcuts.Statuses.NOT_MENTIONED]:
			no_show = no_show + 1
		if d<1800 and e>1800:
			extra_time = extra_time + 1
			extra_time_duration = extra_time_duration + 1
	da = [p['status'] for p in appointments]	
	counts = Counter(da)
	d =[]
	d = [[k, counts[k]] for k in counts ]
	d.insert(0,["Status","Number of hits"])
	d.append(["In Session",1])
	data_source2 = SimpleDataSource(data=d)
	metrics=dict()
	metrics["wait_time_count"] = int(wait_time_count)
	metrics["wait_time_duration"] = wait_time_duration
	metrics["delay_time_count"] = int(delay_time_count)
	metrics["delay_time_duration"] = delay_time_duration
	metrics["no_show"] = int(no_show)
	metrics["extra_time"] = int(extra_time)
	metrics["extra_time_duration"] = extra_time_duration
	context = {'metrics':metrics, 'pc':PieChart(data_source2,options={'title': "Statuses of all Appointments"})}
        return render(request, self.template_name, context)


def get_user_access_token(user, provider='drchrono'):
    return user.social_auth.get(provider=provider).extra_data.get('access_token')


def check_in(request):
	return render_to_response('check_in.html',{"user":request.user}, context_instance=RequestContext(request))

def get_all_appointments_and_save(request):
        api_request = DrChrono_API(get_user_access_token(request.user))
	appointments = AppointmentHistoryModel.objects.values()
	print(appointments)
	print("________________")
	appointment_ids = [d['appointment_id'] for d in appointments]
	current_appointment = get_current_time_appointment(appointments)
	#print("check=",current_appointment['check'])
	if not current_appointment or not current_appointment['check']:
		# Get today's all appointments
		all_appointments = api_request.get_all_appointments()
		print(all_appointments)
		print("---------------------------------------------------------")
		for aa in all_appointments:
			if int(aa['id']) not in appointment_ids:
				data = api_request.get_patient_info_by_id(aa['patient'])
				name = data['first_name'] +" "+ data['last_name']
				ahmodel = AppointmentHistoryModel(name=name,appointment_id=aa["id"],patient_id=aa["patient"], status = aa["status"], appointment_start_time = parser.parse(aa['scheduled_time']), duration = aa['duration'])
				ahmodel.save()
	appointments = AppointmentHistoryModel.objects.values()	
	print(appointments)
	return current_appointment, appointments

def get_current_time_appointment(appointments):
	now = datetime.datetime.now()
	for a in appointments:
		t = a['appointment_start_time']
		print("--------------------",t,"-----------", now)
		if t.day == now.day and t.hour == now.hour and now.minute in range(t.minute, t.minute+31):
			return a

