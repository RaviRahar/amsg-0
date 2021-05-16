#!env/bin/python3
import parser
import sys
import socket
import signal
import threading
import time
import argparse
import sqlite3
import rsa


class server:
    def __init__(self,ip='localhost',port='9999'):
        self.clients = {}
        self.recv_value = 0
        self.name = input("Enter you username for session:")
        self.pubkey,self.privkey = rsa.newkeys(1024)


        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind((ip,port))
        print('Server listening to port:',port)
        print("Address:",self.srv.getsockname())
        self.srv.listen()
        signal.signal(signal.SIGINT, self.sighandler)

    def sighandler(self, signum, frame):
        """ Clean up client outputs"""
        # Close the serverclient1'
        print ('Shutting down server')
        # Close existing client sockets
        for client in self.clients.keys():
            client.close()
        self.clients.clear()
        self.srv.close()
        sys.exit(0)
    def close_all(self):
        for client in self.clients.keys():
            print(".",end='')
            client.close()
        self.srv.close()
        sys.exit(0)





    def create_connections(self):
        while True:
            client, address = self.srv.accept()
            # sending& rcv info
            self.snd_info(client)
            (name,n,e) = self.rcv_info(client,address)
            cli_pubk = rsa.PublicKey(int(n),int(e))

            self.clients[client] = [address,cli_pubk, name]
            try:
                # rcv_msg from each connection
                thread1 = threading.Thread(target=self.rcv_msg, args=[client,name])
                thread1.start()

            except Exception:
                print("Error occured")
                self.close_all()
                return

    def snd_msg(self, msg):
        for client in self.clients.keys():
            try:
                msg = rsa.encrypt(msg.encode('utf-8'),self.clients[client][1])
                client.send(msg)
                return 1
            except socket.error as e:
                print("Error:",e)
                client.close()
                return 0



    def rcv_msg(self,client,name):
        while True:
            try:
                data = client.recv(1024)
                if(len(data)!=0):
                    # return data.decode('utf-8')
                    msg = rsa.decrypt(data,self.privkey)
                    msg = msg.decode('utf-8')
                    con1 = sqlite3.connect('amsg.db')
                    cur1 = con1.cursor()
                    cur1.execute('insert into chat(sender,msg,time) values(?,?,?)',(name,msg,time.ctime(time.time())))
                    con1.commit()
                    self.recv_value =1

            except socket.error as e:
                print("Error:",e)
                client.close()
                print("Connection closed")
                return 0

    def snd_info(self,client):
        n = str(self.pubkey.n)
        e = str(self.pubkey.e)
        info = self.name+','+n+','+e
        try:
            client.send(info.encode('utf-8'))
        except socket.error as e:
            print("Error with server:",e)
            client.close()
            self.close_all()
        return 0
    def rcv_info(self,client,address):
        #waiting to recieve client nickname
        try:
            data = client.recv(1024)
            if(len(data)!=0):
                data = str(data.decode('utf-8'))
                data = data.split(',')
                name = data[0]
                #cli_pubk = rsa.PublicKey(int(data[1]),int(data[2]))
                try:
                    con2 = sqlite3.connect('amsg.db')
                    cur2 = con2.cursor()
                    cur2.execute('insert into User(username,ip,status,join_time) values(?,?,?,?)',(name,address[0],1,time.ctime(time.time())))
                    con2.commit()
                    print(f"Connection established with {name}({address})")
                    return data[0],data[1],data[2]
                except sqlite3.Error as e:
                    print("Error with in db:",e)
                    self.close_all()
                    return


        except socket.error as e:
            print("Error occured",e,"No connecton established with",address)
            client.close()




X = server(parser.ip,parser.port)


try:
    thread = threading.Thread(target=X.create_connections)
    thread.start()
except Exception:
    print("Error occured")
    sys.exit(1)
