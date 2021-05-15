#!env/bin/python3
import sys
import socket
import threading
import time
import signal
import argparse
import sqlite3
import parser
import rsa
import socks

class client:
    def __init__(self,ip='localhost',port='9999',mode='0'):
        #just to support srv variable
        self.clients = 1

        self.srv_info = [(ip,port)]
        self.name = input("Enter you username for session:")
        self.pubkey,self.privkey = rsa.newkeys(1024)

        if(mode=='tor'):
            self.cli = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            self.cli.set_proxy(socks.SOCKS5,"localhost",9050)
        elif(mode=='0'):
            self.cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.cli.connect((ip,port))
        except socket.gaierror as e:
            print("Error:",e)
            self.cli.close()
            sys.exit(1)

        signal.signal(signal.SIGINT, self.sighandler)

    def sighandler(self, signum, frame):

        print("Shutting down connection")
        self.cli.close()
        sys.exit(0)


    def snd_msg(self, msg):
        try:
            msg = rsa.encrypt(msg.encode('utf-8'),self.srv_info[2])
            x = self.cli.send(msg)
            
            return 1
        except socket.error as e:
            print("Error:",e)
            self.cli.close()
            sys.exit(1)


    def rcv_msg(self,name):
        while True:
            try:
                data = self.cli.recv(1024)
                if(len(data)!=0):
                    msg = rsa.decrypt(data,self.privkey)
                    msg = msg.decode('utf-8')
                    con2 = sqlite3.connect('amsg.db')
                    cur2 = con2.cursor()
                    cur2.execute('insert into chat(sender,msg,time) values(?,?,?)',(name,msg,time.ctime(time.time())))
                    con2.commit()

            except socket.error as e:
                print("Error:",e)
                self.cli.close()
                print("connection closed ):")
                return
            except KeyboardInterrupt:
                return 1



    def rcv_info(self):
        try:
            data = self.cli.recv(1024)
            if(len(data)!=0):
                data = str(data.decode('utf-8'))
                data = data.split(',')
                name = data[0]
                #srv_pubk = rsa.PublicKey(int(data[1]),int(data[2]))
                try:
                    con = sqlite3.connect('amsg.db')
                    cur = con.cursor()
                    cur.execute('insert into User(username,ip,status,join_time) values(?,?,?,?)',(name,self.srv_info[0][0],1,time.ctime(time.time())))
                    con.commit()
                    con.close()
                    print(name, "stored in db")
                    return data[0],data[1],data[2]
                except sqlite3.Error as e:
                    print("Error with in db:",e)
                    self.cli.close()
        except socket.error as e:
            print("Error occured",e,"No connecton established with",self.srv_info[0])
            self.cli.close()



    def snd_info(self):
        n = str(self.pubkey.n)
        e = str(self.pubkey.e)
        info = self.name+','+n+','+e
        try:
            self.cli.send(info.encode('utf-8'))
        except socket.error as e:
            print("Error with server:",e)
            self.cli.close()
            sys.exit(0)
        return 1


X = client(parser.ip, parser.port,parser.mode)
try:
    # rcv_msg from srv
    (name,n,e) = X.rcv_info()
    srv_pubk = rsa.PublicKey(int(n),int(e))
    X.srv_info.append(name)
    X.srv_info.append(srv_pubk)
    #snd info for srv
    p = X.snd_info()
    if (p and name):
        print("Connection successful with server")
    else:
        print("error")
    thread = threading.Thread(target=X.rcv_msg, args=[name])
    thread.start()

except Exception as E:
    print(E)
    print("Error occured within thread")
    sys.exit(1)
