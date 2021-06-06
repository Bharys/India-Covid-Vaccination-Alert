import requests
import datetime
import time
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

curr_day = datetime.date.today()
if(int(datetime.datetime.now().strftime('%H'))>=16):curr_day += datetime.timedelta(1)
curr_day = curr_day.strftime('%d-%m-%Y')

mys_restricted_pin = [
	570008, 571186, 570026, 570020, 570004, 570010, 570004, 570001, 570013, 570007, 570001,
	570002, 570017, 570010, 570020, 570008, 570001, 570010, 570019, 570012, 570014, 570008, 570023, 570011,
	570001, 570004, 570001, 570024, 570004, 570023, 570019, 570004, 570001, 570006, 570021, 570016, 570004,
	570001, 570004, 570008, 570005, 570008, 570007, 570004, 570010, 570021, 570015, 570011, 570007, 570020,
	570004, 570006, 570009, 570004, 570021, 570015, 570011, 570003, 570008, 570021, 570019, 570005, 570004,
	570002, 570008, 570017, 570008, 570020, 571130
]
jayanagara_pin = [560011, 560069]
pavan_pin = [560001, 560011, 560069]
kadur_pin = [577548]
hoshangabad_pin = [461001]

district_code = {'mysore': 266, 'chamarajanagar': 271,'bbmp': 294}
dist_payload = {'district_id': district_code['mysore'], 'date': curr_day}

subscribers = [
	{'age':18,
	'district':'mysore',
	'to_email':[''],
	'restricted_pin':mys_restricted_pin,
	'name':'Mysuru City',
	'dose':1,
	'vaccine':'covishield'
	},
	{'age':45,
	'district':'bbmp',
	'to_email':[''],
	'restricted_pin':jayanagara_pin,
	'name':'Jayanagara, Bengaluru',
	'dose':2,
	'date':'08-06-2021'
	},
	{'age':45,
	'district':'mysore',
	'to_email':[],
	'name':'Mysore City',
	'restricted_pin':mys_restricted_pin,
	'date':'29-06-2021',
	'dose':2
	}
]

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
	   'content-type': 'application/json',
	   "Accept-Language": 'hi-IN'
	   }

smtpServer = "smtp.gmail.com"
port = 587
from_email = ''
pswd = ''
context = ssl.create_default_context()

dist_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
master_data = {}
booking_website = 'https://selfregistration.cowin.gov.in/'

table_style = """
				<style>
					table,th,tr,td{
					border:0.1px solid black
					}
					table{
					border-collapse:collapse
					}
                </style>
			"""

def get_from_date(s_idx):
	
	group = subscribers[s_idx]
	from_date = curr_day
	if('date' in group and (time.strptime(group['date'],'%d-%m-%Y') > time.strptime(curr_day,'%d-%m-%Y'))):from_date = group['date']
	return from_date

def get_dates(s_idx,num_days=3):
	
	dates = []
	
	start_date = get_from_date(s_idx)
	dates.append(start_date)
	start_datetime_format = datetime.date(*[int(y) for y in start_date.split('-')[-1::-1]])

	for idx in range(1,num_days):
		tmp = start_datetime_format+datetime.timedelta(idx)
		tmp = tmp.strftime('%d-%m-%Y')
		dates.append(tmp)
	
	return dates

def send_email(email_content, place_name, to_email=[], age=18, dose=1):

	try:
		if(len(to_email) > 0):
			intro = f'Vaccine for age <strong>{age}+, Dose{dose}</strong> in <strong>{place_name}</strong>  available at {len(email_content)} pincode(s) as on {curr_time} {curr_day}'
			msg = MIMEMultipart('alternative')
			msg['Subject'] = f"Vaccine {age}+ Dose{dose}, {place_name}"
			msg['From'] = ''
			table_contents = ''
			sorted_keys = sorted(email_content)
			
			for key in sorted_keys:
				center_list = email_content[key]
				if(len(center_list) > 0):
					for center in center_list:
						col_name = f"<td>{center['name']}</td>"
						col_pin = f"<td>{center['pin_code']}</td>"
						col_slot = f"<td>{center['date_slots']}</td>"
						col_cost = f"<td>{center['cost']}</td>"

						row = f'<tr>{col_name}{col_pin}{col_slot}{col_cost}</tr>'
						table_contents += row

			html = f'<html>'\
					f'<head>{table_style}</head>'\
					f'<body>'\
					f'<p>{intro}</p>'\
					f'<table>'\
					f'<tr><th>Name</th><th>Pin</th><th>Date(no. of slots)</th><th>Fee</th></tr>'\
					f'{table_contents}'\
					f'</table>'\
					f'<p><a href={booking_website}>Register</a></p>'\
					f'</body>'\
					f'</html>'
			table_info = MIMEText(html, 'html')
			server = smtplib.SMTP(smtpServer, port)
			server.starttls(context=context)
			server.ehlo()
			msg.attach(table_info)
			server.ehlo()
			server.login(from_email, pswd)
			server.sendmail(from_email, to_email, msg.as_string())
	except Exception as e:
		print(f"email could not be sent for {age}+, Dose{dose} in {place_name}, error:{e}")
	finally:
		server.close()


def apply_filter(s_idx, c_idx,date):
	
	group = subscribers[s_idx]
	age = int(group['age'])
	district_id = district_code[group['district']]
	clinic_data = master_data[(district_id, date)][c_idx]
	
	pin_check = False
	hospital_check = False
	vaccine_check = False
	age_check = clinic_data['min_age_limit'] == age
	
	if(age_check):		

		if('restricted_pin' not in group or clinic_data['pincode'] in group['restricted_pin']): pin_check = True
		if('restricted_hospital' not in group or clinic_data['center_id'] in group['restricted_hospital']): hospital_check = True
		if('vaccine' not in group or clinic_data['vaccine'].lower() == group['vaccine'].lower()):vaccine_check = True
		
	return age_check and pin_check and hospital_check and vaccine_check


def get_slot_capacity(subscriber_idx, clinic_day_data):

	group = subscribers[subscriber_idx]
	dose_num = group['dose']
	slot_capacity = int(clinic_day_data['available_capacity'])
	if(slot_capacity > 0):
		if(('available_capacity_dose1' or 'available_capacity_dose2') in clinic_day_data):
			slot_capacity = int(clinic_day_data.get('available_capacity_dose'+str(dose_num), 0))
	return slot_capacity


def get_centers(subscriber_idx):

	
	group = subscribers[subscriber_idx]
	temp = {}

	dist_payload['district_id'] = district_code[group['district']]
	date_list = get_dates(subscriber_idx)
	req = requests.Session()

	for date in date_list:
		dist_payload['date'] = date
		master_data_key = (dist_payload['district_id'],date)

		if(master_data_key not in master_data):
			try:
				result = req.get(dist_url, params=dist_payload, headers=headers,timeout=(2,4))
				result.raise_for_status()
				print('res:',result.status_code,' date:',date)
				master_data[master_data_key] = result.json()['sessions']
			except Exception as e:
				print(f"Date:{date} Error:{e}")
				continue

		clinics_data = master_data[master_data_key]

		for clinic_idx, clinics in enumerate(clinics_data):

			filter_res = apply_filter(subscriber_idx,clinic_idx,date)
			num_slots = get_slot_capacity(subscriber_idx, clinics)
			
			if(filter_res and num_slots > 0):		

				clinic = {}
				clinic['name'] = clinics['name']
				clinic['pin_code'] = clinics['pincode']
				clinic['date_slots'] = f"{clinics['date']}({num_slots})-{ clinics['vaccine']}"
				clinic['cost'] = str(clinics['fee_type'])				
				
				if(clinics['pincode'] not in temp):temp[clinics['pincode']] = []
				if(clinic['cost'].lower()=='paid'):clinic['cost'] += f"<br> {clinics['vaccine']}-{clinics['fee']}"

				temp[clinics['pincode']].append(clinic)

	return temp

try:
	for s_idx, group in enumerate(subscribers):
		
		district_name = group['district']
		dist_payload['district_id'] = district_code[district_name]
		dist_res = []

		curr_time = datetime.datetime.now().strftime('%H:%M:%S')
		st_date = get_from_date(s_idx)
		if('dose' in group and group['dose']>0 and group['dose']<3):
			dist_res = get_centers(s_idx)	
			place_name = group['name'] if 'name' in group else district_name.capitalize()
			if(len(dist_res)>0):send_email(dist_res,place_name,group['to_email'],group['age'],group['dose'])
			print(f"Last status fetched for(2) {place_name} for age {group['age']}, Dose { group['dose']} "\
				f"at {curr_time} {curr_day}, no. of centers:{len(dist_res)}")
		else:print('Dose info not available/incorrect')
except Exception as e:
	print("Error:",e)