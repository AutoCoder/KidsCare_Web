#! /bin/bash
echo "1)sync the web server code from github";
echo "..."
git pull
echo

echo "2)killall uwsgi instances"
killall -9 uwsgi
echo

echo "3)restart nginx"
echo "..."
/usr/local/nginx/sbin/nginx -s reload
if [ $? -ne 0 ]; then
   echo "nginx restarted failed"
else
   echo "nginx is restarted!"
fi;
echo

echo "4)restart the uwsgi"
uwsgi --ini uwsgi.ini
if [ $? -ne 0 ]; then
    echo "uwsgi reload failed"
else
    echo "The follow uwsgi instances is launched!"
    sleep 2  
    echo `ps -e|grep uwsgi`
fi;
