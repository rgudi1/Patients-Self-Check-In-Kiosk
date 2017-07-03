import datetime as dt
import requests
import urllib
import datetime
from drchrono.shorthands import DrChrono_Shortcuts


class DrChrono_API(object):
	base_url = "https://drchrono.com"
	def __init__(self, access_token):
        	self.access_token = access_token
        	self.headers = {'Authorization': 'Bearer %s' % self.access_token}

	def get_full_url(self, end_url, **querystrings):
		full_url = self.base_url + end_url + "?" + urllib.urlencode(querystrings)
		return full_url

	def get_patient_id(self, **kwargs):
		firstname = kwargs.pop('firstname','')
		lastname = kwargs.pop('lastname','')
		ssn = kwargs.pop('ssn','')
		full_url = self.get_full_url('/api/patients', first_name=firstname, last_name=lastname)
		print(full_url)
		response = requests.get(full_url, headers=self.headers)
		print(response)
		data = response.json()
		print(data)
		patient_id = None
		if data['results']:
			patient_id =  data['results'][0]['id']
		print("===================================================")
		#print(data['results'][0]['id'])
		print("===================================================")
		return patient_id

	def get_today_appointments_by_name(self, **kwargs):
		firstname = kwargs.pop('firstname','')
		lastname = kwargs.pop('lastname','')
		ssn = kwargs.pop('ssn','')
		full = kwargs.pop('full','')
		i=dt.datetime.now()
		date=i.strftime('%Y-%m-%d')
		# Get the patient id
		patient_id = self.get_patient_id(firstname=firstname, lastname=lastname)
		print("ID+",patient_id)		
		# Get today's appointments
		date=datetime.date.today()
		full_url = self.get_full_url('/api/appointments', date=date)
		response = requests.get(full_url, headers=self.headers)
		data = response.json()
		print(":::::::::::::::::::::::::::::::::::::::::::")
		print(data)
		print(":::::::::::::::::::::::::::::::::::::::::::")
		patient_a_details = []
		if data['results']:
			# Get the patient name and ssn given patient ID
			for i in range(0,len(data['results'])):
				if data['results'][i]['patient'] == patient_id:
					if full:
						return data['results'][i]
					scheduled_time = data['results'][i]['scheduled_time']
					duration = data['results'][i]['duration']
					status = data['results'][i]['status']
					if not status:
						status = DrChrono_Shortcuts.Statuses.NOT_CONFIRMED
					reason = data['results'][i]['reason']
					if not reason:
						reason = DrChrono_Shortcuts.Statuses.NOT_MENTIONED
					patient_a_details.append({'firstname':firstname,'lastname':lastname, 'scheduled_time':scheduled_time, 'duration':duration,'status':status, 'reason':reason }) 
					break					
#		if data['results'] and full:
#			return data['results'][0]		
		return patient_a_details

	def get_patient_info_by_id(self, id):
		full_url = self.base_url + '/api/patients/' + str(id)
		response = requests.get(full_url, headers=self.headers)
		return response.json()
		
	def update_patient_info_by_id(self, id, data):
		full_url = self.base_url + '/api/patients/' + str(id)
		print("g=", data['gender'])
		response = requests.put(full_url,data=data, headers=self.headers)
		return response
				
	def update_patient_appointment_by_id(self, appointment_id, data):
		full_url = self.base_url + '/api/appointments/' + str(appointment_id)
		response = requests.put(full_url,data=data, headers=self.headers)
		return response

	def get_all_appointments(self):
		date=datetime.date.today()
		full_url = self.get_full_url('/api/appointments', date=date)
		response = requests.get(full_url, headers=self.headers)
		data = response.json()
		return data['results']
	def get_patient_appointment_by_id(self,appointment_id):
		print(appointment_id)
		full_url = self.base_url + '/api/appointments/' + str(appointment_id)
		response = requests.get(full_url, headers=self.headers)
		data = response.json()
		return data
