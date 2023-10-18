
if __name__ == '__main__':
    import serial
    import time
    with serial.Serial('COM5', 115200) as port:
        print("I'm here!")
        port.write(b'AT\n')
        time.sleep(5)
        rcv = port.read_all()
        print(rcv)

        if 'OK' in str(rcv):
            port.write(b'AT+CUSD=1,"*105#",15\r\n')
            time.sleep(5)
            rcv = port.read_all()
            print(rcv)
            if 'OK' in str(rcv):
                port.write(b'AT+CUSD=1,"2",15\r\n')
                time.sleep(5)
                rcv = port.read_all()
                print(rcv)

                if 'OK' in str(rcv):
                    port.write(b'AT+CUSD=1,"1",15\r\n')
                    time.sleep(5)
                    rcv = port.read_all()
                    print(rcv)








if 'OK' in response:
                response = self.send_cmd('AT+CUSD=1,"*105#", 15')
                if 'OK' in response:
                    response = self.send_cmd('AT+CUSD=1,"7", 15')
                    if 'OK' in response:
                        response = self.send_cmd('AT+CUSD=1,"2", 15')
                        if 'OK' in response:
                            response = self.send_cmd('AT+CUSD=1,"1994", 15')
                            message = re.findall(r'\+CUSD: 1,"([.\w]*)"', response)

                            msg_splited = message.split('\n')
                            msg_splited.pop(0)
                            msg_splited.pop(len(msg_splited)-1)

                            for msg in msg_splited:
                                transaction = re.findall(r'(\d-)* (\d*) ([\w]*) (\d)*', msg)
                                if transaction:
                                    print(transaction)

                            """
                            if "#" in response:
                                response = self.send_cmd('AT+CUSD=1,"#", 15')
                                list_msg.append(re.findall(r'+CUSD: 1,"(.*)"', response))
                            """


                            