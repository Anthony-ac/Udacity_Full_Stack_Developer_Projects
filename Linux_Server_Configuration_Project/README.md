# README for Udacity Linux Configuration Project

This project deploys the Item Catalog application onto an ubuntu web server hosted by aws.
It configures the following:
- ubuntu Server
- apache2
- wsgi
- PostgreSQL

## Installation & Configuration

**Get your server**
1. Create Ubuntu Server instance via AWS Lightsail.
2. IP Address: XX.XXX.XXX.XXX (Provided by AWS)
3. SSh Port: 2200
4. URL: IP Address (URL optional)
	
**Secure Your Server**
5. Update currently installed packages: `sudo apt-get update`
6. Upgrade linux server: `sudo apt-get upgrade`
7. Create new custom port 2200 via aws firewall
8. Change from default port 22 to 2200 (ensure you save): `sudo nano /etc/ssh/sshd_config`
9. Configure uncomplicated firewall:
`sudo ufw allow 2200/tcp`
`sudo ufw allow 80/tcp`
`sudo ufw allow 123/udp`
`sudo ufw enable`
10. Restart ssh service: `Sudo service ssh restart`
11. Login via terminal with `ssh -i "yourdefaultkey".pem ubuntu@XX.XXX.XXX.XXX -p 2200`
	
**Give Grader Access**
12. Create user *grader*: `sudo adduser grader`
13. Create grader file in sudoers.d directory: `sudo nano /etc/sudoers.d/grader`
edit grader file by pasting: **added: grader ALL=(ALL) NOPASSWD:ALL** (this gives ability to sudo)
14. Create private and public keys locally with `ssh-keygen`
15. Switch to grader account: `su - grader`
16. Create and edit *authorized_keys file* in new .ssh directory: 
`sudo mkdir .ssh`
`sudo nano ssh/authorized_keys`
paste public key in authorized_keys file and save.
17. Restart ssh service: `Sudo service ssh restart` and log off.
18. Log back in with: `ssh -i id_rsa grader@18.223.195.147 -p 2200`

**Prepare to Deploy Your Project**
19. Configure local time Zone to UTC: `sudo dpkg-reconfigure tzdata`
20. Ensure the following in *sshd_config file* are set as below:`sudo nano /etc/ssh/sshd_config` 
Changes PermitRootLogin to no
PasswordAuthentication set to no
21. Install Apache Server: `sudo apt-get install apache2`
22. Install python 3 mod_wsgi `sudo apt-get install libapache2-mod-wsgi-py3`
23. Restart apache : `sudo service apache2 restart`
24. Install python `sudo apt-get install python3.6` and others:
`sudo apt-get install python-pip` (to get pip)
`sudo pip install httplib2 oauth2client sqlalchemy psycopg2 sqlalchemy_utils requests 
Flask`
25. Install psycopg2: `sudo apt-get -qqy install postgresql python-psycopg2`
26. Check if no connections are allowed: `sudo vim /etc/postgresql/9.3/main/pg_hba.conf`
27. Install postgresql `sudo apt-get install postgresql`
28. get into postgresql shell: `psql`
29. create new db and user named *catalog* in psql :
```
        create database catalog;
        create user catalog;
```
30. Set password for user: 
```
alter user catalog with password "your password";
```
31. Give the user catalog permission to the db:
```
grant all privileges on database catalog to catalog;
```
32. quit psql shell and logoff user *postgres*
```
		\q
```
`exit`

		

**Deploy the Item Catalog project**
33. Install Git: `sudo apt-get install git`
34. Change directory: `cd /var/www`
35. Create directory and move to it: `sudo mdir FlaskApp && cd FlaskApp`
36. Clone directory: `git clone https://github.com/anthony-88/Items-Catalog-Project-for-Udacity.git` (this would be your directory in git hub)
37. Rename directory: `sudo mv Items-Catalog-Project-for-Udacity FlaskApp`
38. Rename *main.py*: `sudo mv main.py __init__.py`(ensure its double underscore)
39. Create *FlaskApp.conf* to configure virtual host:
`sudo nano /etc/apache2/sites-available/FlaskApp.conf`
Paste the following:
```
            <VirtualHost *:80>
				ServerName 52.24.125.52
				ServerAdmin qiaowei8993@gmail.com
				WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
				<Directory /var/www/FlaskApp/FlaskApp/>
					Order allow,deny
					Allow from all
				</Directory>
				Alias /static /var/www/FlaskApp/FlaskApp/static
				<Directory /var/www/FlaskApp/FlaskApp/static/>
					Order allow,deny
					Allow from all
				</Directory>
				ErrorLog ${APACHE_LOG_DIR}/error.log
				LogLevel warn
				CustomLog ${APACHE_LOG_DIR}/access.log combined
			</VirtualHost>
```
40. Enable the virtual host above: `sudo a2ensite FlaskApp`
41. Create .wsgi file: `cd /var/www/FlaskApp && sudo nano flaskapp.wsgi`
Add the following:
```
			#!/usr/bin/python
			import sys
			import logging
			logging.basicConfig(stream=sys.stderr)
			sys.path.insert(0,"/var/www/FlaskApp/")

			from FlaskApp import app as application
			application.secret_key = 'Add your secret key'
```
43. Restart Apache: `sudo service apache2 restart`
42. Go to the following directory: `cd /var/www/FlaskApp/FlaskApp`
43. Modify the *db_setup.py, populate_db.py and  _ init _.py files* as follows (do this for your files):
From : `engine = create_engine('sqlite:///weightlifting.db')` 
To: `engine = create_engine('postgresql://catalog:udacity5@localhost/catalog')`
	44. Run the following in order (run your files):
`python db_setup.py`
`python populate_db.py`
`python __init__.py`	

## References
[Udacity](https://www.udacity.com/)
[a2hosting](https://www.a2hosting.com/kb/getting-started-guide/accessing-your-account/disabling-ssh-logins-for-root)
[fosslinux](https://www.fosslinux.com/1115/how-to-reboot-shutdown-log-off-pc-from-terminal-by-command-line-in-ubuntu-and-linux-mint.htm)
[digitalocean](https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps)
[htaccess-guide](http://www.htaccess-guide.com/how-to-use-htaccess/)
[digitalocean](https://www.digitalocean.com/community/questions/500-internal-server-error-how-can-i-fix-this-this-website-was-supposed-to-be-a-christmas-present)
[digitalocean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)