#!/bin/bash
res=$(python3 ~/cowin_check_email.py)
echo "$res" > ~/result.txt
