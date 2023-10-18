from utils_functions import *
import serial
import time
import datetime
import threading
import queue



class GSMThread(threading.Thread):
    TRANSACTIONS = []
    
    def __init__(self, port, baudrate):
        threading.Thread.__init__(self, daemon=True)
        self.module = ModuleGSM(port, baudrate)

    def run(self):
        self.module.main()
        print("We are finished the thread %s" % self.module._port)

    @classmethod
    def get_current_transactions(cls):
        return cls.TRANSACTIONS

    @classmethod
    def add_transactions(cls, transactions):
        for transaction in transactions:
            cls.TRANSACTIONS.append(transaction)


class ModuleGSM:
    used_port = set()

    def __init__(self, port, baudrate):
        if not (port in ModuleGSM.used_port):
            self._port = port
            self._baudrate = baudrate
            self._serial = self._open_port()
            self._serial.setDTR(0)
            self.prefix = None
            self.client = Client().client_login(username='leon', password='Leonadmin@1996')

        else:
            print("Ce port est déjà occupé!")

    def _open_port(self):
        try:
            ser = serial.Serial(self._port, self._baudrate, dsrdtr=False)
            if ser:
                ModuleGSM.add_port(self._port)
            return ser

        except serial.SerialException as e:
            print("Aucun Module n'est branché sur ce port")

    def _close_port(self):
        if self._serial:
            self._serial.close()

    def _setcmd(self, cmd, end='\r\n'):
        return (cmd + end).encode('latin-1')

    def _send_cmd(self, cmd, t=4, read=True):
        cmd = self._setcmd(cmd)
        self._serial.write(cmd)
        time.sleep(t) 
        if read:
            rcv = self._serial.read(self._serial.inWaiting())
            rcv = rcv.decode(encoding='latin-1')
            print(f"{self._port}: {cmd}", rcv, sep='----------------->')
            return rcv

    def send_cmd(self, cmd):
        a = self._send_cmd(cmd)
        return a

    def test_at(self):
        a = self.send_cmd('AT')
        if "OK" in a:
            return 1
        else:
            return 0

    def send_ussd(self, cmd, pos=None, ussd_str=[]):
        resp = None
        if self.test_at(pos=pos):
            for code in ussd_str:
                start = datetime.datetime.now()

                while (datetime.datetime.now() - start).total_seconds() < 10:
                    ussd_cmd = cmd.format(code)
                    resp = self.send_cmd(cmd=ussd_cmd, pos=pos)
                    print(resp)
                    if 'OK' in resp:
                        break
                if not resp:
                    break
        return resp

    def send_message(self, transaction, message):
        if not message:
            message = 'Hello World'
        t = transaction
        pk, phone = t
        rcv = self.send_cmd(MSG_FORMAT.format(phone))
        rcv = self.send_cmd(message)
        rcv = self.send_cmd('\x1A')
        print(rcv)
        # URL = PROTOCOL + DOMAINE_NAME + f'/payment/sim800l/{pk}/change/validated/transaction/'

        if 'OK' in rcv:
            # mis à jour de l'état de la transaction
            # Set is_terminated to value True
            #response = requests.get(URL + '&state=terminated')
            #if 'OK' in response.text:
            #    print('OK')

            #else:
            #    print('Bad requests')
            pass        

        else:
            # on remet la transaction en son état initial
            # Set in_processing to value False 
            # response = requests.get(URL + '&state=processing')
            pass

    def init_network_conf(self):
        
        # check network connection

        rcv = self.send_cmd('AT')
        print(rcv)

        if 'OK' in rcv:
            # set text mode
            rcv = self.send_cmd('AT+CMGF=1')
            if 'OK' in rcv:
                print("Text mode enabled!")
            rcv = self.send_cmd('AT+COPS?')
            
            if 'OK' in rcv:
                try:

                    operator_name = rcv.split(',')[2].strip().upper()
                    print(operator_name)
                except IndexError:
                    print("Impossible de détecter le réseau")
                    return False


                if 'LIBERTIS' in operator_name or 'MTN' in operator_name:
                    self.prefix = '06'
                    return True
                elif 'AIRTEL' in operator_name or 'ZAIN' in operator_name or 'CELTEL' in operator_name:
                    self.prefix = '05'
                    return True

                else:
                    return False
        return self.prefix

    def process_transactions(self):
        try:
            take_out_operation(self)
        except requests.exceptions.ConnectionError:
            pass
        except AssertionError:
            time.sleep(5)
            pass  
            
        
        conf_transaction = get_validated_transaction(client=self.client, pathname='/payment/sim800l/get/first/validated/transaction/')         
        check_confirmed_transaction(self)
        if not conf_transaction:
            self.send_message(conf_transaction)

    def main(self):
        at_result = False
        network_result = False

        while True:
            if not self._serial:
                print("Réinitialisation du port...")
                self.__init__(port=self._port, baudrate=self._baudrate)
                
            
            if not at_result:
                print("Teste de la commande AT")
                at_result = self.test_at()
                
                if at_result:
                    pass
                else:
                    continue

            if not network_result:
                print("Teste des paramètres réseaux")
                network_result = self.init_network_conf()
                
                if network_result:
                    pass
                else:
                    print("Echec des pramètres réseau")
                    continue 
                 
            if network_result:
                try:

                    self.process_transactions()
                    c = input("Entre A")
                except:
                    continue
    @classmethod
    def add_port(cls, port):
        cls.used_port.add(port)
        return len(cls.used_port)
    
    @classmethod
    def get_list_ports(cls):
        from serial.tools.list_ports import comports
        return [port.device for port in comports()]

    @classmethod
    def delete_port(cls, port):
        cls.used_port.remove(port)
        return len(cls.used_port)


if __name__ == '__main__':
    print(ModuleGSM.get_list_ports())
    list_thread = [GSMThread(port, 115200) for port in ModuleGSM.get_list_ports() if not (port in ModuleGSM.used_port)]
    smsthread = threading.Thread()

    for thread in list_thread:
        thread.start()
    
    for thread in list_thread:
        thread.join()

    

    smsthread.start()
    smsthread.join()

    print("Done.")

