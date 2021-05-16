import argparse
parser = argparse.ArgumentParser(description="A-msg service (Encrypted messaging)")
parser.add_argument("--ip","-i", action="store", dest="ip", default="localhost",required=False,help="address of server")
parser.add_argument("--port","-p", action="store", dest="port",type=int,default=9999, required=False)
parser.add_argument("--type","-t", action="store", dest="type", required=True, help="srv/cli ")
parser.add_argument("--mode","-m",action="store", dest="mode",required=False,default='0',help="tor, while connecting to server using onion address")


given_args = parser.parse_args()
port = given_args.port
ip = given_args.ip
type = given_args.type
mode = given_args.mode
