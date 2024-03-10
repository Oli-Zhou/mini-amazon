# Mini-Amazon
Implemented Mini-Amazon web services with Python, Django as framework, and Postgres as database.

## Table of Contents
- [Description](#description)
- [Technologies Used](#Technologies-Used)
- [Installation](#installation)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone Project](#2-clone-project)
  - [3. Configure Local Database](#3-configure-local-database)
  - [4. Configure APIs and Local Variables](#4-configure-apis-and-local-variables)
- [Usage](#usage)
  - [1. Run the Server](#1-run-the-server)
  - [2. Run the Website (Django)](#2-run-the-website-django)
- [Demo](#demo)


## Description
- A full-stack web app modeling Amazon system paired with [warehouse/world simulator](https://github.com/yunjingliu96/world_simulator_exec) and [Mini-UPS](https://github.com/FANFANFAN2506/Mini_UPS) using Django and PostgreSQL, which simulates the entire process from purchasing to delivery
- Implemented [backend server](https://github.com/CaoRui0910/Mini-Amazon/tree/main/server), using Socket and Google Protocol Buffer to communicate with world-simulator and Mini-UPS server
- All features are described in detail in this [document](https://github.com/CaoRui0910/Mini-Amazon/blob/main/differentiation.pdf)
- 🆒 See all Demos [here](#demo), which includes screenshots. Click on this [link](https://youtu.be/rV_J4431dYQ) to see a video demo (Note: Due to network limitations, some functions involving emails (e.g., subscriptions, emails about successful purchases, emails about package status) were not recorded. Besides, the demo in this video doesn't work with the warehouse/world simulator and Mini-UPS, but interested parties can try to get the code for this project as well as the warehouse/world simulator and Mini-UPS from my GitHub link to get them to collaborate and communicate in order to simulate the entire process from purchasing to delivery.)

## Technologies Used
- **Django**: [Official tutorials](https://docs.djangoproject.com/en/4.2/intro/tutorial01/)
- **Google Protocol Buffers**: all of the API details for google protocol buffers can be found [here](https://protobuf.dev/reference/)

## Installation
### 1. Prerequisites
Please install in this order:
```
# Mainly for hw1 currently
sudo apt-get install gcc g++ make valgrind
sudo apt-get install emacs screen
sudo apt-get install postgresql
sudo apt-get install python python3-pip
sudo apt-get install libpq-dev
sudo pip3 install django psycopg2 

# After installing django, you can try this command
# Note you must upgrade your VCM from Ubuntu 18.04 to 20.04 to get this latest 4.0 version of Django
# To upgrade your VCM, execute 'sudo do-release-upgrade' and hit enter through the various prompts
# Then re-execute 'sudo pip3 install django psycogp2'
$ django-admin --version
4.1.5

sudo apt-get install libssl-dev libxerces-c-dev libpqxx-dev
sudo apt-get install manpages-posix-dev
```
Install Google Protocol Buffers:
```
pip install protobuf
```

### 2. Clone Project
Git clone my repository:
```
git clone https://github.com/CaoRui0910/Mini-Amazon.git
```
Install all project-specific requirements:
```
pip3 install -r requirements.txt
```
### 3. Configure Local Database
Connect to postgres server and set up password
```
sudo su - postgres
psql
ALTER USER psql WITH PASSWORD 'passw0rd'; ## replace $PWD with your password
-- Then execute command '\q' to leave postgres
-- Then 'exit' to exit from 'postgres' user back to your default user ID
```

Create database:
```
psql -U <userid>  ## e.g., psql -U postgres
CREATE DATABASE miniamazondb;
```

### 4. Configure APIs and Local Variables
Edit the Django `web-app/mysite/settings.py` file:
1. The `ALLOWED_HOSTS` setting in Django defines the list of hosts/domains that the Django site can serve. You can add '*' to allow all hosts:
```
ALLOWED_HOSTS = ['vcm-30609.vm.duke.edu','127.0.0.1','web','localhost', '*']
```
2. Setting up the database configurations:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'miniamazondb',
        'USER': 'postgres',
        'PASSWORD': 'passw0rd',
        'HOST': 'db',
        'PORT': '5432',
    }
}
# replace miniamazondb with your database name, 
# postgres with your username, 
# and passw0rd with your password
```
3. Change your timezone if you are not in Eastern Standard Time:
```
TIME_ZONE = 'EST'
```
4. Email:
```
# send email:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'miniamazon.rui.aoli1@gmail.com'
EMAIL_HOST_PASSWORD = 'atonbhciojlkrdoo'
```
Also, in `web-app/mini_amazon/utils.py`, edit the following part:
```python
# set up email
EMAIL_SERVER = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# original password: xzaq123.
EMAIL_SERVER.login('miniamazon.rui.aoli1@gmail.com', 'atonbhciojlkrdoo')
```

## Usage
### 1. Run the Server
To run Server part, i.e., communication with [warehouse/world simulator](https://github.com/yunjingliu96/world_simulator_exec) and [Mini-UPS](https://github.com/FANFANFAN2506/Mini_UPS), you can `cd` into `server` directory and then run:
`python3 server.py`

### 2. Run the Website (Django)
Then, `cd` into `web-app` and run the following code:
```
python3 manage.py makemigrations mini_amazon
python3 manage.py migrate
python3 manage.py runserver
```
If you want add data into the database, such as adding products in mini-amazon web, you can try to create an admin user: go to this [link](https://docs.djangoproject.com/en/4.2/intro/tutorial02/), and check "Introducing the Django Admin" part in this link.

## Demo
**Click on this [link](https://youtu.be/rV_J4431dYQ) to see a video demo.**
<br>
<br>
Below are screenshots.
<br>
<br>
1. Home page
<img width="800" alt="Screen Shot 2023-11-10 at 05 59 16" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/5e7ec15b-2608-43f0-8346-4dfc5f3a454d">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 05 57 05" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/5f980b73-5ac0-473b-a7e8-35c585eccd5b">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 05 58 05" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/94b94ccb-9d81-4d87-bf23-1dddfcfbf671">
<br>
<br>

2. Header Section
<img width="800" alt="Screen Shot 2023-11-10 at 06 52 10" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/905297df-eb4d-44a9-ad88-3a66ccb99c7b">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 52 40" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/0b2c4e28-b398-4983-9ce4-2bbc74843308">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 53 04" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/ee67e376-5f0e-4bdb-91c3-9d3f29d33a59">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 53 24" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/92e961e3-9553-4af0-aa1e-b9ce62d2193d">
<br>
<br>

3. Footer Section
<img width="800" alt="Screen Shot 2023-11-10 at 06 49 44" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/a6f109e8-88b9-453a-9987-bad724e567b0">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 47 49" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/b4765db1-f2e5-4e0d-8684-2adbca7bd7b6">
<br>
<br>

4. Products List<br>
All products:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 08 01" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/cb837245-bb54-49a5-afc5-06db569c0e46">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 07 20" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/77bd17ae-e943-443b-b936-07d24e3b2ae8">
<br>
<br>
Product category:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 09 16" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/3bf8cbd3-37ab-4b3f-897c-de41c7087a4b">
<br>
<br>

5. Search Product<br>
Search product by product category. For example, parfum:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 12 26" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/87c4cd23-1129-4d10-a618-7289000d5caa">
<br>
<br>
Search in all products:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 14 22" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/a692ca63-66bb-459f-93bd-01e578c33a80">
<br>
<br>
Seach in a specific product category:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 17 20" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/4bca8c62-abf1-430c-8d5a-76432e5301bf">
<br>
<br>

6. Product Details
<img width="800" alt="Screen Shot 2023-11-10 at 06 18 42" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/d4e402de-4995-4013-b188-00836c961e0b">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 19 45" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/20b92370-e9e4-4b07-a7a1-ec857197a585">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 20 25" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/f8a026f3-dfff-4554-8f16-04e256dbc553">
<br>
<br>

7. Account Details
<img width="800" alt="Screen Shot 2023-11-10 at 06 29 56" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/d5b64b23-c316-4b48-a940-47c07d2674e5">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 32 39" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/693bd3ec-cea7-4ea0-91f9-11ecf8c92f55">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 32 06" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/7c19015d-d25b-4e56-8623-f2b1352afeca">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 33 21" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/e946dccb-b3de-48cd-bb47-9bfd1a0a8821">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 33 51" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/681d6660-e29e-4c3e-bf90-8ef236043267">
<br>
<br>

8. Historical Orders
<img width="800" alt="Screen Shot 2023-11-10 at 06 42 16" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/98636933-091d-4718-aade-9d93b82446d3">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 42 16" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/fa92f04d-dd7a-444b-be81-b5df75874b83">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 42 16" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/02b5b66a-304f-4f7a-bd74-1ae2fb60dc36">
<br>
<br>

9. Shopping Cart
<img width="800" alt="Screen Shot 2023-11-10 at 06 36 19" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/221c09ca-ba68-422f-a385-9720d3eabf7b">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 37 11" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/3006f0c5-6131-41ba-8c1b-8d1bc7b28095">
<br>
<br>

10. Checkout
<img width="800" alt="Screen Shot 2023-11-10 at 06 37 48" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/0cc05b50-391c-40e4-ac6b-b59c25fdd985">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 39 55" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/4c2be25c-03c1-4a42-82e0-2a0b26a7ed4b">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 40 47" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/7c5b3603-bb4d-444a-8a52-b89a0aada368">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 41 33" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/f0dd7399-98db-47b2-8ace-23f990b9a923">
<br>
<br>

11. Subscribe
<img width="800" alt="Screen Shot 2023-11-10 at 06 43 56" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/47c3a4e0-deeb-4b85-9c4a-81095576f62c">
<br>
<br>
<img width="900" alt="Screen Shot 2023-11-10 at 06 44 30" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/cb88afd8-48bb-4790-a3a5-d0c4bbe8a7a6">
<br>
<br>
<img width="550" alt="Screen Shot 2023-11-10 at 06 45 38" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/8f054c56-d989-4884-baeb-33cd1e2c8d84">
<br>
<br>



12. Other Small Features<br>
BGM:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 47 17" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/2a74ece0-6d13-4b0e-8a5b-c3bf73cecdac">
<br>
<br>
"About us" in Footer Section:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 53 59" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/2ba7ac2f-8697-48e3-ba94-2f39c482cdbb">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 54 28" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/51e974b3-3507-4fb5-9be3-3a4850b1dff8">
<br>
<br>
"Get The App" in Footer Section:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 55 10" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/99daa0a6-4c82-4271-b1eb-cd9cde5e7c0b">
<br>
<br>
"FAQ" in Footer Section:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 56 20" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/37b53173-d639-4766-80ea-5ed87e81615a">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 56 50" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/61af5bf0-8d23-4f65-bdbf-28ee7f7adc58">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 57 11" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/be2ba367-6bf3-463b-a8b4-f9ff80256baf">
<br>
<br>
"Returns & Exchanges" in Footer Section:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 58 13" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/505b3a05-d224-46d4-95bf-d237d4fb8b4c">
<br>
<br>
"Shopping Guide" in Footer Section:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 59 02" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/5d4bf7af-4bc6-441e-aed8-c408eec39b32">
<br>
<br>
"Contact Us" in Footer Section:<br>
<img width="800" alt="Screen Shot 2023-11-10 at 06 59 19" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/2b1b4f25-8f5c-48a2-8f24-3539326c059b">
<br>
<br>
<img width="800" alt="Screen Shot 2023-11-10 at 07 00 16" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/c9eb1f2b-7fd2-4d5f-af4b-2bb5db8c4ae6">
<br>
<br>


13. Admin
<img width="800" alt="Screen Shot 2023-11-10 at 05 56 29" src="https://github.com/CaoRui0910/Mini-Amazon/assets/93239143/299eb1eb-9fcf-4c87-bd1a-43da03e4014a">














