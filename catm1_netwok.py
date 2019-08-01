from websocket import create_connection
import websocket
import socket
import paramiko
import sys
import time
sys.stdout.flush()

## EDIT SSH DETAILS ##

ssh = ''
SSH_COMMAND = "echo 'Echo Back Success'"

#M1 Settings
nutaq_path = "Desktop/StkTool/CAT-M1/"
m1_path_mme = '(cd Desktop/StkTool/CAT-M1/; sudo -S ./launch_epc.sh "R1804")'
m1_path_enb = '(cd Desktop/StkTool/CAT-M1/; sudo -S ./launch_enb.sh "R1804")'

#NB1 Settings
nb1_nutaq_path = "Desktop/StkTool/NB1/"
nb1_path_mme = '(cd Desktop/StkTool/NB1/; sudo -S ./launch_epc.sh "R1804")'
nb1_path_enb = '(cd Desktop/StkTool/NB1/; sudo -S ./launch_enb.sh "R1804")'
ssh_stdin = ssh_stdout = ssh_stderr = None

class WSNoConnectError(Exception):
    """
    websocket connection error class
    """
    pass


class Nutaq():
    def __init__(self, host, user, password, mme_port, enb_port, network):
        self.host = host
        self.user = user
        self.password = password
        self.mme_port = mme_port
        self.enb_port = enb_port
        self.network = network
        
        print("\n") 
        print(self.host)
        print(self.user)
        print(self.password)
        print(self.mme_port)
        print(self.enb_port)
        print(self.network)
        sys.stdout.flush()  
        
    def ssh_connect(self):
        try:        
            self.ssh = paramiko.SSHClient()
            #print('Calling paramiko')
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.host, username=self.user, password=self.password)
            print('Connection Established')
            sys.stdout.flush()
        
        except Exception as e:
            print('Connection Failed')
            print(e)
            sys.stdout.flush()
            
    def ssh_close(self):
        if(self.ssh != None):
            self.ssh.close()
            print('Connection close')
            sys.stdout.flush()
            
    def ssh_command(self):
        stdin, stdout, stderr = self.ssh.exec_command(SSH_COMMAND)
        print(stdout.read())
        
    def run_mme(self):
        try:
            self.sock_address = (self.host, self.mme_port)
            print("sock address is ")
            print(self.sock_address)
            
            self.sock = socket.socket()
            self.sock.connect(self.sock_address)
            
            if self.sock:
                print("Configurations already loaded on nutaq")
                self.sock.close()
                del self.sock
                self.connect_mme_enb_sockets()
                self.stop_mme_enb()

        except socket.error:
            print("Configurations are not loaded on nutaq, system is ready to start mme and enb")

	if self.network == "M1":
            mme_stdin, mme_stdout, mme_stderr = self.ssh.exec_command(m1_path_mme)
	elif self.network == "NB1":
            mme_stdin, mme_stdout, mme_stderr = self.ssh.exec_command(nb1_path_mme)
	else:
            #Default CAT-M1 network
            mme_stdin, mme_stdout, mme_stderr = self.ssh.exec_command(m1_path_mme)

        time.sleep(5)
        mme_stdin.write('nutaq\n')
        mme_stdin.flush()
        print("waiting 15 seconds to start MME properly ")
        sys.stdout.flush()
        time.sleep(15)


    def run_enb(self):
        try:
            if self.network == "M1":
                mme_stdin, mme_stdout, mme_stderr = self.ssh.exec_command(m1_path_enb)
            elif self.network == "NB1":
                mme_stdin, mme_stdout, mme_stderr = self.ssh.exec_command(nb1_path_enb)
            else:
                #Default CAT-M1 network
                mme_stdin, mme_stdout, mme_stderr = self.ssh.exec_command(m1_path_enb)

            time.sleep(5)
            mme_stdin.write('nutaq\n')
            mme_stdin.flush()
            print("waiting 20 seconds to start ENB properly ")
            sys.stdout.flush()
            time.sleep(20)
			
        except Exception as e:
            sys.stderr.write("ENB start up exception: {0}".format(e))
            sys.stdout.flush()


    def connect_mme_enb_sockets(self):
        try:
            print("Try in the connect_mme_enb_sockets")
            print("*********************************")
            print("---------------------------------")
            self.mme_socket = self.config_connect(self.mme_port)
            print("++++++++++++++++++++++++++++++++++")
            self.enb_socket = self.config_connect(self.enb_port)
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print("Configuration Loaded Successfully")
            sys.stdout.flush()
        
        except Exception as e:
            raise WSNoConnectError("Unable to connect with MME and ENB sockets: {0}".format(e))
            sys.stdout.flush()


    def stop_mme_enb(self):
        try:
            self.send_custom(self.mme_socket, '{\"message\": \"quit\"}')
            self.send_custom(self.mme_socket, '{\"message\": \"quit\"}')
            print("Adding wait of 10 seconds to make sure ENB and MME closed properly")
            sys.stdout.flush()
            time.sleep(10)
        
        except Exception as e:
            raise WSNoConnectError("Unable to stop MME and ENB: {0}".format(e))
            sys.stdout.flush()

        
    def config_connect(self, port):
        try:
            websocket.enableTrace(False)
            self.ws_handle = create_connection("ws://" + self.host + ":" + str(port), timeout=3)
            return self.ws_handle

        except Exception as e:
            raise WSNoConnectError("Unable to connect to WebSocket host: " + e.message)

    def send_custom(self, handle, command):
        handle.send(command)
        output = handle.recv()
        return output
                
if __name__ == '__main__':

    host = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    mme_port = int(sys.argv[4])
    enb_port = int(sys.argv[5])
    network = sys.argv[6]
    executionTime = int(sys.argv[7])
    executionTime = executionTime*60

    print("host name: ", host) 
    print("user name: ", user) 
    print("password: ", password) 
    print("mme_port: ", mme_port) 
    print("enb_port: ", enb_port) 
    print("network: ", network)
    print("Timeout : ", executionTime) 
    print("\n")    
    
    Nutaq_Handler = Nutaq(host, user, password, mme_port, enb_port, network)
    Nutaq_Handler.ssh_connect()
    Nutaq_Handler.ssh_command() # Check SSH connection
    print("SSH connection successfull")
    sys.stdout.flush()

    Nutaq_Handler.run_mme()
    Nutaq_Handler.run_enb()
    Nutaq_Handler.connect_mme_enb_sockets()

    if network == "M1":
        print("CAT-M1 Network Running . . .")
    elif network == "NB1":
        print("NB-IoT Network Running . . .")
    else:
        print("CAT-M1 Network Running . . .")

    sys.stdout.flush()
    time.sleep(executionTime)
            
    Nutaq_Handler.stop_mme_enb()
    print("CAT-M1 Stop")
    sys.stdout.flush()
        
    Nutaq_Handler.ssh_close()
