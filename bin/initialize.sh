#!/bin/bash

# create settings_private.py

cat << EOF > settings_private.py
KEY="`pwgen 40 `"
GOOGLE_MAPS_KEY="ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSosDVG8KKPE1-m51RBrvYughuyMxQ-i1QfUnH94QxWIa6N4U6MouMmBA"
EOF


