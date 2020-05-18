from utils import color, gclassroom

Classroom = gclassroom.Classroom() 
ClassroomHelper = gclassroom.ClassroomHelper(classroom=Classroom) 
Color = color.Color()

def help():
    print(Color.BLUE + "classroom-cli v0.0.1 - help menu\n" + Color.END + "h | Displays this menu\nlc | Lists courses that you are enrolled in\nla | Lists assignments that are due to be turned in\nstop | Closes the application")

def menu():
    print(Color.BOLD + "Type a command or use 'h' or 'help' for help" + Color.END)
    parseCommand(input(Color.BLUE + "> " + Color.END))

def parseCommand(command):
    if(command == "h" or command == "help"):
        help()
    elif(command == "lc" or command == "listcourses"):
        ClassroomHelper.listCourses()
    elif(command == "la" or command == "listassignments"):
        ClassroomHelper.listAssignmentsBatch()
    elif(command == "exit" or command == "x" or command == "stop"):
        exit(0)
    else:
        print(Color.RED + "Unknown command \"" + command + "\"" + Color.END)
        
    menu()

if __name__ == '__main__':
    Classroom.initialize()

    # pylint: disable=no-member
    student = Classroom.service.userProfiles().get(userId="me").execute()
    name = student.get("name").get("fullName")

    print(Color.GREEN  + Color.BOLD + "You are logged in as " + name + Color.END)

    menu()