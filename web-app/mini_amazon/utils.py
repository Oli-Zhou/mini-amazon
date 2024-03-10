# from .models import Upss, Address, Category, Products, Packages, Warehouse
import sys
import math
from email.message import EmailMessage
import smtplib
import re

# def get_best_warehouse(x, y):
#     all_warehouses = Warehouse.objects.all()
#     result_id = 0
#     reslut_distance = sys.maxsize
#     for warehouse in all_warehouses:
#         distance = math.sqrt(math.pow(warehouse.x - x, 2) + math.pow(warehouse.y - y, 2))
#         if distance < reslut_distance:
#             reslut_distance = distance
#             result_id = warehouse.id
#     return result_id


# set up email
EMAIL_SERVER = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# original password: xzaq123.
EMAIL_SERVER.login('miniamazon.rui.aoli1@gmail.com', 'atonbhciojlkrdoo')

def send_email(subject, email_content, receiver):
    print("Send email")
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'Mini Amazon Team'
    msg['To'] = receiver
    msg.set_content(email_content)
    try:
        EMAIL_SERVER.send_message(msg)
        print("Finish Send email")
    except:
        print("email send error!!!")
        # ??????????????????
        pass

# check whether the parttern of the user input email is valid
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


# email = "1@1.co"
# print(is_valid_email(email))