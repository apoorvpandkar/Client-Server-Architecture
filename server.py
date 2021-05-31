# Name: Apoorv Pandkar
# Student Id: 1001553485

import os
import shutil
from socket import *
from threading import *
from tkinter import *
from dirsync import sync
from watchdog.events import PatternMatchingEventHandler #watcher
from watchdog.observers import Observer
import time


global client_list, server_log, top, server_frame, Server, identify_clients, identifier_list,project_dir, count
count = 0
client_list = []
client_names = {}
identify_clients = {}
identifier_list = []
project_dir = os.getcwd()
Server = os.path.join(project_dir,'Server')
operations = []

# https://pythonprogramming.net/python-binding-listening-sockets/
try:
    global host, port, s, print_to_server
    host = "127.0.0.1"
    port = 1710
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    # How many incoming connections we're willing to listen before denying
    s.listen(3)

except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()


# https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
def accept_clients():
    global clientname, server_log, server_frame

    while True:
        try:
            if len(client_list) <= 3:
                # Accept 3 clients only
                conn, address = s.accept()
                conn.send("Enter your name: ".encode())
                clientname = str(conn.recv(1024), "utf-8")  # Receive 1
                f1 = validate_username(clientname)
                while f1:
                    conn.send("Illegal characters, can't use digit".encode())
                    clientname = str(conn.recv(1024), "utf-8")
                    f1 = False
                else:
                    while True:
                        flag = True
                        # Check unique username
                        for cl in client_list:
                            if (cl == clientname):
                                flag = False
                        if flag == True:
                            client_list.append(clientname)
                            Thread(target=handle_client, args=(conn,)).start()  # calls the handle_client functions
                            break
                        if flag == False:
                            conn.send("Enter different username".encode())
                            clientname = conn.recv(1024).decode("utf-8")
                    client_names[conn] = clientname

            else:

                conn.send("Maximum connection reached".encode())
                print("Maximum connection reached")
                print_to_server("Maximum connection reached")
                conn.close()
                break
        except Exception as e:
            print_to_server("Client %s disconnected.." % clientname)

def handle_client(conn):

    try:
        global clientname, Server

        print(f"{clientname}- Using directory: {Server}")
        for clientName in client_list:
            print_to_server(f"Active clients: {clientName}")  # print clients connected to server
        message = "You have connected!!!"
        conn.send(message.encode())
        print_to_server(f"Client {clientname} has connected!!!")
        while True:
            clientname = client_names[conn]

            if clientname in client_names.values():
                if clientname in identify_clients.keys():
                    conn.send("You have already selected an identifier!".encode())
                    # identifier = identify_clients[clientname]
                    # path = os.path.join(Server,identifier)
                    # os.chdir(path)
                    # print(os.getcwd())
                else:
                    conn.send("Select an identifier A,B or C".encode())  # recv 3
                    identifier = conn.recv(1024).decode()
                    while identifier in identifier_list:
                        print("Duplicate identifier")
                        conn.send("Please choose different identifier".encode())
                        identifier = conn.recv(1024).decode()
                    else:
                        try:
                            if identifier == 'A':
                                identifier_list.append('A')
                                identify_clients[clientname] = identifier
                            elif identifier == 'B':
                                identifier_list.append('B')
                                identify_clients[clientname] = identifier
                            elif identifier == 'C':
                                identifier_list.append('C')
                                identify_clients[clientname] = identifier
                            else:
                                print("Invalid identifier")
                        except FileExistsError:
                            print("File already exists")

                conn.send("List of server directories:".encode())
                directories = os.listdir(Server)
                for directory in directories:
                    conn.send(f'{directory}\n'.encode())
                conn.send("Select Sync,create,move,etc".encode())
                data = conn.recv(1024).decode()
                if data == 'Create':
                    create_directory(conn)
                elif data == 'Delete':
                    delete_directory(conn)
                elif data == 'Move':
                    move_directory(conn)
                elif data == 'Rename':
                    rename_directory(conn)
                elif data == 'List':
                    list_directory(conn)
                elif data == 'Undo':
                    undo_operation(conn, clientname)
                elif data == 'Sync':
                    identifier=identify_clients[clientName]
                    sync_directory(conn,identifier)
                elif data == 'desync':
                    identifier = identify_clients[clientName]
                    desync_directory(conn,identifier)
                elif data == 'Disconnect':
                    client_list.remove(clientname)
                    print("Client %s has disconnected" % clientname)
                    print_to_server("Client Disconnected: %s" % clientname)
                    conn.close()

                else:
                    conn.send("Invalid input".encode())

                if len(client_list) == 0:
                    print_to_server("No active connection")
                    break
                else:
                    print_to_server(f"Active connections: {client_list}")
            else:
                print_to_server("Unknown client: Cannot accept more than 3 clients")
                break
    except Exception as e:
        print(f"Client's {clientname} :connection terminated {e}")
        # print_to_server(f"Client's {clientname} :connection terminated!!")

# Validate username: If username has digit in it do not allow the user
# https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
def validate_username(inputstring):
    return any(char.isdigit() for char in inputstring)

#http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
#https://www.michaelcho.me/article/using-pythons-watchdog-to-monitor-changes-to-a-directory
def watcher(source,target):
    global project_dir

    #Handle On any changes create,rename,delete,etc
    def on_any_event(event):
        #current_directory = f'{project_dir}/LD/{identifier}'
        source_path = source
        target_path = target
        sync(source_path, target_path, 'sync', purge=True, create=True)

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_any_event = on_any_event

    #Server directories path to observe
    path = f'{Server}'
    go_recursively = True
    global my_observer
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()

#https://www.instructables.com/Syncing-Folders-With-Python/
#https://stackoverflow.com/questions/54688687/how-to-synchronize-two-folders-using-python-script
def sync_directory(conn, identifier):
    try:
        global Server
        print(Server)
        conn.send("Enter directory name:".encode())
        dir_name = conn.recv(1024).decode()
        source_path = f'{Server}/{dir_name}'
        target_path = f'{project_dir}/LD/{identifier}/Copy_{dir_name}'
        sync(source_path, target_path, 'sync', purge=True, create= True)
        conn.send("Directory Synchronized Successfully\n".encode())
        #Monitor Changes to server based home directories
        Thread(target=watcher, args=(source_path,target_path)).start()
    except Exception as e:
            print_to_server(e)
            conn.send(e)

#https://linuxize.com/post/python-delete-files-and-directories/
def desync_directory(conn, identifier):

    global Server, project_dir
    conn.send("Enter directory name to desync:".encode())
    dir_name = conn.recv(1024).decode()
    dir_path = f'{project_dir}/LD/{identifier}/Copy_{dir_name}'

    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))
        print_to_server("Error: %s : %s" % (dir_path, e.strerror))



#https://stackoverflow.com/questions/37463569/extract-dict-value-from-list-of-dict
#https://stackoverflow.com/questions/2860153/how-do-i-get-the-parent-directory-in-python/29137365
#https://stackoverflow.com/questions/2860153/how-do-i-get-the-parent-directory-in-python/29137365
#https://stackoverflow.com/questions/42170411/tkinter-how-to-make-tkinter-text-widget-update

def undo_operation(conn, clientname):
    print("Undo opeartion")
    global Server, project_dir, operations
    conn.send("Select operation you want to undo".encode())
    op = conn.recv(1024).decode()

    if op == 'Create':
        conn.send("Undo create folder name".encode())
        dir_name = conn.recv(1024).decode() #Folder which you don't want to create
        dir_path = f'{Server}/{clientname}/{dir_name}'
        try:
            shutil.rmtree(dir_path) #Delete folder
            conn.send('Undo successful'.encode())
            # Remove child folders if parent folder deleted
            for i in operations:
                if i['operation'] == 'Create':
                    name  = i['Folder']
                    l1 = os.listdir(name)
                    for j in l1:
                        child = os.path.dirname(j) # Get parent directory
                        if child == name:
                            operations.remove({'operation':'Create','Folder':child})
                            print(operations)

            # Remove parent directory
            operations.remove({'operation':'Create', 'Folder': dir_name})
            print(operations)
            #write_to_file(operations)

        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))
            print_to_server("Error: %s : %s" % (dir_path, e.strerror))

    elif op == 'Move':
        conn.send("Undo move - Folder name:".encode())
        dir_name = conn.recv(1024).decode()
        for i in operations:
            if i['operation'] == 'Move':
                if i['Src_Folder'] == dir_name:
                    move = i['Dest_Folder']

        current_dir = os.path.join(Server, clientname, move)
        os.chdir(current_dir)
        temp_dir = os.path.join(Server,clientname)
        # Move back to the original folder
        shutil.move(dir_name, temp_dir)
        conn.send("Undo Move success".encode())
        # Remove entry from log
        operations.remove({'operation': 'Move', 'Src_Folder': dir_name,'Dest_Folder':move})
        print(operations)
        #write_to_file(operations)
        conn.send("Undo successful".encode())

    elif op == 'Delete':
        conn.send("Undo delete folder name:".encode())
        dir_name = conn.recv(1024).decode()
        path = os.path.join(Server, clientname, dir_name)
        os.makedirs(path)
        # Remove entry from log
        operations.remove({'operation': 'Delete', 'Folder': dir_name})
        print(operations)
        #write_to_file(operations)
        conn.send("Undo successful".encode())

    elif op == 'Rename':
        conn.send("Undo rename folder name:".encode())
        dir_name = conn.recv(1024).decode()
        for i in operations:
            if i['operation'] == 'Rename':
                if i['Dest_Folder'] == dir_name:
                    rename = i['Src_Folder']
        os.rename(dir_name, rename)
        # Remove entry from log
        operations.remove({'operation': 'Rename', 'Src_Folder': rename, 'Dest_Folder': dir_name})
        print(operations)
        #write_to_file(operations)
        conn.send("Undo successful".encode())
# https://www.geeksforgeeks.org/create-a-directory-in-python/
# Create directory
def create_directory(conn):
    try:
        print("Inside create")
        global Server, operations, count
        print("Count is:",count)
        clientname = client_names[conn]

        print(f"Parent dir: {Server}")
        conn.send("Enter new directory name: ".encode())
        new_dir = conn.recv(1024).decode()
        operations.append({'operation':'Create', 'Folder': new_dir})
        print(operations)
        #write_to_file(operations)
        path = os.path.join(Server, clientname, new_dir)
        print(f"path : {path}")
        os.makedirs(path)
        message = "Directory %s created" % new_dir
        print_to_server(f"Client {clientname}: {message}")
        conn.send(message.encode())

    except Exception as e:
        try:
            conn.send(f"Error creating directory.Error: {e}".encode())
            print_to_server(f"Error creating directory.Error: {e}")
        except:
            print(f"Something went wrong with {clientname}.")


# Delete directory
# https://stackoverflow.com/questions/6996603/how-to-delete-a-file-or-folder
def delete_directory(conn):
    try:
        print("Inside delete")
        global Server,operations
        clientname = client_names[conn]
        temp = clientname
        print(f"Parent directory {Server}")
        current_dir = os.path.join(Server, temp)
        print(f"Current directory {current_dir}")
        os.chdir(current_dir)  # Change directory
        conn.send("Enter which directory you want to delete?".encode())
        new_dir = conn.recv(1024).decode()
        path = os.path.join(current_dir, new_dir)
        print(f"Path : {path}")
        shutil.rmtree(path)
        print("Deleted %s directory" % new_dir)

        operations.append({'operation':'Delete','Folder': new_dir})
        print(operations)
        #write_to_file(operations)
        message = "Directory %s deleted" % new_dir
        print_to_server(f"Client {clientname}: Directory {new_dir} deleted")
        conn.send(message.encode())
    except Exception as e:
        try:
            conn.send(f"Delete Failed {e}".encode())
        except:
            print(f"Something went wrong with {clientname}.")


# Move directory
# https://www.geeksforgeeks.org/python-shutil-move-method/
def move_directory(conn):
    try:
        global Server
        clientname = client_names[conn]
        current_dir = os.path.join(Server, clientname)
        os.chdir(current_dir)
        print("Move directory")
        conn.send("Select which directory to move:".encode())
        src = conn.recv(1024).decode()
        conn.send("Select a directory to move file to:".encode())
        dest = conn.recv(1024).decode()
        shutil.move(src, dest)

        conn.send(f"Directory {src} has been moved to {dest}!!".encode())
        operations.append({'operation': 'Move', 'Src_Folder': src,'Dest_Folder':dest})
        print(operations)
        #write_to_file(operations)
        print_to_server(f"Client {clientname}: Directory {src} has been moved to {dest}!!")
    except Exception as e:
        try:
            conn.send("Error moving directory!")
        except:
            print(f"Something went wrong with {clientname}{e}.")


# Rename a directory
# https://www.tutorialspoint.com/python/os_rename.htm
def rename_directory(conn):
    try:
        print("Inside rename")
        global Server
        clientname = client_names[conn]
        print(f"Parent dir: {Server}")
        current_dir = os.path.join(Server, clientname)
        os.chdir(current_dir)
        conn.send("\n Enter filename you want to rename".encode())
        src = conn.recv(1024).decode()
        conn.send("Enter new filename: ".encode())
        dst = conn.recv(1024).decode()
        os.rename(src, dst)
        message = "Directory %s renamed to %s" % (src, dst)
        operations.append({'operation': 'Rename', 'Src_Folder': src, 'Dest_Folder': dst})
        print(operations)
        #write_to_file(operations)
        print_to_server(message)
        conn.send(message.encode())
    except Exception as e:
        try:
            conn.send(f"Error rename {e}".encode())
        except:
            print(f"Something went wrong with {clientname}.")


# List all directories
# https://www.educative.io/edpresso/how-to-list-files-in-a-directory-in-python
def list_directory(conn):
    try:
        global Server
        clientname = client_names[conn]
        current_dir = os.path.join(Server, clientname)
        print(f"Inside list dir: {current_dir}")
        list_all = os.listdir(current_dir)
        print(list_all)
        conn.send(f"List of directories for {clientname}".encode())
        for i in list_all:
            conn.send(f"{i}\n".encode())
    except Exception as e:
        try:
            print(e)
            conn.send("Error to list directories.".encode())
        except:
            print(f"Something went wrong with {clientname}")


# Print message to server log
def print_to_server(msg):
    global server_frame, server_log
    server_log.insert(END, "%s" % msg + "\n")
#
#
# def print_label(val):
#     global server_frame, Variable
#
#     Variable.set(val)
#     l1 = Label(server_frame, textvariable=Variable)
#     l1.pack()
#
# def update(l1):
#     global server_frame, Variable
#     with open("htfl.txt","w+") as f:
#
#         data = f.read()
#         f.close()
#         l1.config(text = data)
#     root.after(100000, update(l1))

# Stop server
def exit():
    os._exit(0)


# https://realpython.com/python-gui-tkinter/
def disp():
    # global server_log, top, server_frame
    global  root
    root = Tk()
    global server_log, top, server_frame, Variable
    Variable = StringVar()

    server_frame = Frame(
        root, bd=2, relief=SUNKEN, width=1020, height=700)

    server_frame.grid(row=0, column=0, sticky="nsew")

    # http://effbot.org/tkinterbook/label.htm
    server_label = Label(server_frame, text="Welcome to Server", font=('Helvetica', 18, 'bold'))
    server_label.grid(row=0, column=0, columnspan=2, sticky=E + W + N, pady=5, padx=5)

    server_log = Text(server_frame, height=25, width=50)
    server_log.grid(row=3, column=0, sticky="nsew", padx=2, pady=2)

    bar = Scrollbar(server_frame, command=server_log.yview)
    bar.grid(row=0, column=1, sticky='nsew')
    server_log['yscrollcommand'] = bar.set

    l1 = Label(server_frame)
    l1.grid(row=4, column = 1)
    #update(l1)
    root.mainloop()


def main():
    # Create a thread to display server GUI
    Thread(target=disp).start()
    accept_clients()


main()