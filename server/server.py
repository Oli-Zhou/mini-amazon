import psycopg2
import socket
import amazon_world_pb2
import ups_amazon_pb2
import threading
import time
import smtplib
from email.message import EmailMessage
import math
import sys

from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32

test = True

########################################### global variables ###########################################
seqnum = 0
world_msg = {}
world_ack = []
# commands' seqnum from world 
world_seqnum = []
ups_msg = {}
ups_ack = []
# commands' seqnum from ups 
ups_seqnum = []

WAIT_TIME = 20  # if send a msg and wait for time longer than this => redeem it as timeout and resend the message
SIMSPEED = 100
UPS_SOCKET = 0
WORLD_SOCKET = 0
# set up email
EMAIL_SERVER = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# original password: xzaq123.
EMAIL_SERVER.login('miniamazon.rui.aoli@gmail.com', 'jzgrsrsqpefflbxi')

lock = threading.Lock()
# Connect to database
conn = psycopg2.connect(
    database="miniamazondb",
    user='postgres',
    password='passw0rd',
    host='db',
    port='5432'
)

# UPS_HOST = "vcm-30458.vm.duke.edu"
# UPS_PORT = 32345

# # ??????
# WORLD_HOST = "vcm-30458.vm.duke.edu"
# WORLD_PORT = 23456
UPS_HOST = "vcm-32421.vm.duke.edu"
UPS_PORT = 32345

# ??????
WORLD_HOST = "vcm-32421.vm.duke.edu"
WORLD_PORT = 23456

########################################### Basic functions ##########################################

def send_email(email_content, receiver, subject):
    if test:
        print("send_email")
    msg = EmailMessage()
    # 'Your package status changes'
    # or 'Your package destination changes'
    msg['Subject'] = subject
    msg['From'] = 'Mini Amazon Team'
    msg['To'] = receiver
    msg.set_content(email_content)
    try:
        thread_send_email = threading.Thread(target=EMAIL_SERVER.send_message, args=(msg,))
        thread_send_email.start()
    except:
        # print("Email Sending Error Happened")
        pass


def world_seq(msg):
    if test:
        print("world_seq")
    with lock:
        global seqnum
        seqnum = seqnum+1
        world_msg[seqnum] = msg
        return seqnum


def ups_seq(msg):
    if test:
        print("ups_seq")
    with lock:
        global seqnum
        seqnum = seqnum+1
        ups_msg[seqnum] = msg
        return seqnum

# socket send
def send_msg(sock, msg):
    if test:
        print("send_msg")
        print(msg)
    message = msg.SerializeToString()
    _EncodeVarint(sock.sendall, len(message), None)
    sock.sendall(message)

# socket receive
def recv_msg(socket):
    if test:
        print("recv_msg")
    var_int_buff = []
    while True:
        buf = socket.recv(1)
        var_int_buff += buf
        print(var_int_buff)
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket.recv(msg_len)
    return whole_message


# From UPS get world id
def recv_world_id(ups_socket):
    if test:
        print("recv_world_id")
    msg = ups_amazon_pb2.UTAConnect()
    msg.ParseFromString(recv_msg(ups_socket))
    world_id = msg.worldid
    # send_msg(ups_socket, world_id)
    return world_id


# initialize warehouses and inventory of this world and save the information of these three warehouses
def init_warehouse():
    if test:
        print("init_warehouse")
    # clear data in warehouse table
    cursor = conn.cursor()
    # ALTER SEQUENCE mini_amazon_warehouse_id_seq RESTART WITH 0;
    sql = "TRUNCATE TABLE mini_amazon_warehouse"
    cursor.execute(sql)
    # cursor.execute("ALTER SEQUENCE mini_amazon_warehouse_id_seq RESTART WITH 0 ;")
    cursor.execute("TRUNCATE TABLE mini_amazon_warehouse RESTART IDENTITY;")
    cursor.execute("TRUNCATE TABLE mini_amazon_inventories")
    conn.commit()
    warehouses = []
    # Assume we have 3 warehourses
    warehouses.append({})
    warehouses[0]['x'] = 10
    warehouses[0]['y'] = 10
    warehouses[0]['id'] = create_warehouse(10, 10)
    warehouses.append({})
    warehouses[1]['x'] = 50
    warehouses[1]['y'] = 50
    warehouses[1]['id'] = create_warehouse(50, 50)
    warehouses.append({})
    warehouses[2]['x'] = 100
    warehouses[2]['y'] = 100
    warehouses[2]['id'] = create_warehouse(100, 100)
    # initialize inventory data
    # cursor.execute("SELECT id FROM mini_amazon_products;")
    # products_id = cursor.fetchall()
    # for warehous in warehouses:
    #     for product_id in products_id:
    #         cursor.execute("INSERT INTO mini_amazon_inventories (warehouse_id, product_id, inventory_quantity) VALUES (%s, %s, %s);",
    #                        (warehous['id'], product_id[0], 0))
    # conn.commit()
    # cursor.close()
    return warehouses

# add 3 warehouses to database and get their id:
def create_warehouse(x, y):
    if test:
        print("create_warehouse")
    # try:
    cursor = conn.cursor()
    cursor.execute(
            "INSERT INTO mini_amazon_warehouse (x, y) VALUES (%s, %s) RETURNING id;", (x, y))
    wh_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    return wh_id
    # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)


def modify_package_status(package_id, status):
    if test:
        print("modify_package_status")
    # try:
    cur = conn.cursor()
    cur.execute(
            'UPDATE mini_amazon_packages SET status = %s WHERE id = %s', (status, package_id))
    conn.commit()
    cur.close()
    # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)

########################################### Basic functions end ##########################################


########################################### communication with a world ##########################################

# Connect to World with world_id
def conn_world(world_id):
    if test:
        print("conn_world")
    msg = amazon_world_pb2.AConnect()
    # msg.simspeed = SIMSPEED
    msg.worldid = world_id
    msg.isAmazon = True
    warehouses_list = init_warehouse()
    for warehouse in warehouses_list:
        msg.initwh.add(id=warehouse['id'], x=warehouse['x'], y=warehouse['y'])
    if test:
        print("====================AConnect::::")
        print(msg)
    # send AConnect to World:
    send_msg(WORLD_SOCKET, msg)
    # receive AConnected from World:
    world_reponse = amazon_world_pb2.AConnected()
    world_reponse.ParseFromString(recv_msg(WORLD_SOCKET))
    if world_reponse.result == "connected!":
        print("Amazon successfully connected to world " + str(world_id))
        return True
    else:
        print("Amazon failed to connect to world " + str(world_id))
        return False


def send_to_world(seq, command):
    if test:
        print("send_to_world")
        print(command)
    send_msg(WORLD_SOCKET, command)
    while True:
        time.sleep(WAIT_TIME)
        if seq in world_ack:
            break
        else:
            send_msg(WORLD_SOCKET, command)


# notify the world: BUYING
def world_buy(whnum, things, count):
    if test:
        print("world_buy")
    msg = amazon_world_pb2.ACommands()
    # msg.simspeed = SIMSPEED
    tobuy = msg.buy.add()
    tobuy.whnum = whnum
    if test:
        print(things)
    for thing in things:
        if test:
            print(thing[0])
            print(thing[1])
        tobuy.things.add(id=thing[0], description=thing[1], count=count)
    tobuy.seqnum = world_seq(tobuy)
    send_to_world(tobuy.seqnum, msg)


# handle APurchaseMore arrived response from world
def world_arrived(bought):
    if test:
        print("world_arrived")
    warehouse_id = bought.whnum
    for thing in bought.things:
        product_id = thing.id
        count = thing.count
        # try:
        cur = conn.cursor()
        cur.execute(
            "SELECT inventory_quantity FROM mini_amazon_inventories WHERE product_id = %s AND warehouse_id = %s;", (product_id, warehouse_id))
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO mini_amazon_inventories (warehouse_id, product_id, inventory_quantity) VALUES (%s, %s, %s);", (warehouse_id, product_id, count))
        else:
            inventory = row[0]
            cur.execute('UPDATE mini_amazon_inventories SET inventory_quantity = %s WHERE product_id = %s AND warehouse_id = %s;',
                    (inventory+count, product_id, warehouse_id))
        conn.commit()
        cur.close()
        # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)


# world_pack(whnum, things, package_id)
# notify the world: PACKING
def world_pack(whnum, product_id, description, package_id, purchase_quantity):
    if test:
        print("world_pack")
    msg = amazon_world_pb2.ACommands()
    # msg.simspeed = SIMSPEED
    to_pack = msg.topack.add()
    to_pack.whnum = whnum
    to_pack.shipid = package_id
    to_pack.things.add(id=product_id, description=description,
                       count=purchase_quantity)
    reduce_inventory(product_id, whnum, purchase_quantity)
    to_pack.seqnum = world_seq(to_pack)
    print("&&&&&&&&&&&&& send world: pack packages")
    send_to_world(to_pack.seqnum, msg)
    print("&&&&&&&&&&&&& send world: pack packages---modify status")
    modify_package_status(package_id, 2)
    # email to user to notify that their packages change status to PACKING
    # email_content = "Congratulations! Your package is being packed. Thanks for your patience."
    # receiver = get_user_email(package_id)
    # send_email(email_content, receiver, 'Your package status changes')


def reduce_inventory(product_id, warehouse_id, purchase_quantity):
    if test:
        print("reduce_inventory")
    # try:
    cur = conn.cursor()
    cur.execute("SELECT inventory_quantity FROM mini_amazon_inventories WHERE product_id = %s AND warehouse_id = %s;",
                    (product_id, warehouse_id))
    row = cur.fetchone()
    inventory = row[0]
    cur.execute('UPDATE mini_amazon_inventories SET inventory_quantity = %s WHERE product_id = %s AND warehouse_id = %s;',
                    (inventory-purchase_quantity, product_id, warehouse_id))
    conn.commit()
    cur.close()
    # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)


def world_packed(ready):
    if test:
        print("world_packed")
    package_id = ready.shipid
    # try:
    modify_package_status(package_id, 3)
    # email to user to notify that their packages change status to PACKING
    # email_content = "Congratulations! Your package has been packed. Thanks for your patience."
    # receiver = get_user_email(package_id)
    # send_email(email_content, receiver, 'Your package status changes')

    # except (Exception, psycopg2.DatabaseError) as error:
    # print(error)


# notify the world: LOADING
def world_load(whnum, truck_id, package_id):
    if test:
        print("world_load")
    msg = amazon_world_pb2.ACommands()
    # msg.simspeed = SIMSPEED
    toload = msg.load.add()
    toload.whnum = whnum
    toload.truckid = truck_id
    toload.shipid = package_id
    toload.seqnum = world_seq(toload)
    send_to_world(toload.seqnum, msg)
    modify_package_status(package_id, 4)
    # email to user to notify that their packages change status to PACKING
    # email_content = "Congratulations! Your package is being loaded on to a truck. Thanks for your patience."
    # receiver = get_user_email(package_id)
    # send_email(email_content, receiver, 'Your package status changes')


def world_loaded(loaded):
    if test:
        print("world_loaded")
    package_id = loaded.shipid
    # try:
    modify_package_status(package_id, 5)
    # email to user to notify that their packages change status to PACKING
    # email_content = "Congratulations! Your package has been loaded on to a truck. Thanks for your patience."
    # receiver = get_user_email(package_id)
    # send_email(email_content, receiver, 'Your package status changes')
    # # except (Exception, psycopg2.DatabaseError) as error:
    # # print(error)


# query the package details from the world
def world_queries(packageid):
    if test:
        print("world_queries")
    msg = amazon_world_pb2.ACommands()
    # msg.simspeed = SIMSPEED
    query = msg.queries.add()
    query.packageid = packageid
    query.seqnum = world_seq(query)
    send_to_world(query.seqnum, msg)  # ??


# disconnect with the world (optional)
def world_disconnect():
    if test:
        print("world_disconnect")
    msg = amazon_world_pb2.ACommands()
    msg.disconnect = True
    send_msg(WORLD_SOCKET, msg)  # ??


# This function is used to send ack to world to response world's command
def ack_to_world(seqnum):
    if test:
        print("ack_to_world")
    ack_command = amazon_world_pb2.ACommands()
    ack_command.acks.append(seqnum)
    send_msg(WORLD_SOCKET, ack_command)


def recv_world():
    if test:
        print("recv_world")
    response = amazon_world_pb2.AResponses()
    response.ParseFromString(recv_msg(WORLD_SOCKET))
    return response


########################################### end of communication with the world ##########################################


################################################ handle world #####################################################
# handle all kinds of received messages from World
def world_handler():
    if test:
        print("world_handler")
    while True:
        response = recv_world()
        print(response)
        for error in response.error:
            # send ack to world
            ack_to_world(error.seqnum)
            if error.seqnum in world_seqnum:
                continue
            else:
                world_seqnum.append(error.seqnum)
            print("world error: " + error.err)
        for ack in response.acks:
            # send ack to world
            world_ack.append(ack)
            print("************Received ack from world:" + str(ack))
        for bought in response.arrived:
            # send ack to world
            ack_to_world(bought.seqnum)
            if bought.seqnum in world_seqnum:
                continue
            else:
                world_seqnum.append(bought.seqnum)
            thread4 = threading.Thread(target=world_arrived, args=(bought,))
            thread4.start()
        for ready in response.ready:
            print("@@@@@@@@@@@@@ received pack finish from world")
            ack_to_world(ready.seqnum)
            if ready.seqnum in world_seqnum:
                continue
            else:
                world_seqnum.append(ready.seqnum)
            thread5 = threading.Thread(target=world_packed, args=(ready,))
            thread5.start()
        for loaded in response.loaded:
            ack_to_world(loaded.seqnum)
            if loaded.seqnum in world_seqnum:
                continue
            else:
                world_seqnum.append(loaded.seqnum)
            thread6 = threading.Thread(target=world_loaded, args=(loaded,))
            thread6.start()
        
        if response.finished == True:
            print("connection to world closed.")
            WORLD_SOCKET.close()
        # for package in response.packagestatus:
        #     modify_package_status(package.packageid, package.status)


################################################ handle world end #####################################################

########################################### communicate with ups ######################################################


def send_to_ups(seq, command):
    if test:
        print("send_to_ups")
    send_msg(UPS_SOCKET, command)
    while True:
        time.sleep(WAIT_TIME)
        if seq in ups_ack:
            break
        else:
            send_msg(UPS_SOCKET, command)


def is_packed(package_id):
    if test:
        print("is_packed")
    is_packed = True
    cur = conn.cursor()
    cur.execute(
        'SELECT status FROM mini_amazon_packages WHERE id = %s', (package_id, ))
    status = cur.fetchone()[0]
    conn.commit()
    cur.close()
    if status != 3:
        is_packed = False
    return is_packed


def get_user_email(package_id):
    if test:
        print("get_user_email")
    cur = conn.cursor()
    cur.execute(
        "SELECT email_address FROM mini_amazon_emails WHERE user_id = (SELECT user_id FROM mini_amazon_packages WHERE id = %s)", (package_id, ))
    user_email = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return user_email

# ATULoaded: for loop to query whether all packages with specific whid and truck_id are loaded and then decide to send ATULoaded


def loaded_to_ups(packages_id_list, truck_id):
    if test:
        print("loaded_to_ups")
    while True:
        if is_all_loaded(packages_id_list):
            # send message ATULoaded
            command = ups_amazon_pb2.ATUCommands()
            # command.simspeed = SIMSPEED
            # request_loaded_msg = command.loaded.add()
            request_loaded_msg = ups_amazon_pb2.ATULoaded()
            print("I am testing package id********************" + str(packages_id_list))
            for package_id in packages_id_list:
                print("I am testing package id::::::::::::::::::" + str(package_id))
                request_loaded_msg.packageid.append(package_id)
            # request_loaded_msg.packageid = packages_id_list
            request_loaded_msg.truckid = truck_id
            request_loaded_msg.seqnum = ups_seq(request_loaded_msg)
            command.loaded.append(request_loaded_msg)
            print(request_loaded_msg)
            print(command)
            send_to_ups(request_loaded_msg.seqnum, command)
            # send_msg(UPS_SOCKET, command)
            # recv ups ack
            ############################ TODO ###########################
            ############################ TODO ###########################
            break
        time.sleep(1)


# query whether all packages to deliver are loaded
def is_all_loaded(packages_id_list):
    if test:
        print("is_all_loaded")
    is_all_loaded = True
    for package_id in packages_id_list:
        cur = conn.cursor()
        cur.execute(
            'SELECT status FROM mini_amazon_packages WHERE id = %s', (package_id, ))
        status = cur.fetchone()[0]
        conn.commit()
        cur.close()
        if status != 5:
            is_all_loaded = False
    return is_all_loaded

# for a package with specific package_id, add truck_id data in database
def add_truck_id(package_id, truck_id):
    if test:
        print("add_truck_id")
    # try:
    cur = conn.cursor()
    cur.execute(
            'UPDATE mini_amazon_packages SET truck_id = %s WHERE id = %s', (truck_id, package_id))
    conn.commit()
    cur.close()
    # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)

# This function is used to send ack to ups to response ups's command
def ack_to_ups(seqnum):
    if test:
        print("ack_to_ups")
    ack_command = ups_amazon_pb2.ATUCommands()
    ack_command.acks.append(seqnum)
    send_msg(UPS_SOCKET, ack_command)

########################################### end of communicating with ups ######################################################

############################################# handle ups ###############################################################
# handle all kinds of received messages from UPS


def ups_handler():
    if test:
        print("ups_handler")
    while True:
        ups_res = ups_amazon_pb2.UTACommands()
        ups_res.ParseFromString(recv_msg(UPS_SOCKET))
        print("recv from UPS: "+str(ups_res))
        for error in ups_res.err:
            # send ack to world
            ack_to_ups(error.seqnum)
            if error.seqnum in ups_seqnum:
                continue
            else:
                ups_seqnum.append(error.seqnum)
            print("world error: " + error.err)
        for ack in ups_res.acks:
            ups_ack.append(ack)
            print("************Received ack from ups:" + str(ack))
        for arrive_truck_msg in ups_res.arrive:
            # 1. ack to ups:
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$ handle arrive of trucks")
            ack_to_ups(arrive_truck_msg.seqnum)
            if arrive_truck_msg.seqnum in ups_seqnum:
                continue
            else:
                ups_seqnum.append(arrive_truck_msg.seqnum)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$ handle arrive of trucks----")
            thread7 = threading.Thread(target=handle_truck_arrive, args=(arrive_truck_msg,))
            thread7.start()
        for out_delivery_msg in ups_res.todeliver:
            # 1. ack to ups:
            ack_to_ups(out_delivery_msg.seqnum)
            if out_delivery_msg.seqnum in ups_seqnum:
                continue
            else:
                ups_seqnum.append(out_delivery_msg.seqnum)
            thread8 = threading.Thread(target=handle_todeliver, args=(out_delivery_msg,))
            thread8.start()
        for delivered_msg in ups_res.delivered:
            # 1. ack to ups:
            ack_to_ups(delivered_msg.seqnum)
            if delivered_msg.seqnum in ups_seqnum:
                continue
            else:
                ups_seqnum.append(delivered_msg.seqnum)
            thread9 = threading.Thread(target=handle_delivered, args=(delivered_msg,))
            thread9.start()


def handle_delivered(delivered_msg):
    # 2. change packages' status to DELIVERED in database
    package_id = delivered_msg.packageid
    modify_package_status(package_id, 7)
    # email to user to notify that their packages change status to DELIVERED
    email_content = "Congratulations! Your package has been delivered. Thanks for your patience."
    receiver = get_user_email(package_id)
    send_email(email_content, receiver, 'Your package status changes')



def handle_todeliver(out_delivery_msg):
    # 2. change packages' status to DELIVERING in database
    package_id = out_delivery_msg.packageid
    # User can change address in UPS account:
    new_x = out_delivery_msg.x
    new_y = out_delivery_msg.y
    modify_dest_address(package_id, new_x, new_y)
    modify_package_status(package_id, 6)
    # email to user to notify that their packages change status to DELIVERING
    # email_content = "Congratulations! Your package is being delivered. Thanks for your patience."
    # receiver = get_user_email(package_id)
    # send_email(email_content, receiver, 'Your package status changes')

def handle_truck_arrive(arrive_truck_msg):
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$ handle arrive of trucks--99999--")
    # 2. add truck_id to these packages in database
    truck_id = arrive_truck_msg.truckid
    for package_id in arrive_truck_msg.packageid:
        add_truck_id(package_id, truck_id)
        # 3. handle the arrived truck: call load function
        #       send command to Warehouse: some packages with specific whid to load
        while True:
            # before sending load command to Warehouse, need to check whether this package is PACKED
            if is_packed(package_id):
                #  world_load(whnum, truck_id, package_id)
                world_load(arrive_truck_msg.whid, truck_id, package_id)
                break
            time.sleep(1)
    #       recv response from Warehouse: some packages with specific whid loaded
    # for loop to query
    # send ATULoaded message to ups
    loaded_to_ups(arrive_truck_msg.packageid, truck_id)


def modify_dest_address(package_id, new_x, new_y):
    cursor = conn.cursor()
    # get old address:
    #SELECT address_x, address_y FROM myapp_address 
    #WHERE id = (SELECT dest_address_id FROM myapp_packages WHERE id = <package_id>)
    cursor.execute("SELECT address_x, address_y FROM mini_amazon_address WHERE id = (SELECT dest_address_id FROM mini_amazon_packages WHERE id = %s)", (package_id, ))
    old_address = cursor.fetchone()
    old_x = old_address[0]
    old_y = old_address[1]
    # 1. check whether this address is in common used addresses
    cursor.execute("SELECT user_id FROM mini_amazon_packages WHERE id = %s", (package_id, ))
    row = cursor.fetchone()
    user_id = row[0]
    cursor.execute("SELECT * FROM mini_amazon_address WHERE user_id = %s AND address_x= %s AND address_y = %s", (user_id, new_x, new_y))
    rows = cursor.fetchall()
    # 2. if not, insert it
    if len(rows) == 0:
        # INSERT INTO Address (address_x, address_y, user_id) VALUES (123, 456, 789);
        cursor.execute("INSERT INTO mini_amazon_address (address_x, address_y, user_id, is_used) VALUES (%s, %s, %s, FALSE);", (new_x, new_y, user_id))
    # 3. if it is, do nothing
    # 4. Then change this package's dest_address to this new address
    cursor.execute("SELECT id FROM mini_amazon_address WHERE user_id = %s AND address_x= %s AND address_y = %s", (user_id, new_x, new_y))
    result = cursor.fetchone()
    new_address_id = result[0]
    cursor.execute("UPDATE mini_amazon_packages SET dest_address_id = %s WHERE id = %s", (new_address_id, package_id,))
    conn.commit()
    cursor.close()
    if old_x != new_x or old_y != new_y:
        # if dest address changes: email to user to notify that their packages change to a new dest address
        email_content = "The destination address of your package was changed in your linked UPS account. For the safety of your package, we remind you to pay attention to whether this change is from yourself."
        receiver = get_user_email(package_id)
        send_email(email_content, receiver, 'Your package destination changes')

############################################# handle ups end ###############################################################

########################################### handle web ###############################################################
# handle all packages with "BOUGHT" status
def web_handler():
    if test:
        print("web_handler")
    while True:
        # try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM mini_amazon_packages WHERE status = 1 AND is_processing = FALSE;")
        packages_bought = cursor.fetchall()
        for package_id in packages_bought:
            set_best_wh(package_id[0])
            cursor.execute(
                "SELECT warehouse_id FROM mini_amazon_packages WHERE id = %s;", (package_id[0], ))
            whnum = cursor.fetchone()[0]
            cursor.execute(
                "SELECT product_id_id FROM mini_amazon_packages WHERE id = %s;", (package_id[0], ))
            pd_id = cursor.fetchone()[0]
            cursor.execute(
                "SELECT id, description FROM mini_amazon_products WHERE id = %s;", (pd_id, ))
            things = cursor.fetchall()
            cursor.execute(
                "SELECT purchase_quantity FROM mini_amazon_packages WHERE id = %s;", (package_id[0], ))
            count = cursor.fetchone()[0]

            # 1. Let world buy
            world_buy(whnum, things, count)
            # Let this package become is_processing
            cursor.execute('UPDATE mini_amazon_packages SET is_processing = %s WHERE id = %s', (True, package_id[0]))

            # 2. Let UPS send a truck
            request_pickup(package_id[0], whnum)
            
            cursor.execute("SELECT description FROM mini_amazon_products WHERE id = %s;", (pd_id, ))
            description = cursor.fetchone()[0]
            while True:
                # Before sending world a command to pack this package, check whether there is sufficient inventory
                if is_enough_inventory(pd_id, whnum, count):
                    # 3. Let world pack
                    world_pack(whnum, pd_id, description, package_id[0], count)
                    break
                time.sleep(1)
        conn.commit()
        cursor.close()
        # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)


# Before sending world a command to pack a package, check whether there is sufficient inventory
def is_enough_inventory(product_id, warehouse_id, purchase_quantity):
    ans = False
    cur = conn.cursor()
    cur.execute("SELECT inventory_quantity FROM mini_amazon_inventories WHERE product_id = %s AND warehouse_id = %s;", (product_id, warehouse_id))
    row = cur.fetchone()
    inventory = row[0]
    if inventory >= purchase_quantity:
        ans = True
    conn.commit()
    cur.close()
    return ans


def set_best_wh(package_id):
    cur = conn.cursor()
    cur.execute("SELECT address_x, address_y FROM mini_amazon_address WHERE id = (SELECT dest_address_id FROM mini_amazon_packages WHERE id = %s);", (package_id, ))
    row = cur.fetchone()
    dest_x = row[0]
    dest_y = row[1]
    cur.execute("SELECT id, x, y FROM mini_amazon_warehouse;")
    rows = cur.fetchall()
    result_id = 0
    reslut_distance = sys.maxsize
    for row in rows:
        distance = math.sqrt(math.pow(row[1] - dest_x, 2) + math.pow(row[2] - dest_y, 2))
        if distance < reslut_distance:
            reslut_distance = distance
            result_id = row[0]
    cur.execute("UPDATE mini_amazon_packages SET warehouse_id = %s WHERE id = %s;", (result_id, package_id))
    conn.commit()
    cur.close()
    return



# get the nearest wh_id
def request_pickup(package_id, whnum):
    if test:
        print("request_pickup")
    # try:
        # ??????????
    command = ups_amazon_pb2.ATUCommands()
    # command.simspeed = SIMSPEED
    # msg.initwh.add(id=warehouse['id'], x=warehouse['x'], y=warehouse['y'])
    cur = conn.cursor()
    cur.execute("SELECT address_x, address_y FROM mini_amazon_Address WHERE id = (SELECT dest_address_id FROM mini_amazon_Packages WHERE id = %s);", (package_id, ))
    row = cur.fetchone()
    # destination = request_pickup_msg.destination.add()
    destination = ups_amazon_pb2.Desti_loc()
    destination.x = row[0]
    destination.y = row[1]
    request_pickup_msg = ups_amazon_pb2.ATURequestPickup(destination = destination)
    request_pickup_msg.whid = whnum
    request_pickup_msg.packageid = package_id
    # product_name, ups_account, destination (x, y), seqnum
    # ???? cur ?????
    cur.execute(
            "SELECT pdname FROM mini_amazon_products WHERE id = (SELECT product_id_id FROM mini_amazon_packages WHERE id = %s);", (package_id, ))
    request_pickup_msg.product_name = cur.fetchone()[0]
    cur.execute(
            "SELECT ups_name FROM mini_amazon_upss WHERE id = (SELECT ups_name_id FROM mini_amazon_packages WHERE id = %s);", (package_id, ))
    request_pickup_msg.ups_account = cur.fetchone()[0]
    request_pickup_msg.seqnum = ups_seq(request_pickup_msg)

    command.topickup.append(request_pickup_msg)
    print(request_pickup_msg)
    # # Let this package become is_processing
    # cur.execute(
    #     'UPDATE mini_amazon_packages SET is_processing = %s WHERE id = %s', (True, package_id))
    conn.commit()
    cur.close()
    send_to_ups(request_pickup_msg.seqnum, command)
    # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)

########################################### handle web end ###############################################################

########################################### handle subscribe from user ###############################################################
# send_email(email_content, receiver, subject)
def subscribe_handler():
    print("subscribe_handler")
    cursor = conn.cursor()
    old_product_id = 0
    while True: 
        cursor.execute("SELECT id FROM mini_amazon_products ORDER BY id DESC;")
        result = cursor.fetchall()
        if result:
            old_product_id = result[0][0]
            break
    while True:
        time.sleep(20)
        cursor.execute("SELECT id FROM mini_amazon_products ORDER BY id DESC;")
        result = cursor.fetchall()
        if result:
            new_product_id = result[0][0]
            while new_product_id != old_product_id and new_product_id > old_product_id:
                # we have new product in datatbase:
                cursor.execute("SELECT pdname, description, price FROM mini_amazon_products WHERE id = %s", [old_product_id+1])
                row = cursor.fetchone()
                email_content = f"We just launched a new product! Product Name: {row[0]} Product description: {row[1]} Product price: {row[2]} Discount price!"
                cursor.execute("SELECT email_address FROM mini_amazon_subscriber;")
                subscribers = cursor.fetchall()
                for subscriber in subscribers:
                    receiver = subscriber[0]
                    send_email(email_content, receiver, "Today's Newsletter")
                    time.sleep(5)
                old_product_id = old_product_id + 1
    cursor.close()

########################################### handle subscribe end ###############################################################



################################################# main #########################################################
if __name__ == "__main__":
    if test:
        print(11111111)
    # ? delete the data in tables but do not delete tables
    # 1. Connection:
    # UTAConnect: connect to UPS and receive world id (worldid)
    ups_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ups_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ups_socket.connect((UPS_HOST, UPS_PORT))
    UPS_SOCKET = ups_socket
    world_id = recv_world_id(UPS_SOCKET)
    # Connect to World (Warehouse) (port: 23456) and initialize warehouses of the world
    world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    world_socket.connect((WORLD_HOST, WORLD_PORT))
    WORLD_SOCKET = world_socket
    is_connect_world = conn_world(world_id)
    # AUConnected: tell UPS that amazon connect to world (Warehouse)
    if test:
        print(222222)
    if is_connect_world:
        # Make sure your result string is “connected!” before proceeding to any further actions.
        msg = ups_amazon_pb2.AUConnected()
        msg.worldid = world_id
        send_msg(ups_socket, msg)
        threads_list = []
        thread1 = threading.Thread(target=world_handler, args=())
        threads_list.append(thread1)
        thread2 = threading.Thread(target=ups_handler, args=())
        threads_list.append(thread2)
        thread3 = threading.Thread(target=web_handler, args=())
        threads_list.append(thread3)
        # handle Subscriber: Subscribers will receive email notifications whenever a new product is launched.
        subscribe_thread = threading.Thread(target=subscribe_handler, args=())
        threads_list.append(subscribe_thread)
        for thread in threads_list:
            thread.start()
        for thread in threads_list:
            thread.join()

    # finish. close the connection of database:
    conn.close()
    # finish. close email server:
    EMAIL_SERVER.quit()
