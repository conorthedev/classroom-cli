from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
]

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def initialize():
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    global service
    service = build('classroom', 'v1', credentials=creds)

def menu():
    print(color.BOLD + "Type a command or use 'h' or 'help' for help" + color.END)
    parseCommand(input(color.BLUE + "> " + color.END))

def parseCommand(command):
    if(command == "h" or command == "help"):
        help()
    if(command == "lc" or command == "listcourses"):
        listCourses()
    if(command == "exit" or command == "x" or command == "stop"):
        exit(0)
        
    menu()

def help():
    print(color.BLUE + "classroom-cli v1.0 - help menu\n" + color.END + "h | Displays this menu\nlc | Lists courses that you are enrolled in\nstop | Closes the application")

def listCourses():
    results = service.courses().list(pageSize=100).execute()
    courses = results.get('courses', [])

    if not courses:
        print(color.RED + 'No courses found.' + color.END)
    else:
        print(color.BLUE + "Courses: (" + str(courses.__len__()) + ")" + color.END)
        for course in courses:
            print(course['name'])

if __name__ == '__main__':
    initialize()

    student = service.userProfiles().get(userId="me").execute()
    name = student.get("name").get("fullName")

    print(color.GREEN  + color.BOLD + "You are logged in as " + name + color.END)

    menu()