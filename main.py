from tkinter import *
import tkinter.messagebox
import sqlite3
sqlite_file = '/Users/adam/Documents/Python/Coursework Project/project.db'
con = sqlite3.connect(sqlite_file)
c = con.cursor()
current_user = "username1"
skip_login = True

class LoginScreen():
    def __init__(self, master):
        self.master = master
        if skip_login:
            self.switch_window()
        c.execute("CREATE TABLE IF NOT EXISTS Accounts (UserID INTEGER PRIMARY KEY, Username varchar(16), Password varchar(16))") #Create table to hold usernames and passwords

        self.usernameLabel = Label(master, text="Username:") #Creating labels for "Username" and "Password"
        self.passwordLabel = Label(master, text="Password:")
        self.userEntry = Entry(master) #Creating entry boxes to hold input
        self.passEntry = Entry(master, show="*") #Replaces password characters with *

        self.usernameLabel.grid(row=0, sticky=W) #Places each element using grid layout
        self.passwordLabel.grid(row=1, sticky=W)
        self.userEntry.grid(row=0, column=1)
        self.passEntry.grid(row=1, column=1)

        self.buttonFrame = Frame(master)
        self.loginButton = Button(self.buttonFrame, text="LOGIN", command=self.login_btn, padx=10) #Runs login_btn when button clicked
        self.registerButton = Button(self.buttonFrame, text="REGISTER", command=self.register_btn, padx=10) #Runs register_btn when clicked
        self.loginButton.pack(side="left")
        self.registerButton.pack(side="right")
        self.buttonFrame.grid(row=3, column=1, columnspan=2, sticky="nesw")
    
    def login_btn(self):
        global current_user
        username = self.userEntry.get() #Retrieves text from entry boxes
        password = self.passEntry.get()

        c.execute("SELECT Password FROM Accounts WHERE Username=? AND Password=?", (username, password)) #Querying for password of the username entered
        if c.fetchone() is not None:
            print("login successful")
            current_user = username
            self.switch_window() #If a password is returned from the query, the match is true and the main program will be shown
        else:
            tkinter.messagebox.showwarning("Error", "Incorrect username or password")
        
        """ result = c.fetchall()
        print(result)
        if (password != result[0] or result is None):
            tkinter.messagebox.showwarning("Error", "Incorrect username or password")
        else:
            print("login successful")
            self.switch_window() """
    
    def register_btn(self):
        username = self.userEntry.get()
        password = self.passEntry.get()
        c.execute("SELECT Username FROM Accounts WHERE Username='" + username + "'")
        selected_username = c.fetchone()
        if selected_username: #Testing each case of invalid usernames/passwords
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

    def switch_window(self): #Shows main window and removes LoginScreen from view
        self.master.withdraw()
        toplevel = Toplevel(self.master)
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        toplevel.geometry("%dx%d+0+0" % (w,h))
        app = MainProgram(toplevel)

class MainProgram:
    def __init__(self, master):
        self.master = master
        self.toolbar()
        c.execute("CREATE TABLE IF NOT EXISTS Catalogues (CatalogueID INTEGER PRIMARY KEY, CatalogueName TEXT, OwnerID INTEGER, DateCreated DATE, Archived BIT, FOREIGN KEY(OwnerID) REFERENCES Accounts(UserID))") #Create catalogues table and set UserID/OwnerID as foreign key

        self.left_panel = Frame(self.master,bg="grey", highlightbackground="black", highlightthickness=1) #Creates two frames to fill the left and right of the window
        self.right_panel = Frame(self.master,bg="white", highlightbackground="black", highlightthickness=1)

        self.left_panel.grid(row=0,column=0, sticky='nsew')
        self.right_panel.grid(row=0,column=1, sticky='nsew')

        self.master.rowconfigure(0, weight=1) #Configure grid layout
        self.master.columnconfigure(0, weight=1, uniform="x")
        self.master.columnconfigure(1, weight=1, uniform="x")

        self.catalogue_list()
        self.catalogue_details()

    def catalogue_list(self):
        global current_user
        self.header_catalogues = Label(self.left_panel, text="Catalogues:", font=("Helvetica", 54))
        self.listbox = Listbox(self.left_panel, selectmode=SINGLE) #Create list box to hold catalogues
        c.execute("SELECT Catalogues.CatalogueName FROM Catalogues INNER JOIN Accounts ON Catalogues.OwnerID = Accounts.UserID WHERE Accounts.Username = '"+current_user+"'") #Select catalogue name and the owner's username
        result = c.fetchall()
        counter = 1
        for i in result: #Inserts catalogues owned by current user into the listbox
            self.listbox.insert(counter, i)
            counter+=1
        self.header_catalogues.pack(side=TOP, anchor=W)
        self.listbox.pack(side=TOP, anchor=W)
    
    def update_selected_catalogue(self):
        self.selection = self.listbox.get(self.listbox.curselection()[0])[0]
        self.catalogue_name.delete(0,50)
        self.catalogue_name.insert(0, self.selection)
        c.execute("SELECT DateCreated FROM Catalogues WHERE CatalogueName = '"+self.selection+"'")
        self.date_created.delete(0,50)
        self.date_created.insert(0, c.fetchone()[0])

    def catalogue_details(self):
        global current_user
        self.header_details = Label(self.right_panel, text="Details", font=("Helvetica", 54))
        self.label_catalogue_name = Label(self.right_panel, text="Catalogue Name:")
        self.catalogue_name = Entry(self.right_panel)
        self.catalogue_name.insert(0, "-")
        self.label_date = Label(self.right_panel, text="Date Created:")
        self.date_created = Entry(self.right_panel)
        self.date_created.insert(0, "-")
        
        self.header_details.grid(row=0, column=0, columnspan=2)
        self.label_catalogue_name.grid(row=1, column=0, sticky=W)
        self.catalogue_name.grid(row=1, column=3, sticky=E)
        self.label_date.grid(row=2, column=0, sticky=W)
        self.date_created.grid(row=2, column=3, sticky=E)

        self.listbox.bind("<ButtonRelease-1>", lambda e:self.update_selected_catalogue())

    def close_windows(self):
        self.master.quit()

    def toolbar(self):
        global current_user
        toolbar = Menu(self.master)
        self.master.config(menu=toolbar)

        #File Menu
        fileMenu = Menu(toolbar)
        toolbar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Create", command=self.create_ctlg)
        fileMenu.add_command(label="Delete", command=self.delete_ctlg)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.close_windows)
        #User Menu
        userMenu = Menu(toolbar)
        toolbar.add_cascade(label="User", menu=userMenu)
        userMenu.add_command(label=current_user)
        userMenu.add_separator()
        userMenu.add_command(label="Preferences", command=self.user_preferences)  

    def create_ctlg(self):
        pass

    def delete_ctlg(self):
        pass

    def user_preferences(self):
        pass

root = Tk()
root.title("Login")
root.state('zoomed')
cls = LoginScreen(root)
root.mainloop()