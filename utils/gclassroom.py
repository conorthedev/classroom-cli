from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# pylint: disable=import-error
from apiclient.http import BatchHttpRequest
from . import color, logger
Color = color.Color()
Logger = logger.Logger()

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
    'https://www.googleapis.com/auth/classroom.coursework.me'
]


class ClassroomHelper:
    gclassroom = None

    def __init__(self, classroom):
        self.gclassroom = classroom

    def getCourses(self):
        if 'courses' in globals():
            return

        results = self.gclassroom.service.courses().list(pageSize=100).execute()
        global courses
        courses = results.get('courses', [])

    def listCourses(self):
        self.getCourses()

        if not courses:
            Logger.error('No courses found!')
        else:
            Logger.notice("Courses: (" + str(courses.__len__()) + ")")
            for course in courses:
                print(course['name'])

    def listAssignmentsBatch(self):
        print("Getting due assignments... this may take a moment depending on the number of courses")
        global courseWork
        courseWork = []

        global submissions
        submissions = []

        def courseWorkCallback(request_id, response, exception):
            if exception is not None:
                Logger.error('Error getting course: "{0}" {1}'.format(
                    request_id, exception))
            else:
                courseWork.append(response)

        def submissionsCallback(request_id, response, exception):
            if exception is not None:
                Logger.error('Error getting submission: "{0}" {1}'.format(
                    request_id, exception))
            else:
                submissions.append(response)

        self.getCourses()

        # Get courseWork
        courseWorkBatch = self.gclassroom.service.new_batch_http_request(
            callback=courseWorkCallback)
        for course in courses:
            if 'ARCHIVED' not in course['courseState']:
                request = self.gclassroom.service.courses(
                ).courseWork().list(courseId=course['id'])
                courseWorkBatch.add(request, request_id=course['id'])

        courseWorkBatch.execute()

        submissionsBatch = self.gclassroom.service.new_batch_http_request(
            callback=submissionsCallback)
        for work in courseWork:
            assignmentList = work.get('courseWork')

            if not assignmentList:
                Logger.success("No assignments due!")
                return

            # Get submisions
            for assignment in assignmentList:
                request = self.gclassroom.service.courses().courseWork().studentSubmissions(
                ).list(courseId=assignment['courseId'], courseWorkId=assignment['id'])
                submissionsBatch.add(request, request_id=assignment['id'])

        submissionsBatch.execute()

        dueAssignments = []
        for submission in submissions:
            submission = submission.get('studentSubmissions')[0]
            if submission.get('courseWorkType') == 'ASSIGNMENT':
                if submission.get('state') != 'TURNED_IN' and submission.get('state') != 'RETURNED':
                    dueAssignments.append(submission)

        if dueAssignments == []:
            Logger.success("No assignments due!")
        else:
            Logger.notice("Assignments: ")
            for submission in dueAssignments:
                for coursework in courseWork:
                    if coursework.get('courseWork')[0].get('id') == submission.get("courseWorkId"):
                        desc = ""
                        if len(coursework.get('courseWork')[0].get('description').split('\n')[0]) > 100:
                            desc = coursework.get('courseWork')[0].get(
                                'description').split('\n')[0][0:100] + "..."
                        else:
                            desc = coursework.get('courseWork')[0].get(
                                'description').split('\n')[0]

                        Logger.info("* " + coursework.get('courseWork')[0].get(
                            'title') + " (" + coursework.get('courseWork')[0].get('id') + ")")
                        print("  " + desc)

            Logger.notice("Due: " + str(dueAssignments.__len__()))


class Classroom:
    service = None

    def initialize(self):
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

        self.service = build('classroom', 'v1', credentials=creds)
