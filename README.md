# django_blog
django blo

开发环境： Ubuntu 14.04 + Anaconda2(python 2.7) + Pycharm
部署环境： django + mod_wsgi + apache2.4.7  
数据库：mysql

工程配置文件： （见apache_django_wsgi.conf）
<IfModule mod_wsgi.c>

WSGISocketPrefix /var/run/wsgi

Alias /uploads /home/xiaoxiong/PycharmProjects/django_project/uploads/
Alias /static /home/xiaoxiong/PycharmProjects/django_project/static/

<Directory /home/xiaoxiong/PycharmProjects/django_project/static>
Require all granted
</Directory>

<Directory /home/xiaoxiong/PycharmProjects/django_project/uploads>
Require all granted
</Directory>


<Directory /home/xiaoxiong/PycharmProjects/django_project>
<Files wsgi.py>
Require all granted
</Files>
</Directory>


WSGIDaemonProcess blogprj python-path=/home/xiaoxiong/PycharmProjects/django_project:/home/xiaoxiong/anaconda2/lib/python2.7/site-packages user=xiaoxiong group=xiaoxiong
WSGIProcessGroup blogprj
WSGIScriptAlias / /home/xiaoxiong/PycharmProjects/django_project/django_project/wsgi.py
AddType text/html .py

</IfModule>


Apache2配置文件：
LoadModule wsgi_module modules/mod_wsgi.so
Include /home/xiaoxiong/PycharmProjects/django_project/apache_django_wsgi.conf


settings.py：
1. 将日志器中的log地址加上BASE_DIR
2. STATICFILES_DIRS 以及 STATIC_ROOT


后台admin环境：
1. python manage.py collectstatic
2. mv admin ../static

