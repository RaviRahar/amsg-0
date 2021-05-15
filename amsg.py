#!env/bin/python3
import parser
import time
import sys
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect,url_for
import threading

#App
amsg = Flask(__name__)

#Database
amsg.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amsg.db'
amsg.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(amsg)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    msg = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(40), default=time.ctime(time.time()))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False )
    ip = db.Column(db.String(70), nullable=False )
    join_time = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer, nullable=False)

@amsg.route("/refresh")
def manual_refresh():
    return redirect(url_for('msg_view'))

#
# @amsg.route("/contacts",methods=['POST','GET'])
# def contacts():
#     # + blacklist
#     return render_template('contacts.html',contacts = contacts)


@amsg.route('/',methods=['POST','GET'])
def msg_view():
    alert = ""
    if request.method == 'POST' :
        if 'msg' in request.form.keys():
            msg = request.form['msg']
            if(X.clients):
                if(len(msg.strip())!=0):
                    success = X.snd_msg(msg)
                    if success:
                        chat = Chat(sender='me',msg=msg)
                        db.session.add(chat)
                        db.session.commit()
                    else:
                        print("Error occured in sending msg")
                        print("Restart session")
                        sys.exit(0)
            else:
                alert = "No connected users"
    view = Chat.query.all()
    return render_template('msg.html', msgs=view,alert=alert)



db.create_all()

if parser.type=='srv':
    from amsg_srv import X
else:
    from amsg_cli import X


amsg.run(debug=True, port=5000,use_reloader=False)
time.sleep(5)
