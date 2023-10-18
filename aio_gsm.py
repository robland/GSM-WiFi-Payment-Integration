import serial
import time
import datetime
import threading
import queue


class GSMThread(threading.Thread):
    TRANSACTIONS = []

    def __init__(self, port, baudrate, prefix):
        threading.Thread.__init__(self)
        self.module = ModuleGSM(port, baudrate, prefix)

    def run(self):
        m = self.module._port
        print("We are starting the thread %s" % m)
        # Here is my function
        self.module.get_queue_list(raw_transactions=GSMThread.TRANSACTIONS)
        self.module.process_queue_transactions()
        print("We are finished the thread %s" % m)

    @classmethod
    def get_current_transactions(cls):
        return cls.TRANSACTIONS

    @classmethod
    def add_transactions(cls, transactions):
        for transaction in transactions:
            cls.TRANSACTIONS.append(transaction)


class ModuleGSM:
    used_port = set()

    def __init__(self, port, baudrate, prefix):
        self.list_queue = queue.Queue()
        if not (port in ModuleGSM.used_port):
            self._port = port
            self._baudrate = baudrate
            self._serial = self._open_port()
            self._prefix = prefix
        else:
            print("Ce port est déjà occupé!")

    def _open_port(self):
        try:
            ser = serial.Serial(self._port, self._baudrate)
            if ser:
                ModuleGSM.add_port(self._port)
            return ser

        except serial.SerialException as e:
            print("Aucun Module n'est branché sur ce port")

    def _close_port(self):
        if self._serial:
            self._serial.close()

    def _setcmd(self, cmd, end='\r\n', pos=None):
        if pos is not None:
            return str(pos) + "@" + cmd + end
        else:
            return cmd + end

    def _send_cmd(self, cmd, t=5, pos=None, read=True):
        cmd = self._setcmd(cmd, pos=pos)
        print(cmd)
        time.sleep(1)
        self._serial.setDTR(0)
        time.sleep(1)
        self._serial.write(cmd.encode())
        if read:
            time.sleep(t)
            rcv = self._serial.read(self._serial.inWaiting())
            rcv = rcv.decode(encoding='latin-1')
            return rcv

    def send_cmd(self, cmd, pos=None):
        a = self._send_cmd(cmd, pos=pos)
        return a

    def test_at(self, pos=None):
        a = self.send_cmd("AT", pos=pos)
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

    def process_queue_transactions(self):
        while True:
            try:
                transaction = self.list_queue.get(block=False)
                print(transaction)

            except queue.Empty:
                return
            else:
                response = self.send_cmd("AT", 1)
                if "OK" in response:
                    response = self.send_cmd('AT+CUSD=1,"%s",15' % transaction[0], 1)
                    print(response)

                    if "OK" in response:
                        response = self.send_cmd('AT+CUSD=1,"%s",15' % transaction[1], 1)
                        print(response)

                        if "OK" in response:
                            response = self.send_cmd('AT+CUSD=1,"%s",15' % transaction[2], 1)
                            print(response)

                            if "OK" in response:
                                response = self.send_cmd('AT+CUSD=1,"%s",15' % transaction[3], 1)
                                print(response)

                                if "OK" in response:
                                    response = self.send_cmd('AT+CUSD=1,"%s",15' % transaction[4], 1)
                                    print(response)

                                    if "OK" in response:
                                        response = self.send_cmd('AT+CUSD=1,"%s",15' % transaction[5], 1)
                                        print(response)
                                        response = self.send_cmd('AT+CMGF=1', 1)
                                        print(response)
                                        if "OK" in response:
                                            print('Text mode set!')
                                            if "OK" in response:
                                                # response = self.send_cmd('AT+CMSS="ALL"', 1)
                                                print("I will send you a message")






                else:
                    print("Impossible de se connecter au module")

    def get_queue_list(self, raw_transactions):
        for i in raw_transactions:
            if i[3].startswith(self._prefix):
                self.list_queue.put(i)
            else:
                continue

    @classmethod
    def add_port(cls, port):
        cls.used_port.add(port)
        return len(cls.used_port)

    @classmethod
    def delete_port(cls, port):
        cls.used_port.remove(port)
        return len(cls.used_port)


if __name__ == '__main__':
    GSMThread.add_transactions(transactions=[
        ["*105#", "2", "1", "054852080", "20", "1994"],
        ["*105#", "2", "1", "064852080", "20", "1994"],
        ["*105#", "2", "1", "050828274", "20", "1994"]
    ])

    thread1 = GSMThread("COM5", 115200, '06')
    thread2 = GSMThread("COM9", 115200, '05')
    thread3 = GSMThread("COM10", 115200, '04')
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

    print("Done.")

