import requests
import datetime
import pprint
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

curr_date = datetime.date.today().strftime('%d-%m-%y')

mys_restricted_pin = [
    570008, 571186, 570026, 570020, 570004, 570010, 570004, 570001, 570013, 570007, 570001,
    570002, 570017, 570010, 570020, 570008, 570001, 570010, 570019, 570012, 570014, 570008, 570023, 570011,
    570001, 570004, 570001, 570024, 570004, 570023, 570019, 570004, 570001, 570006, 570021, 570016, 570004,
    570001, 570004, 570008, 570005, 570008, 570007, 570004, 570010, 570021, 570015, 570011, 570007, 570020,
    570004, 570006, 570009, 570004, 570021, 570015, 570011, 570003, 570008, 570021, 570019, 570005, 570004,
    570002, 570008, 570017, 570008, 570020, 571130
]
jayanagara_pin = [560011]

district_code = {'mysore': 266, 'chamarajanagar': 271, 'bbmp': 294}
# default payload
dist_payload = {'district_id': district_code['mysore'], 'date': curr_date}

subscribers = [
    {'age': 18,
     'district': 'mysore',
        'to_email': [],  # add email
     'restricted_pin':mys_restricted_pin,
     'name':'Mysuru City'
     },
    {'age': 18,
     'district': 'chamarajanagar',
     'to_email': [],  # add email
     'name':'Chamarajanagara District',
     'restricted_hospital':[]  # hospital code(s)
     },
    {'age': 45,
        'district': 'bbmp',
        'to_email': [],  # add email
        'name':'Jayanagara, Bengaluru',
     'restricted_pin':jayanagara_pin
     }
]

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
           'content-type': 'application/json',
           "Accept-Language": 'hi-IN'
           }

smtpServer = "smtp.gmail.com"
port = 587
from_email = ''  # add email
pswd = ''  # password
context = ssl.create_default_context()

pp = pprint.PrettyPrinter(indent=4)

dist_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict'

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


def send_email(email_content, place_name, to_email=[], age=18):

    try:
        if(len(to_email) > 0):
            intro = 'Vaccine for age <strong>{}</strong>+ in <strong>{}</strong> available at {} pincode(s) as on {} {}'.format(
                age, place_name, len(email_content), curr_time, curr_date)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Vaccine {}+".format(age)
            msg['From'] = ''  # email
            table_contents = ''
            sorted_keys = sorted(email_content)

            for key in sorted_keys:
                center_list = email_content[key]
                if(len(center_list) > 0):
                    for center in center_list:
                        col1 = '<td>'+str(center['name'])+'</td>'
                        col2 = '<td>'+str(center['pin_code'])+'</td>'
                        col3 = ''
                        for info in center['date_slots']:
                            col3 += str(info)+'<br>'
                        col3 = '<td>'+col3+'</td>'
                        col4 = '<td>'+center['cost']+'</td>'

                        row = '<tr>{}{}{}{}</tr>'.format(col1,
                                                         col2, col3, col4)
                        table_contents += row

            html = """ <html>
					<head>{}</head>
					<body>
						<p>{}</p>
						<table>					
						<tr><th>Name</th><th>Pin</th><th>Date(no. of slots)</th><th>Fee</th></tr>
						{}
						</table>
						<p><a href={}>Register</a></p>
					</body>
					</html>
					""".format(table_style, intro, table_contents, booking_website)
            table_info = MIMEText(html, 'html')
            server = smtplib.SMTP(smtpServer, port)
            server.starttls(context=context)
            server.ehlo()
            msg.attach(table_info)
            server.ehlo()
            server.login(from_email, pswd)
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        print("the email could not be sent.", e)
    finally:
        server.close()


def apply_filter(district_id, s_idx, c_idx):
    group = subscribers[s_idx]
    clinic_data = master_data[district_id][c_idx]
    pin_check = False
    hospital_check = False
    if('restricted_pin' not in group or clinic_data['pincode'] in group['restricted_pin']):
        pin_check = True
    if('restricted_hospital' not in group or clinic_data['center_id'] in group['restricted_hospital']):
        hospital_check = True
    return pin_check and hospital_check


def get_centers(subscriber_idx):

    group = subscribers[subscriber_idx]
    temp = {}
    dist_payload['district_id'] = district_code[group['district']]
    if(dist_payload['district_id'] not in master_data):
        result = requests.get(dist_url, params=dist_payload, headers=headers)
        print('res:', result.status_code)
        if(result.status_code == 200):
            master_data[dist_payload['district_id']] = result.json()['centers']
        else:
            return temp

    try:
        clinics_data = master_data[dist_payload['district_id']]
        for clinic_idx, clinics in enumerate(clinics_data):
            if(apply_filter(dist_payload['district_id'], subscriber_idx, clinic_idx)):
                clinic = {}
                clinic['name'] = clinics['name']
                clinic['pin_code'] = clinics['pincode']
                clinic['date_slots'] = []
                clinic['cost'] = str(clinics['fee_type'])

                for sessions in clinics['sessions']:
                    if(sessions['min_age_limit'] == int(group['age']) and sessions['available_capacity'] > 0):
                        clinic['date_slots'].append(
                            sessions['date']+'('+str(sessions['available_capacity'])+')')
                        if(clinics['pincode'] not in temp):
                            temp[clinics['pincode']] = []
                if('vaccine_fees' in clinics):
                    for vaccine_type in clinics['vaccine_fees']:
                        clinic['cost'] += "<br>" + \
                            str(vaccine_type['vaccine']) + \
                            '-'+str(vaccine_type['fee'])
                if(len(clinic['date_slots']) > 0):
                    temp[clinics['pincode']].append(clinic)
    except Exception as e:
        print("Error ", e)
    finally:
        return temp


for s_idx, group in enumerate(subscribers):

    curr_time = datetime.datetime.now().strftime('%H:%M:%S')
    district_name = group['district']
    dist_payload['district_id'] = district_code[district_name]

    dist_res = get_centers(s_idx)

    place_name = group['name'] if 'name' in group else district_name.capitalize()
    print('Last status fetched for '+place_name+' at '+str(curr_time)+' ' +
          str(curr_date)+' for age '+str(group['age'])+', no. of centers:', len(dist_res))
    if(len(dist_res) > 0):
        send_email(dist_res, place_name, group['to_email'], group['age'])
