import socket
import json
import requests
from initialize import boot
from pyfiglet import Figlet
from argparse import ArgumentParser
from PyInquirer import Token,prompt,style_from_dict,Separator

f = Figlet(font='slant')
print (f.renderText('Noobcash'))


style = style_from_dict({
    Token.Separator: '#CC5454 bold',
    Token.QuestionMark: '#673AB7 bold',
    Token.Selected: '#CC5454 bold',  # default
    Token.Pointer: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

def application():
    port = [{
        'type' : 'input',
        'name' : 'port',
        'message' : "What port of the node is the service using ?"
    }]
    hostname =  socket.gethostname()
    ip = socket.gethostbyname(hostname)
    port = str(prompt(port,style=style)['port'])
    #print(hostname)
    #print(ip)
    #print(port)
    exit = True
    while exit:
        if not boot:
            actions = [{
                'type' : 'checkbox',
                'message' : 'What do you want to do',
                'name' : 'actions',
                'choices' : [
                    Separator('\n<============ Actions ============>\n'),
                    {
                        'name':'Create a new transaction'
                    },
                    {
                        'name':'View last transactions'
                    },
                    {
                        'name':'Show wallet balance'
                    },
                    {
                        'name':'Help'  
                    },
                    {
                        'name':'Terminate client'
                    }
                ]
            }]

        else:
            actions = [{
                'type' : 'checkbox',
                'message' : 'What do you want to do',
                'name' : 'actions',
                'choices' : [
                    Separator('\n<============ Actions ============>\n'),
                    {
                        'name':'Create a new transaction'
                    },
                    {
                        'name':'View last transactions'
                    },
                    {
                        'name':'Show wallet balance'
                    },
                    {
                        'name':'Help'  
                    },
                    {
                        'name':'5 nodes experiment'
                    },
                    {
                        'name':'10 nodes experiment'
                    },
                    {
                        'name':"Dummy experiment"
                    },
                    {
                        'name':'Terminate client'
                    }
                ]
            }]

        action  = prompt(actions,style=style)['actions']
        
        if action[0] == 'Show wallet balance':
            address = 'http://' + ip + ':' + port + '/money'
            response = requests.get(address)

            if response.status_code == 200:
                print("Current balance : " + str(response.json()['message']))
            else:
                print("Something went wrong")

        if action[0] == 'View last transactions':
            address = 'http://' + ip + ':' + port + "/last_transactions"
            response = requests.get(address)
            if response.status_code == 200:
                print("Successfully retrieved the transactions of the node's most recent block.")
                for line in response.json():
                    print(line)
            else:
                print("Something went wrong")

        if action[0] == 'Create a new transaction':
            form = [
                {
                'type':'input',
                'name': 'id',
                'message': 'Select id'
                },
                {
                'type':'input',
                'name': 'amount',
                'message': 'Select amount'
                }
            ]

            content = prompt(form)
            #print(type(content['id']))
            #print(type(content['amount']))
            address = 'http://' + ip + ':' + port + '/transaction'
            response = requests.post(address,json=content)
            
            if response.status_code == 200:
                print('Transaction completed')

            if response.status_code == 400:
                print("Couldnt create transaction")

        if action[0] == 'Help':
            print("\n* Creating a new transaction will require from you to set a receiver and the amount to be sent.")
            print("\n* Viewing the last transactions will present to you the transactions of the latest block in the chain.")
            print("\n* Choosing the show wallet balance option will print how many coins are left in the wallet of the node.")
            print("\n* If you wish to terminate the app select the corresponding option.\n")

        if action[0] == '5 nodes experiment':
            address = 'http://' + ip + ':' + port + '/five_nodes'
            response = requests.get(address)

            if response.status_code == 200:
                 print("OK")

        if action[0] == '10 nodes experiment':
            address = 'http://' + ip + ':' + port + '/ten_nodes'
            response = requests.get(address)

            if response.status_code == 200:
                 print("OK")

        if action[0] == 'Dummy experiment':
            address = 'http://' + ip + ':' + port + '/temp'
            response = requests.get(address)

            if response.status_code == 200:
                 print("OK")
            

        if action[0] == 'Terminate client':
            exit = False


if __name__ == "__main__":
    parser = ArgumentParser(description="cli application")

    application()