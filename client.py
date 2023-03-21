import socket
import requests
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
    print(hostname)
    print(ip)
    print(port)
    exit = True
    while exit:
        actions = [{
            'type' : 'checkbox',
            'message' : 'What do you want to do',
            'name' : 'actions',
            'choices' : [
                Separator('<== Actions ==>'),
                {
                    'name':'Create a new transaction.'
                },
                {
                    'name':'View last transactions.'
                },
                {
                    'name':'Show wallet balance.'
                },
                {
                    'name':'Terminate client.'
                }
            ]
        }]

        action  = prompt(actions,style=style)['actions']
        
        if action[0] == 'Show wallet balance.':
            address = 'http://' + ip + ':' + port + '/money'
            response = requests.get(address)

            if response.status_code == 200:
                print("Current balance : " + str(response.json()['message']))
            else:
                print("Something went wrong")

        if action[0] == 'Terminate client.':
            exit = False


if __name__ == "__main__":
    parser = ArgumentParser(description="cli application")

    application()