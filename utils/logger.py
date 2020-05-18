from . import color 
Color = color.Color()

class Logger:
    @staticmethod
    def info(message):
        print(Color.BOLD + message + Color.END)

    @staticmethod
    def error(message):
        print(Color.RED + message + Color.END)

    @staticmethod
    def notice(message):
        print(Color.BLUE + message + Color.END)

    @staticmethod
    def success(message):
        print(Color.GREEN + message + Color.END)
