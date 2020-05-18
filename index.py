from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import BatchHttpRequest

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
    'https://www.googleapis.com/auth/classroom.coursework.me'
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
    elif(command == "lc" or command == "listcourses"):
        listCourses()
    elif(command == "la" or command == "listassignments"):
        listAssignmentsBatch()
    elif(command == "exit" or command == "x" or command == "stop"):
        exit(0)
    else:
        print(color.RED + "Unknown command \"" + command + "\"" + color.END)
        
    menu()

def help():
    print(color.BLUE + "classroom-cli v0.0.1 - help menu\n" + color.END + "h | Displays this menu\nlc | Lists courses that you are enrolled in\nla | Lists assignments that are due to be turned in\nstop | Closes the application")

def getCourses():
    if 'courses' in globals():
        return

    results = service.courses().list(pageSize=100).execute()
    global courses
    courses = results.get('courses', [])

def listCourses():
    getCourses()

    if not courses:
        print(color.RED + 'No courses found.' + color.END)
    else:
        print(color.BLUE + "Courses: (" + str(courses.__len__()) + ")" + color.END)
        for course in courses:
            print(course['name'])


def listAssignmentsBatch():
    print("Getting due assignments... this may take a moment depending on the number of courses")
    global courseWork
    courseWork = []

    global submissions
    submissions = []

    def courseWorkCallback(request_id, response, exception):
        if exception is not None:
            print('Error getting course: "{0}" {1}'.format(request_id, exception))
        else:
            courseWork.append(response) 

    def submissionsCallback(request_id, response, exception):
        if exception is not None:
            print('Error getting submission: "{0}" {1}'.format(request_id, exception))
        else:
            submissions.append(response) 

    getCourses()

    # Get courseWork
    courseWorkBatch = service.new_batch_http_request(callback=courseWorkCallback)
    for course in courses:
        request = service.courses().courseWork().list(courseId=course['id'])
        courseWorkBatch.add(request, request_id=course['id'])

    courseWorkBatch.execute()

    submissionsBatch = service.new_batch_http_request(callback=submissionsCallback)
    for work in courseWork:
        assignmentList = work.get('courseWork')

        # Get submisions
        for assignment in assignmentList:
            request = service.courses().courseWork().studentSubmissions().list(courseId=assignment['courseId'], courseWorkId=assignment['id'])
            submissionsBatch.add(request, request_id=assignment['id'])

    submissionsBatch.execute()

    print(color.BLUE + "Assignments: " + color.END)

    dueAssignments = []
    for submission in submissions:
        submission = submission.get('studentSubmissions')[0]
        if submission.get('courseWorkType') == 'ASSIGNMENT':
            if submission.get('state') != 'TURNED_IN' and submission.get('state') != 'RETURNED':
                dueAssignments.append(submission)
                for coursework in courseWork:
                    if coursework.get('courseWork')[0].get('id') == submission.get("courseWorkId"):
                        desc = ""
                        if len(coursework.get('courseWork')[0].get('description').split('\n')[0]) > 100:
                            desc = coursework.get('courseWork')[0].get('description').split('\n')[0][0:100] + "..."
                        else:
                            desc = coursework.get('courseWork')[0].get('description').split('\n')[0]
                        print(color.BOLD + "* " + coursework.get('courseWork')[0].get('title') + " (" + coursework.get('courseWork')[0].get('id') + ")\n  " + color.END + desc)

    print(color.BLUE + "Due: " + str(dueAssignments.__len__()) + color.END)

if __name__ == '__main__':
    initialize()

    student = service.userProfiles().get(userId="me").execute()
    name = student.get("name").get("fullName")

    print(color.GREEN  + color.BOLD + "You are logged in as " + name + color.END)

    menu()