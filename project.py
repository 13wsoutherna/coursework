from tkinter import * #Adds the tkinter library
import tkinter.messagebox
import sqlite3
sqlite_file = '/Users/adam/Documents/Python/Coursework Project/accounts.db'
con = sqlite3.connect(sqlite_file)
c = con.cursor()

class LoginScreen(Frame):
    def __init__(self, master):
        super().__init__(master)
        c.execute("CREATE TABLE IF NOT EXISTS Accounts (UserID INTEGER PRIMARY KEY, Username varchar(16), Password varchar(16))")

        self.usernameLabel = Label(self, text="Username:") #Creating labels for "Username" and "Password"
        self.passwordLabel = Label(self, text="Password:")
        self.userEntry = Entry(self) #Creating entry boxes to hold input
        self.passEntry = Entry(self, show="*") #Replaces password characters with *

        self.usernameLabel.grid(row=0, sticky=W) #Places each element
        self.passwordLabel.grid(row=1, sticky=W)
        self.userEntry.grid(row=0, column=1)
        self.passEntry.grid(row=1, column=1)

        self.buttonFrame = Frame(self)
        self.loginButton = Button(self.buttonFrame, text="LOGIN", command=self.login_btn, padx=10) #Runs login_btn when button clicked
        self.registerButton = Button(self.buttonFrame, text="REGISTER", command=self.register_btn, padx=10)
        self.loginButton.pack(side="left")
        self.registerButton.pack(side="right")
        self.buttonFrame.grid(row=3, column=1, columnspan=2, sticky="nesw")
        
        self.pack()
    
    def login_btn(self):
        username = self.userEntry.get() #Retrieves text from entry boxes
        password = self.passEntry.get()

        c.execute("SELECT Password FROM Accounts WHERE Username='" + username + "'")
        result = c.fetchone()
        print(result[0])
        if (password != result[0]):
            tkinter.messagebox.showwarning("Error", "Incorrect username or password")
        else:
            print("login successfull")
    
    def register_btn(self):
        username = self.userEntry.get()
        password = self.passEntry.get()
        c.execute("SELECT Username FROM Accounts WHERE Username='" + username + "'")
        selected_username = c.fetchone()
        print(selected_username)
        if selected_username:
            print("not available")
            tkinter.messagebox.showwarning("Error", "This username has already been taken")
        elif (not password):
            tkinter.messagebox.showwarning("Error", "Please enter a password")
        elif (len(username)>16 or len(password)>16):
            tkinter.messagebox.showwarning("Error", "Username and password must not exceed 16 characters")
        else:
            c.execute("INSERT INTO Accounts (Username, Password) VALUES(?,?)", (username, password))
            tkinter.messagebox.showinfo("Success", "The account with username: "+username+" has been successfully created")

        con.commit()

root = Tk()
lg = LoginScreen(root)
root.mainloop()