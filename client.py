# Name: Apoorv Pandkar
# Student Id: 1001553485

from socket import *
from tkinter import *
from threading import *

# Create socket connection
s = socket(AF_INET, SOCK_STREAM)
host = '127.0.0.1'
port = 1710
s.connect((host, port))

root = Tk()
root.title('Client')


# Get the user input and send  request to the server
def send_msg(event=None):
    try:
        message = client_input.get()
        s.send(bytes(message.encode()))
        client_input.set("")  # entry box is set to null every time message sent.\

    except Exception as e:
        print(e)

def receive_msg():
    while True:
        try:
            message = s.recv(1024).decode("utf-8")  # Receive messages from the server

            client_log.insert(END, "%s" % message + "\n")
        except OSError as msg:
            print(f"Connection terminated by the host..{msg}")
            break


def create_func(event=None):
    client_input.set("Create")
    send_msg()


def delete_func(event=None):
    client_input.set("Delete")
    send_msg()


def rename_func(event=None):
    client_input.set("Rename")
    send_msg()


def move_func(event=None):
    client_input.set("Move")
    send_msg()


def disconnect(event=None):
    client_input.set("Disconnect")
    send_msg()
    s.close()
    root.quit()

def sync_func(event=None):
    client_input.set("Sync")
    send_msg()

def list_func(event=None):
    client_input.set("List")
    send_msg()


client_frame = Frame(root, bg='#80c1ff', bd=2, width=400, height=150)
client_frame.grid(row=0, column=0)

client_log = Text(client_frame, height=20, width=80)
client_log.grid(row=0, column=0, rowspan=6, sticky="nsew", padx=2, pady=2)

bar = Scrollbar(client_frame, command=client_log.yview)
bar.grid(row=0, column=1)
client_log['yscrollcommand'] = bar.set

Create_btn = Button(client_frame, text='Create', command=create_func)
Create_btn.grid(row=0, column=1)

Delete_btn = Button(client_frame, text='Delete', command=delete_func)
Delete_btn.grid(row=3, column=1)

Rename_btn = Button(client_frame, text='Rename', command=rename_func)
Rename_btn.grid(row=1, column=1)

Move_btn = Button(client_frame, text='Move', command=move_func)
Move_btn.grid(row=2, column=1)

List_btn = Button(client_frame, text='List of files', command=list_func)
List_btn.grid(row=4, column=1)

Exit_btn = Button(client_frame, text='Disconnect', command=disconnect)
Exit_btn.grid(row=5, column=1)

Sync_btn = Button(client_frame, text='Sync', command=sync_func)
Sync_btn.grid(row=7, column=1)

Send_btn = Button(client_frame, text='Send', command=send_msg)
Send_btn.place(relx=0.7, relwidth=0.3, relheight=1)
Send_btn.grid(row=8, column=1)

# https://www.youtube.com/watch?v=7A_csP9drJw&t=336s
client_input = StringVar()
client_input.set("")
entry = Entry(client_frame, textvariable=client_input, font="times 15")
entry.bind("<Return>", send_msg)
entry.place(relwidth=0.65, relheight=1)
entry.grid(row=8, column=0)

Thread(target=receive_msg).start()  # calls the recieve function
root.mainloop()