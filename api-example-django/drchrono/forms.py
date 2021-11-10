from django import forms
from localflavor.us.us_states import STATE_CHOICES
from drchrono.shorthands import DrChrono_Shortcuts
# forms go here
class SearchAppointmentForm(forms.Form):
	firstname = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': ' First Name'}) )
	lastname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': ' Last Name'}) )
	ssn = forms.CharField(max_length=10, widget=forms.PasswordInput(attrs={'placeholder': ' SSN'}, render_value = True) )

class PatientInfoForm(forms.Form):
    	first_name = forms.CharField(required=False)
    	middle_name = forms.CharField(required=False)
	last_name = forms.CharField(required=False)
	date_of_birth = forms.DateField(required=True)
	gender = forms.ChoiceField(required=True, choices=(
		('','Select'),
		(DrChrono_Shortcuts.Gender.FEMALE, DrChrono_Shortcuts.Gender.FEMALE),
		(DrChrono_Shortcuts.Gender.MALE,   DrChrono_Shortcuts.Gender.MALE),
		(DrChrono_Shortcuts.Gender.OTHER,  DrChrono_Shortcuts.Gender.OTHER),
	))
	social_security_number = forms.CharField(required=False)
	home_phone = forms.CharField(required=False)
	cell_phone = forms.CharField(required=False)
	address = forms.CharField(required=False)
	city = forms.CharField(required=False)
	state = forms.ChoiceField(required=False, choices= STATE_CHOICES)
	zip_code = forms.CharField(required=False)
	email = forms.CharField(required=False)
	ethnicity = forms.ChoiceField(required=False, choices=(
		(DrChrono_Shortcuts.Ethnicity.BLANK, DrChrono_Shortcuts.Ethnicity.BLANK),
		(DrChrono_Shortcuts.Ethnicity.HISPANIC, DrChrono_Shortcuts.Ethnicity.HISPANIC),
		(DrChrono_Shortcuts.Ethnicity.NOT_HISPANIC,DrChrono_Shortcuts.Ethnicity.NOT_HISPANIC),
		(DrChrono_Shortcuts.Ethnicity.DECLINED,DrChrono_Shortcuts.Ethnicity.DECLINED),
	))
	race = forms.ChoiceField(required=False, choices=(
		(DrChrono_Shortcuts.Race.BLANK,DrChrono_Shortcuts.Race.BLANK),
		(DrChrono_Shortcuts.Race.INDIAN,DrChrono_Shortcuts.Race.INDIAN),
		(DrChrono_Shortcuts.Race.ASIAN,DrChrono_Shortcuts.Race.ASIAN),
		(DrChrono_Shortcuts.Race.HAWAIIAN,DrChrono_Shortcuts.Race.HAWAIIAN),
		(DrChrono_Shortcuts.Race.WHITE,DrChrono_Shortcuts.Race.WHITE),
		(DrChrono_Shortcuts.Race.DECLINED,DrChrono_Shortcuts.Race.DECLINED),
	))

	emergency_contact_name = forms.CharField(required=False)
	emergency_contact_phone = forms.CharField(required=False)
	emergency_contact_relation = forms.CharField(required=False)

	employer = forms.CharField(required=False)
	employer_address = forms.CharField(required=False)
	employer_city = forms.CharField(required=False)
	employer_state = forms.ChoiceField(required=False, choices= STATE_CHOICES)
	employer_zip_code = forms.CharField(required=False)

	responsible_party_name = forms.CharField(required=False)
	responsible_party_relation = forms.CharField(required=False)
	responsible_party_phone = forms.CharField(required=False)
	responsible_party_email = forms.CharField(required=False)
