# from Tkinter import *
import json
import socket
import string
import threading
import tkinter as tk
import tkinter.filedialog
from tkinter import *
from tkinter import messagebox, simpledialog

import mysql.connector
from PIL import Image, ImageTk
from tkcolorpicker import askcolor

window = tk.Tk()
window.title("Client")
username = " "




topFrame = tk.Frame(window)


lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
lblName = tk.Label(topFrame, text = "password:" ,).pack(side=tk.LEFT)
password_entry = tk.Entry(topFrame ,  show= '*')
password_entry.pack(side = tk.LEFT)
btnConnect = tk.Button(topFrame, text="Login", bg='brown',fg='white',  height=1, width=15, command=lambda : connect())
btnConnect.pack(side=tk.LEFT)

topFrame.pack(side=tk.TOP)
# entName = tk.Entry(topFrame)


search_value = tk.StringVar()
search_frame = tk.Frame(window)

# search_label = tk.Label(search_frame , text = "Search User " ).pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame , width = 50  , textvariable = search_value  )
search_entry.config(state = tk.DISABLED)
search_entry.pack(side=tk.LEFT)
search_button = tk.Button(search_frame , text="Search User " , bg='brown',fg='white',  height=1, width=15, command = lambda : search_user_request())
search_button.config(state = tk.DISABLED)
search_button.pack(side=tk.LEFT)
# search_button.config(text = "Search ")


search_frame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)


tkDisplay.insert(END , "Hello this is box to display message\n")



chat_option = tk.IntVar()
anotherFrame = tk.Frame(window)
tk.Label(anotherFrame, text="""Choose a chat mode:""" ,padx = 20).pack(side = tk.LEFT)
tk.Radiobutton(anotherFrame, text="public",padx = 20, variable=chat_option, value=1).pack(side = tk.LEFT)
tk.Radiobutton(anotherFrame,text="private",padx = 20,variable=chat_option,value=2).pack(side = tk.LEFT)

chat_option.set(1)
anotherFrame.pack()

message_value = tk.StringVar()

message_frame = tk.Frame(window)
message_entry = tk.Entry(message_frame , width = 50  , textvariable = message_value)
message_entry.config(state = DISABLED)
message_entry.pack(side = tk.LEFT)

send_button = tk.Button(message_frame , text = "Send" , bg='brown',fg='white',  height=1, width=15 , command = lambda : getChatMessage(message_entry.get()))
send_button.config(state = DISABLED)
send_button.pack(side = tk.LEFT)
# send_button.config(pady = 10)
message_frame.pack()


leftside_frame = tk.Frame(window)

upload_image_button = tk.Button(leftside_frame, height=2, width=15 ,bg='brown',fg='white', text="Upload" , command = lambda  : select_file_to_upload())
upload_image_button.pack(side = tk.LEFT)

# view_image_button = tk.Button(leftside_frame, text = "View Image" ,bg='brown',fg='white',  height=2, width=15 , command = lambda  : view_image()).pack(side = tk.LEFT)
change_background_button = tk.Button(leftside_frame, text = "Change bg colour" , bg='brown',fg='white' , height=2, width=15  , command = lambda : background_selection() )
change_background_button.pack(side = tk.LEFT)
view_chat_history = tk.Button(leftside_frame, text = "Sign up " ,bg='brown',fg='white',  height=2, width=15 , command = lambda  : sign_up())
view_chat_history.pack(side = tk.LEFT)
update_password_button = tk.Button(leftside_frame, text = "Update password" ,bg='brown',fg='white',  height=2, width=15 , command = lambda  : update_password())
update_password_button.pack(side = tk.LEFT)
update_nickname_button = tk.Button(leftside_frame, text = "Update NickName" ,bg='brown',fg='white',  height=2, width=15 , command = lambda  : update_nickname())
update_nickname_button.pack(side = tk.LEFT)
delete_profile_button = tk.Button(leftside_frame, text = "Delete Profile " ,bg='brown',fg='white',  height=2, width=15 , command = lambda  : delete_profile())
delete_profile_button.pack(side = tk.LEFT)


leftside_frame.pack()


load = Image.open("blank.jpg")
new_image = load.resize((50, 50))
render = ImageTk.PhotoImage(new_image)
img = Label(topFrame, image=render)
img.image = render
img.pack(side = tk.LEFT)


# password_entry.config(state  = tk.DISABLED)
# btnConnect.config(state=tk.DISABLED)
search_button.config(state = tk.DISABLED)
search_entry.config(state = tk.DISABLED)
update_nickname_button.config(state = tk.DISABLED)
update_password_button.config(state = tk.DISABLED)
upload_image_button.config(state = tk.DISABLED)
delete_profile_button.config(state = tk.DISABLED)





def background_selection():
            
        color_code = askcolor(color="red", parent=None, title=("Color Chooser"), alpha=False)
        window.configure(background = color_code[1])
        leftside_frame.configure(background_selection = color_code[1])
        message_frame.configure(background_selection = color_code[1])
        topFrame.configure(background_selection = color_code[1])



def connect():
    global username, client
    if (entName.get() == "" and password_entry.get() == ""):
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your name and Password")
    else:
        username = entName.get()
        connect_to_server(username , password_entry.get())



def connect_to_server(name, password):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 12345))
        message_body = {'username' : name , "password" : password}

        message_header = {'sender_name' : name , 'reciever_name' : None , 'message_type' : 'login' , 'message_content' : message_body , 'request_type' : 'login' , 'result' : None}

        from_server_string = json.dumps(message_header)
                
        client.send(from_server_string.encode()) # Send name to server after connecting

        
        
        
        

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")

def delete_profile():
    data = {'sender_name' :entName.get() , "request_type" : "delete_profile" , "message_content" : ""  }
    
    data = json.dumps(data)
    
    client.send(data.encode())

def search_user_request():
    
    if(search_value.get() != ""):

                search_message  = {'sender_name' :entName.get() , "request_type" : "search_history" , "message_content" : search_value.get() , 'result' : None }
                search_message = json.dumps(search_message)
                client.send(search_message.encode())
        
    else:
        tk.messagebox.showerror(title = "Empty value" , message="Please enter textfield to search user" )

def select_file_to_upload():
    file_name = tk.filedialog.askopenfilename(initialdir = "./", multiple = False , filetypes =(("Images", "*.jpeg"),))
    print(file_name)
    if file_name is not None: 

        print("\nUploading file: {}...".format(file_name))
        # with open(file_name, 'rb') as file:
            # binaryData = file.read()

        message_header = {'sender_name' : entName.get() , 'reciever_name' : None , 'file_name' : file_name , 'message_content' : file_name , 'request_type' : 'picture_upload' }

                                
        data_string = json.dumps(message_header)
        # client.send(data_string.encode());
        client.send(data_string.encode());
        
def popupmsg(msg):
    
    def select_file_to_upload():
        global file_name
        file_name = tk.filedialog.askopenfilename(initialdir = "./", multiple = False , filetypes =(("Images", "*.jpeg"),))
        print(file_name)
        if file_name is not None: 
            print("Please select file")
            
    popup = tk.Tk()
    popup.wm_title("!")
    label_0 = Label(popup, text="Registration form",width=30,font=("bold", 50))
    label_0.pack(ipady = 10 , pady = 10)


    label_1 = Label(popup, text="FullName",width=30,font=("bold", 10))
    label_1.pack( pady = 10)
    fullname_entry = Entry(popup ,  width = 50)
    fullname_entry.pack(ipady = 10 , pady = 10)
        
        
    label_2 = Label(popup, text="UserName",width=30,font=("bold", 10))
    label_2.pack( pady = 10)
    username_entry = Entry(popup ,  width = 50)
    username_entry.pack(ipady = 10 , pady = 10)
       
    label_4 = Label(popup, text="Password:",width=30,font=("bold", 10))
    label_4.pack( pady = 10)
    password_entry = Entry(popup ,  width = 50)
    password_entry.pack(ipady = 10 , pady = 10)
        
        # Button(popup, )
    Button(popup, text='upload picture',width=43,bg='brown',fg='white' , command = select_file_to_upload).pack(ipady = 10 , pady = 10)
        
    Button(popup, text='Submit',width=43,bg='brown',fg='white' , command = signup).pack()
    # Button(popup, text='Back',width=43,bg='brown',fg='white' , command = back).pack(ipady = 10 , pady = 10)
    
def sign_up():
    popupmsg("heello")
    
def recieve_online_user_response(from_server):
    tkDisplay.insert(END, "Result of User History of " + entName.get() + " and " + from_server['message_content'] + "\n")
    result = from_server['result']
    print(type(result))
    result_list = []
    if (len(from_server['result']) > 0):  
        for i in result:
            result_list.append(i[0])
            result_list.append(i[1])
            result_list.append(i[2])
            
            print("inside for loop of result")

            sender = result_list[0]
            reciever = result_list[1]
            message = result_list[2]
            # time = i[3]
            tkDisplay.insert(END , str(sender)   +"\tto\t" + str(reciever)  + "\t ->\t" + str(message), "tag_your_message") 
    else:
        tkDisplay.insert(END,from_server['message_content'] + "\n")
        

def receive_message_from_server(sck, m):
    index = 1
    while True:
        from_server = sck.recv(90000)
        
        from_server = json.loads(from_server)
        
        print(from_server)
        
        if (from_server['request_type'] == "login_response"):
             
            if (from_server['message_content'] =="success" ):    
                # controller.show_frame(AfterLoginPage)
                # btnConnect.config(state=tk.DISABLED)
                # tkMessage.config(state=tk.NORMAL)
                password_entry.config(state  = tk.DISABLED)
                btnConnect.config(state=tk.DISABLED)
                search_button.config(state = tk.NORMAL)
                search_entry.config(state = tk.NORMAL)
                update_nickname_button.config(state = tk.NORMAL)
                update_password_button.config(state = tk.NORMAL)
                upload_image_button.config(state = tk.NORMAL)
                delete_profile_button.config(state = tk.NORMAL)
                result = from_server['result']
                tkDisplay.config( state=tk.NORMAL)
                # password_entry.config(state  = tk.DISABLED)
                entName.config(state = tk.DISABLED)
                tk.messagebox.showinfo(title= from_server['message_content'] , message = from_server['message_content'])
            
                load = Image.open(str(from_server['result']))
                new_image = load.resize((50, 50))
                render = ImageTk.PhotoImage(new_image)
                img.configure( image=render)
                img.image = render
                message_entry.config(state = tk.NORMAL)
                send_button.config(state =tk.NORMAL)
                
                            
                        
            else:
                password_entry.config(state  = tk.NORMAL)
                btnConnect.config(state=tk.NORMAL)
                tk.messagebox.showinfo(title= from_server['message_content'] , message = from_server['message_content'])
                entName.config(state=tk.NORMAL)
                password_entry.config(state  = tk.NORMAL)
                # tk.messagebox.showinfo(title = "Account information invalid" , message = from_serverfrom_server['message_content'])

        
        elif(from_server['request_type'] == 'chat_history_response'):
                recieve_online_user_response(from_server)
            
            
        elif(from_server['request_type'] == "private message delievery"):
            # texts = tkDisplay.get("1.0", tk.END).strip()
            if(from_server['reciever_name'] == entName.get()): 
                # tkDisplay.insert(index.end, "Private message by " +  str(from_server['sender_name']) + "  ->>  " + str(from_server['message_content']), "tag_your_message")
                tkDisplay.insert(END, "\nPrivate message by " +  str(from_server['sender_name']) + "  ->>  " + str(from_server['message_content']))
                index = index + 3
            else:
                print("tera lia nahe aya theak hain ")
                
        elif(from_server['request_type'] =="public_message_delievery" ):
            print("In Public message delievery")
            print(from_server['message_content'])
            # texts = tkDisplay.get("1.0", tk.END).strip()
            # tk.update()
            # tkDisplay.insert(index.end ,"Public message by " + str(from_server['sender_name']) + "  ->>  " + str(from_server['message_content']), "tag_your_message")
            tkDisplay.insert(END ,"\nPublic message by " + str(from_server['sender_name']) + "  ->>  " + str(from_server['message_content']))
    # texts = tkDisplay.get("1.0", tk.END).strip()
            index = index + 3
    
                
        elif(from_server['request_type'] =='search_user_response'):
            recieve_search_response(from_server)
            
                
        elif(from_server['request_type'] =='picture_upload_response'):
            print("HI Picture uploaded")
            if(from_server['message_content'] == 'success'):
                print("IN success picture")
                tk.messagebox.showinfo(title = str(from_server['request_type']) , message = "Your picture with path "+ str(from_server['file_name'])  + " has been uploaded")
                load = Image.open(str(from_server['file_name']))
                new_image = load.resize((50, 50))
                render = ImageTk.PhotoImage(new_image)
                img.configure( image=render)
                img.image = render
                # img.pack(side = tk.LEFT)

                
                
        elif(from_server['request_type'] == "view_image_response"):
            recieve_view_image_response(from_server)
                
        elif(from_server['request_type'] =="delete_profile"):
            if(from_server['message_content'] == "success"):
                tk.messagebox.showinfo(title= "Success" , message="Your profile is deleted")
                search_button.config(state = tk.DISABLED)
                search_entry.config(state = tk.DISABLED)
                update_nickname_button.config(state = tk.DISABLED)
                update_password_button.config(state = tk.DISABLED)
                upload_image_button.config(state = tk.DISABLED)
                delete_profile_button.config(state = tk.DISABLED)
                entName.config(state = tk.NORMAL)
                password_entry.config(state = tk.NORMAL)
                btnConnect.config(tk.NORMAL)

        
            # recieve_chat_history_response(from_server)
       
    window.destroy()


def getChatMessage(msg):

    # msg = msg.replace('\n', '')
    # texts = tkDisplay.get("1.0", tk.END).strip()
    
    tkDisplay.config(state=tk.NORMAL)
    # if len(texts) < 1:
        # tkDisplay.insert(tk.END, entName.get() + " --> " + msg, "tag_your_message") # no line
    # else:
    tkDisplay.insert(END, "\n" + entName.get() + " -->> " + msg , "tag_your_message" )

    # tkDisplay.config(state=tk.DISABLED)
    
    if(chat_option.get() == 1):
        send_mssage_to_server(msg , "public")
    else:
        USER_INP = simpledialog.askstring(title="Reciever Name", prompt="Please enter reciever name?:")
        send_private_message(msg , "private" , USER_INP)
            


    # tkDisplay.see(tk.END)
        message_entry.delete('1.0', tk.END)


def send_mssage_to_server(msg , mode):
    data = {'sender_name' : entName.get(), 'reciever_name' : None , 'message_content' : msg , 'request_type' : 'message' , 'message_mode' : 'public'  }
    data = json.dumps(data)
    client.send(data.encode())
    print("Sending message")
    

def send_private_message(message , mode , reciever_name):
    data = {'sender_name' : entName.get(), 'reciever_name' : reciever_name , 'message_content' : message , 'request_type' : 'message' , 'message_mode' : 'private'  }
    data = json.dumps(data)
    client.send(data.encode())
    print("Sending private message to " + reciever_name)

window.mainloop()
