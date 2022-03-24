#!/bin/bash
echo "Migrations Initiated..."
sleep 2
FILE=/opt/app/wayrem-admin-backend/newmigration
# FILE=/home/fealty/Documents/Dynamic_Model/admin/wayrem-admin-backend/newmigration
echo "$FILE"
if test -f "$FILE"; then
    echo "$FILE exists."
    # /bin/python /opt/app/wayrem-admin-backend/manage.py makemigrations
    /usr/local/bin/python3.8 /opt/app/wayrem-admin-backend/manage.py makemigrations wayrem_admin
    sleep 3
    /usr/local/bin/python3.8 /opt/app/wayrem-admin-backend/manage.py migrate

    echo "Migrations Completed..."
    # /usr/bin/python3.8 /home/fealty/Documents/Dynamic_Model/admin/wayrem-admin-backend/manage.py makemigrations
    # sleep 3
    # /usr/bin/python3.8 /home/fealty/Documents/Dynamic_Model/admin/wayrem-admin-backend/manage.py migrate
    #...
    rm if "$FILE"
    echo "$FILE is removed"
fi