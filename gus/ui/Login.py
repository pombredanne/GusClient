from gus.GusSession import GusSession
from Tkinter import *
import getpass

class Login:
    def __init__(self):
        self.username = None
        self.password = None
        self.token = None
        
    def prompt(self):
        if self.username is None or self.password is None or self.token is None:
            self.display()
            
    def get_username(self):
        self.prompt()
            
        return self.username
    
    def get_password(self):
        self.prompt()
        
        return self.password
    
    def get_token(self):
        self.prompt()
        
        return self.token


    
class GUILogin(Login):
    def display(self):
        root = Tk()
        root.title("Looks like you're not logged in yet...")
        root.geometry('600x200+100+100')
        session = GusSession()
        userbox = Entry(root)
        userbox.config(width=50)
        if session.load_user_name() is not None:
            userbox.insert(0, session.load_user_name())
        pwdbox = Entry(root, show = '*')
        pwdbox.config(width=50)
        tokenbox = Entry(root)
        tokenbox.config(width=50)
        if session.load_gus_token() is not None:
            tokenbox.insert(0, session.load_gus_token())
        
        def onenter(evt):
            for b in [userbox, pwdbox, tokenbox]:
                if b.get() == '':
                    b.focus()
                    return
            
            self.username = userbox.get()
            self.password = pwdbox.get()
            self.token = tokenbox.get()
            root.destroy()
        
        def onokclick():
            self.username = userbox.get()
            self.password = pwdbox.get()
            self.token = tokenbox.get()
            root.destroy()

        Label(root, text = 'GUS Username:').grid(row=0)
        userbox.grid(row=0, column=1)
        Label(root, text = 'GUS Password:').grid(row=1)
        pwdbox.grid(row=1, column=1)
        pwdbox.focus()
        Label(root, text = 'GUS Token:').grid(row=2)
        tokenbox.grid(row=2, column=1)
        
        if session.load_user_name() is None:
            userbox.focus()
        else:
            pwdbox.focus()
        
        root.bind('<Return>', onenter)
        Button(root, command=onokclick, text = 'OK').grid(row=3, column=1)
        root.attributes('-topmost', 1)
        root.focus()
        root.mainloop()

class CLILogin(Login):
    def display(self):
        print "Looks like you're not logged in yet..."
        
        session = GusSession()
        self.username = self.__prompt__('GUS Username', session.load_user_name())
        self.password = getpass.getpass('Please enter your GUS password: ')
        self.token = self.__prompt__('Security Token', session.load_gus_token())

    def __prompt__(self, prompt, default):
        if default is not None:
            default_prompt = ' [' + default + ']'
        else:
            default_prompt = ''
            
        return raw_input('Please Enter your %s%s: ' % (prompt, default_prompt)) or default


class Factory:
    def get_login(self, login_type='CLI'):
        if login_type == 'GUI':
            return GUILogin()
        else:
            return CLILogin()
    
