# CovidVaccinationEnquiry
A script to enquire when a covid vaccination slot opens up at a place / set of places in India and to send an email to the subscribers.
The script uses subscriber groups that have in common a district, set of pincodes if requried, age and preference for hospital(enter hospital code) if required and a list of email.
This was not hosted on any cloud platform, a local cronjob used to run the script every minute to make calls to the api opened by the Govt. [API Setu](https://apisetu.gov.in/public/marketplace/api/cowin)

The script cowin_appointment_check.py makes the api call and sends an email. 
Take note that only district_code and subscribes list and any dependencies(restricted pin/ restricted hospital codes) for filtering needs to be filled in.
vacc_check.sh is the file executed by the local cronjob which logs the result of the previous operation that includes status_code(200/403 etc..) and time and name of the center last pinged.
