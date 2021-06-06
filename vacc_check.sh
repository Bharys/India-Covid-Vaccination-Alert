#!/bin/bash
res=$(python3 ~/covid_vacc_slot_enquiry.py)
echo "$res" > ~/result.txt
res=$(python3 ~/cowin_check_email.py)
echo "$res" >> ~/result.txt
