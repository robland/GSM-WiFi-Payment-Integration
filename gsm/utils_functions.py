import requests
import time
import json
import re
        

DOMAINE_NAME = 'ec2-54-164-160-60.compute-1.amazonaws.com'
PROTOCOL = 'http://'
MSG_FORMAT = 'AT+CMGS="{0}"'

def get_validated_transaction(client, pathname):
    URL = PROTOCOL + DOMAINE_NAME + pathname
    response = client.get(URL)
    resp = response.json()
    try:
        resp = json.loads(resp)[0]
        return resp['pk'], resp['fields']
    except:
        None

def build_ussd(i, prefix=None):
    if prefix:
        if prefix == '06':
            return ['*105#', '2', '1', i[0]['fields']['profile'][0], i[0]['fields']['package'][0], '1994']
        elif prefix == '05':
            return ['*105#', '2', '1', i[0]['fields']['profile'][0], i[0]['fields']['package'][0], '1994']
    return None

def check_confirmed_transaction(obj):
    print('START TO CHECK TRANSACTION')
    if obj.prefix == '06':
        response = obj.send_cmd('AT+CUSD=2')
        for index, code in enumerate(['"*105#"', '"7"', '"2"', '"1994"']):
            response = obj.send_cmd(f'AT+CUSD=1,{code},15')
            time.sleep(2)
            if "OK" in response:
                if index == 3:
                    list_msg = re.findall(r'\+CUSD: 1,"([\s\-\w\'.:_,#]*)", 15', response)
                    try:
                        message = list_msg[0]
                    except IndexError:
                        # response = obj.send_cmd('AT+CUSD=2')
                        # print(response)
                        break


                    while ('#' in message):
                        response = obj.send_cmd('AT+CUSD=1,"#", 15')
                        print(response)
                        sub_string = re.findall(r'\+CUSD: 1,"([\s\-\w\'.:_,#\*]*)", 15', response)
                        print(sub_string)
                        try:
                            message += "\n" + sub_string[0]
                            if not ('#' in sub_string[0]):
                                break
                        except IndexError:
                            response = obj.send_cmd('AT+CUSD=2')
                            print(response)
                            break
                    print(message)
                    rows = message.split('\n')
                    print(rows)
                    new_message = ''

                    for row in rows:
                        if ('#' in row) or ('*' in row):
                            continue
                        else:
                            new_message += ' ' + row
                    print(new_message)
                    transactions = re.findall(r'([-\d]*) ([\d]*) ([\w]*) ([\d]*)', new_message)
                    for trans in transactions:
                        print(trans)
                        response = obj.client.get(f"{PROTOCOL}{DOMAINE_NAME}/payment/sim800l/add/transaction/{trans[0].strip()}/{trans[1].strip()}/{trans[2].strip()}/{trans[3].strip()}/")
                        print(response.status_code)
                        if response.status_code == '200':
                            print("Good!")
        else:
            pass
        
    elif obj.prefix == '05':
        pass                                    

def take_out_operation(obj):
    # Transaction format [{'model': 'manage_payment.subscription', 'pk': 450, 'fields': {'profile': ['064852080'], 'package': [300.0, 2]}}]
    url = f"{PROTOCOL}{DOMAINE_NAME}/payment/sim800l/get/transactions/{obj.prefix}/"
    i = json.loads(obj.client.get(url).json())
    print(i)
    assert len(i) > 0
    transaction = build_ussd(i, obj.prefix)
    print(transaction)
    # revoir le cas du None                
    pk = i[0]['pk']
    # obj.send_message(transaction=(pk, transaction[3]), message="Votre requete est en cours de traitement. \nVous recevrez une demande de confirmation dans les secondes qui suivent.")
    # response = obj.send_cmd('AT+CUSD=2')
    # print(response)
      
    for index, value in enumerate(transaction):
        response = obj.send_cmd('AT+CUSD=1,"%s",15' % value)    
        if "OK" in response:

            if "Fonds insuffisants" in response:
                obj.send_message(transaction=(pk, transaction[3]), message="Désolé cher client, Votre fonds est insuffisant. Veuillez recharger votre compte!")
            
            if index == len(transaction)-1:
                response = obj.client.get(f"{PROTOCOL}{DOMAINE_NAME}/payment/sim800l/update/transaction/{pk}/")
                if "OK" in response.text and response.status_code == '200':
                    obj.send_message(transaction, "Veuillez confirmer la transaction !")
                    # print(response)
            else: 
                continue
        else:
            print("We have a problème!")

            break

    

def create_account(obj):
    url = f"{PROTOCOL}{DOMAINE_NAME}/payment/sim800l/get/messages/"
    response_json = obj.client.get(url).json()
    messages = json.loads(response_json)

    for msg in messages:
        text_to_send = msg['fields']['message']
        list_string = text_to_send.split('\n')
        username = list_string[0].split(':')[1].strip()
        password = list_string[1].split(':')[1].strip()
        email = username + "@wesurf.com"

        response = obj.client.post(f"{PROTOCOL}{DOMAINE_NAME}/v1/wesurf/account/", username=username, email=email, password1=password, password2=password)        
        response = json.loads(response.json())
        token_response = json.loads(obj.client.post(f"{PROTOCOL}{DOMAINE_NAME}/v1/wesurf/token/validate/", token = response['token']).json())


        message_to_send = f"Votre compte wesurf a bien été créé!\nusername:{username}\npassword:{token_response['radius_user_token']}"
        text_response = obj.client.get(f"{PROTOCOL}{DOMAINE_NAME}/payment/sim800l/update/message/{msg['pk']}/")
        # Activation du token d'authentification
        obj.send_message(message_to_send)



class Client():
    def __init__(self):
        self.client = requests.session()
    
    def download_cookies(self, URL):
        self.client.get(URL)
        return self.client.cookies

    def client_login(self, login_url='/admin/login/', **data):
        url = PROTOCOL+DOMAINE_NAME
        login_url = url + login_url
        self.download_cookies(login_url)

        if 'csrftoken' in self.client.cookies:
            csrftoken = self.client.cookies['csrftoken']
        else:
            csrftoken = self.client.cookies['csrf']
        data.setdefault('csrfmiddlewaretoken', csrftoken)
        data.setdefault('next', '/admin')
        self.client.post(login_url, data=data)
        return self.client

if __name__ == '__main__':

    resp = get_validated_transaction(pathname="/payment/sim800l/get/first/validated/transaction/")
    print(resp)