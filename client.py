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
    
    port = prompt(port,style=style)['port']
    print(port)

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
            }
        ]
    }]

    action  = prompt(actions,style=style)['actions']
    print(action)


if __name__ == "__main__":
    parser = ArgumentParser(description="cli application")

    application()