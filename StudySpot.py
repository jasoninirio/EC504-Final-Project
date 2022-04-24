# StudySpot by Jason Inirio and Dasha Veraksa
# EC504 Final Project

import os, sys
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
import keyboard

CITY = None
AMENITY = None
METHOD = None

def cmd_ui():
    '''
    Shows the UI on Commandline
    Prompts user to input location information
    '''
    print("\033[H\033[J", end="") # clears console

    # TODO: set validators to check user answers

    # Colors and UI Style
    style = style_from_dict({
        Token.Separator: '#cc5454',
        Token.QuestionMark: '#673ab7 bold',
        Token.Selected: '#cc5454',  # default
        Token.Pointer: '#673ab7 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#f44336 bold',
        Token.Question: '',
    })

    # Question Prompt
    print('Study Spot by Jason & Dasha')
    questions = [
        {
            'type': 'input',
            'name': 'city',
            'message': 'Name your city',
            'default': 'Boston'
        },
        {
            'type': 'checkbox',
            'name': 'amenity',
            'message': 'Where you want to study?',
            'choices': [
                Separator(),
                {
                    'name': 'Cafe',
                    'checked': True
                },
                {
                    'name': 'Library'
                },
            ],
        },
        {
            'type': 'checkbox',
            'name': 'method',
            'message': 'What is your preferred method of transportation?',
            'choices': [
                Separator(),
                {
                    'name': 'Car',
                },
                {
                    'name': 'Bike'
                },
                {
                    'name': 'Walking',
                    'checked': True
                },
                {
                    'name': 'Public transportation'
                }
            ],
        }
    ]

    answers = prompt(questions, style=style)
    pprint(answers)
    for k in answers.keys():
        if k == 'amenity': AMENITY = answers[k]
        if k == 'city': CITY = answers[k]
        if k == 'method': METHOD = answers[k]
    
if __name__ == '__main__':
    # TODO: have an while True loop to improve reusability, 'q' key press would quit
    cmd_ui()