import base64
import glob
import json
import os
import random
import shutil
import socket
import string
import struct
import sys
import threading
import time
import tkinter as tk
import tkinter.messagebox
from shutil import copyfile

import mysql.connector

import _thread

window = tk.Tk()
window.title("Sever")

try:
    mydb = mysql.connector.connect(host="localhost" , user="root" , password="" , database="dccn_final" )
    if mydb.is_connected():
        db_Info = mydb.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        mycursor = mydb.cursor()
        # mycursor = mydb.cursor(named_tuple=True)
        # cursor = d.cursor()
        mycursor.execute("select database();")
        record = mycursor.fetchone()
        print("You're connected to database: " , record)

except error as e:
    print("Error while connecting to MySQL", e)



# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# The client frame shows the client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 12345
client_name = " "
clients = []
clients_names = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT # code is fine without this
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)
        print("client added ")
        print(clients)

        # use a thread so as not to clog the gui thread
        threading._start_new_thread(send_receive_client_message, (client, addr))

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")
    
    return filename


    
    
# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
   

    while True:
        dataFromClient = client_connection.recv(900000)
        dataFromClient =dataFromClient.decode()
        dataFromClient = json.loads(dataFromClient)
        
        print('wait')


        print("data from client")
        print(dataFromClient)

        print("data type is ")
        print(type(dataFromClient))
        
        if (dataFromClient['request_type'] == "login"):
            print("request type is login")

            username = dataFromClient['message_content']['username']

            password = dataFromClient['message_content']['password']

            sql = "SELECT * from user WHERE username = %s AND password = %s"
            val = (username, password)

            mycursor.execute(sql, val)

            result = mycursor.fetchall()

            if (len(result) == 0):
                dataFromClient['message_content'] = "Please enter valid cridentials"
                dataFromClient['request_type'] = 'login_response'

                dataFromClient = json.dumps(dataFromClient)

                client_connection.send(dataFromClient.encode())

            elif (len(result) > 0 and username != ""):
                
                image_blob = result[0][3]
                image_path = ".\\" + "profile_image_" + str(username) + ".jpeg"
                return_path  = writeTofile(image_blob, image_path)
                
                
                dataFromClient['message_content'] = "success"
                dataFromClient['request_type'] = 'login_response'
                dataFromClient['result'] = return_path
                

                print("CLient name here is " + username)
            
                dataFromClient = json.dumps(dataFromClient)

                client_connection.send(dataFromClient.encode())

        elif (dataFromClient['request_type'] == "message"):


            if (dataFromClient['message_mode'] == "private"):


                sql = "INSERT INTO history (sender_name, reciever_name , message ) VALUES (%s, %s ,%s )"
                val = (dataFromClient['sender_name'], dataFromClient['reciever_name'], dataFromClient['message_content'])

                mycursor.execute(sql, val)

                mydb.commit()
                print(mycursor.rowcount, "record(s) affected")
                
                dataFromClient['request_type'] = "private message delievery"
                
                

                dataFromClient = json.dumps(dataFromClient)
                

                # client_connection.send(dataFromClient.encode())
                for c in clients:
                    if c != client_connection:
                        c.send(dataFromClient.encode())
                
            elif (dataFromClient['message_mode'] == "public"):
                print("Public chat requested by " + str(dataFromClient['sender_name']))
                dataFromClient['request_type'] = "public_message_delievery"
                dataFromClient = json.dumps(dataFromClient)
                for c in clients:
                    if c != client_connection:
                        c.send(dataFromClient.encode())
                        # dataFromClient

        elif (dataFromClient['request_type'] == "picture_upload"):
            # print("CLient name in picture upload is " + dataFromClient['sender_name'])
            with open(dataFromClient['message_content'], 'rb') as file:
                binaryData = file.read()

            # print(binaryData)

            try:
                sql = "UPDATE user SET picture = %s WHERE username = %s"
                val = (binaryData, dataFromClient['sender_name'])

                # print("CLient name in picture upload is " + dataFromClient['sender_name'])

                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record(s) affected")
                

            except mysql.connector.Error as error:
                print("Failed inserting BLOB data into MySQL table {}".format(error))
                dataFromClient['message_content'] = "Fail to insert your picture"

                dataFromClient['request_type'] = "picture_upload_response"
                # dataFromClient['file_name'] = "NO"

                dataFromClient = json.dumps(dataFromClient)

                client_connection.send(dataFromClient.encode())
                # print("sending  data to client in picture uplaod \n" + dataFromClient)

                

            dataFromClient['message_content'] = "success"

            dataFromClient['request_type'] = "picture_upload_response"

            dataFromClient = json.dumps(dataFromClient)

            print("sending  data to client in picture uplaod \n" + dataFromClient)

            client_connection.send(dataFromClient.encode())

        elif (dataFromClient['request_type'] == "search_history"):
            try:
                sql = "select * from history WHERE sender_name = %s AND reciever_name = %s"
                val = (dataFromClient['sender_name'],
                       dataFromClient['message_content'])
                mycursor.execute(sql, val)
                # Execute SQL Query to select all record
                print("I have executed  query ")
                result = mycursor.fetchall()
                print(result)
                  # fetches all the rows in a result set
                
                dataFromClient['request_type'] = "chat_history_response"
                
                if(len(result) != 0):
                    dataFromClient['result'] = result
                    dataFromClient = json.dumps(dataFromClient)
                    client_connection.send(dataFromClient.encode())
                else:
                    empty_list = []
                    dataFromClient['result'] = empty_list
                    dataFromClient['message_content'] = "no History found "
                    
                    dataFromClient = json.dumps(dataFromClient)
                    client_connection.send(dataFromClient.encode())
                

               
            except Exception as e:
                print(e)

                print('Error:Unable to fetch data.')
                # mysqldb.close()  # Connection Close

        elif (dataFromClient['request_type'] == "close_connection"):
            message = "user " + \
                dataFromClient['sender_name'] + \
                    "\t has gone offline and closed connection :("
            dataFromClient["message_content"] = message

            dataFromClient['request_type'] = 'broadcast'

            dataFromClient = json.dumps(dataFromClient)

            client_connection.send(dataFromClient)

            # stop thead here

        elif (dataFromClient['request_type'] == 'registration'):
            fullname = dataFromClient['message_body']['fullname']
            username = dataFromClient['message_body']['username']
            password = dataFromClient['message_body']['password']
            # filename = "sdhjsakhdkjas"
            # with open(filename, 'rb') as file:
                    # binaryData = file.read()
            
            sql = "INSERT INTO user (name , username , password ) VALUES (%s ,%s ,%s  )"
            val = (fullname, username, password,)
            mycursor.execute(sql, val)
            mydb.commit()
            print(mycursor.rowcount, "record(s) affected")

            dataFromClient['message_content'] = "success"

            dataFromClient['request_type'] == "signup_response"

            dataFromClient = json.dumps(dataFromClient)

            client_connection.send(dataFromClient.encode())

            # dataFromServer['request_type'] == "username_request" and dataFromServer['message_type'] == "send_username"

        elif (dataFromClient['request_type'] == "delete_profile" ):
            sql = "DELETE FROM user WHERE username = %s"
            val = (dataFromClient['sender_name'],)
            mycursor.execute(sql , val)

            mydb.commit()

            print(mycursor.rowcount, "record(s) deleted")
            dataFromClient['message_content'] = 'success'
            
            data = json.dumps(dataFromClient)
            
            client_connection.send(data.encode())
            
            # dataFromClient['request_type'] = "delete_profile_request"

        elif (dataFromClient['request_type'] == "update_nickname"):
            updated_name = dataFromClient['sender_name']
            sql = "UPDATE user SET username = %s  WHERE username = %s"
            val = (dataFromClient['message_content'],  dataFromClient['sender_name'],)
            mycursor.execute(sql , val)

            mydb.commit()

            print(mycursor.rowcount, "record(s) updated")
            dataFromClient['message_content'] = 'success'
            dataFromClient['sender_name'] = updated_name
            dataFromClient['request_type'] = "nickname_response"
            
            data = json.dumps(dataFromClient)
            
            client_connection.send(data.encode())
            
            # dataFromClient['request_type'] = "delete_profile_request"

        elif (dataFromClient['request_type'] == "update_password"):
            updated_name = dataFromClient['sender_name']
            sql = "UPDATE user SET password = %s  WHERE username = %s"
            val = (dataFromClient['message_content'],  dataFromClient['sender_name'],)
            mycursor.execute(sql , val)

            mydb.commit()

            print(mycursor.rowcount, "record(s) updated")
            dataFromClient['message_content'] = 'success'
            dataFromClient['request_type'] = "passowrd_response"
            # dataFromClient['sender_name'] = updated_name
            
            data = json.dumps(dataFromClient)
            
            client_connection.send(data.encode())
            
            # dataFromClient['request_type'] = "delete_profile_request"


        elif (dataFromClient['request_type'] == "search user"):
           print("in search box\n")
           sql = "SELECT name , username from user WHERE username LIKE %s OR name = %s  "
           username = dataFromClient['message_content']
           val = (username+"%", username+"%",)
           mycursor.execute(sql, val)
           result = mycursor.fetchall()

           print(result)

           if(len(result) <= 0):
               dataFromClient['message_content'] = "Sorry no user found :("
               dataFromClient['request_type'] = 'search_user_response'
               
               
               dataFromClient = json.dumps(dataFromClient)
               client_connection.send(dataFromClient.encode())
           
           else:
                dataFromClient['result'] = result
                dataFromClient['request_type'] = 'search_user_response'
                dataFromClient = json.dumps(dataFromClient)
                client_connection.send(dataFromClient.encode())

            #    print("result from server query ")
            #    print(result)

        elif(dataFromClient['request_type'] == "online user"):
            dataFromClient['result'] = user_online
            dataFromClient['request_type'] = 'online_user_response'
            dataFromClient['message_content'] = 'online user list'
            dataFromClient['reciever_name'] =  dataFromClient['sender_name']
            
            sql = 'SELECT name , username FROM user' 
            mycursor.execute(sql)
            
            
            dataFromClient = json.dumps(dataFromClient)
            client_connection.send(dataFromClient.encode())
            

def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()
