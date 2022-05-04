# StudySpot by Jason Inirio and Dasha Veraksa
# EC504 Final Project

import os, sys
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
import keyboard
from src.LocationsData import LocationsData
from src.Graph import Graph

# Constants
CITY = None
AMENITY = None
METHOD = None
LOCATION = None

def clearConsole():
    print("\033[H\033[J", end="") # clears console

def StudySpotPrompt():
    '''
    Shows the UI on Commandline
    Prompts user to input location information
    '''
    clearConsole()

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
            'name': 'location',
            'message': 'What is your current location? (please include full address, city, state/country)',
            'default': "8 St Mary's St, Boston, MA"
        },
        {
            'type': 'input',
            'name': 'city',
            'message': 'Where do you want to study?',
            'default': 'Boston'
        },
        {
            'type': 'list',
            'name': 'amenity',
            'message': 'Cafe or Library?',
            'choices': [
                Separator(),
                {
                    'name': 'Cafe',
                    'checked': True
                },
                {
                    'name': 'Library',
                    'disabled': ""
                },
            ],
        },
        {
            'type': 'list',
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
                }
            ],
        }
    ]

    answers = prompt(questions, style=style)
    return answers

def confirmationPrompt(target):
    # confirms if you want to go to this cafe, if not; refinds a new one
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
    questions = [
        {
            'type': 'confirm',
            'name': 'isConfirmed',
            'message': f"Is {target['name']} ok?",
            'default': True
        }
    ]

    answers = prompt(questions, style=style)
    return answers
    
def main():
    '''
    Main Program for StudySpot - EC504 Final Project
    By Jason Inirio & Dasha Veraska

    For more information and source code: https://github.com/jasoninirio/EC504-Final-Project
    '''

    answers = StudySpotPrompt()
    # clearConsole()
    print("Thank you for your response!")
    # clearConsole()
    print(answers)
    print("Starting StudySpot...")
    ld = LocationsData(answers['city'], answers['amenity'], answers['method'], answers['location'])
    print("Found potential spots! Now narrowing it down by preferences...")
    targetNode = ld.findLocalAmenity()
    # clearConsole()
    confirmation = confirmationPrompt(targetNode)

    while (not confirmation['isConfirmed']):
        targetNode = ld.findLocalAmenity(targetNode)
        if targetNode == None:
            print(f"No other amenities with the tag {answers['amenity']} :(")
            return
        confirmation = confirmationPrompt(targetNode)
    
    # after confirming, present information
    ld.createBBox(targetNode)
    ld.callOSM()

    # find best path to location
    studyGraph = Graph(ld.StudySpotGraph)
    target = studyGraph.findNearestNode(targetNode['latitude'], targetNode['longitude'])
    source = studyGraph.findNearestNode(ld.location[0], ld.location[1])

    print(source)
    print(target)
    path = studyGraph.Dijkstra(source, target)

    # print out html map for visualization
    print(path)
    ld.planRoute(path)

if __name__ == '__main__':
    main()