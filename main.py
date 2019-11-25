from tkinter import *
import tkinter.messagebox
import sqlite3
import datetime
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
        c.execute("CREATE TABLE IF NOT EXISTS Accounts (UserID INTEGER PRIMARY KEY, Username varchar(16), Password varchar(16), IsAdmin BIT)") #Create table to hold account details

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
        self.current_user = current_user
        self.master.title(self.current_user)
        self.toolbar()
        self.colour_1 = "grey"
        c.execute("CREATE TABLE IF NOT EXISTS Catalogues (CatalogueID INTEGER PRIMARY KEY, CatalogueName TEXT, OwnerID INTEGER, DateCreated DATE, Archived BIT, FOREIGN KEY(OwnerID) REFERENCES Accounts(UserID))") #Create catalogues table and set UserID/OwnerID as foreign key
        c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, ItemName TEXT, Description TEXT, Catalogue TEXT, DateCreated DATE)")

        self.left_panel = Frame(self.master,bg=self.colour_1, highlightbackground="black", highlightthickness=1) #Creates two frames to fill the left and right of the window
        self.right_panel = Frame(self.master,bg="white", highlightbackground="black", highlightthickness=1)

        self.left_panel.grid(row=0,column=0, sticky='nsew')
        self.right_panel.grid(row=0,column=1, sticky='nsew')

        self.master.rowconfigure(0, weight=1) #Configure grid layout
        self.master.columnconfigure(0, weight=1, uniform="x")
        self.master.columnconfigure(1, weight=1, uniform="x")

        self.catalogue_list()
        self.catalogue_details()
        self.item_list()

    def create_ctlg_popup(self):
        popup_window = CreateCtlgPopup(self.master) #Creates popup window for new catalogue
        self.create_ctlg_btn["state"] = "disabled" 
        self.master.wait_window(popup_window.top) #Waits until popup is closed
        self.create_ctlg_btn["state"] = "normal"
        self.current_date = datetime.date.today().strftime('%d/%m/%y')
        if popup_window.value is not "":
            c.execute("SELECT UserID FROM Accounts WHERE Username = '"+self.current_user+"'")
            c.execute("INSERT INTO Catalogues (CatalogueName, OwnerID, DateCreated, Archived) VALUES(?,?,?,?)", (popup_window.value,c.fetchone()[0],self.current_date,0))
            con.commit() #Adds new catalogue to database with its name, date created, owner and its archive status
        """ self.indexes.configure(state=NORMAL)
        new_index = self.catalogue_listbox.size()+1
        self.indexes.insert(END, str(new_index)+"\n")
        self.catalogue_listbox.insert(new_index, self.popup_window.value)
        self.indexes.configure(height=new_index)
        self.catalogue_listbox.configure(height=new_index)
        self.indexes.configure(state=DISABLED) """
        self.update_catalogue_list()
    
    def create_item_popup(self):
        ctlg_selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0]
        popup_window = CreateItemPopup(self.master)
        self.create_item_btn["state"] = "disabled" 
        self.master.wait_window(popup_window.top)
        self.create_item_btn["state"] = "normal"
        self.current_date = datetime.date.today().strftime('%d/%m/%y')
        if popup_window.value is not "":
            c.execute("INSERT INTO Items (ItemName, Catalogue, Description, DateCreated) VALUES(?,?,?,?)", (popup_window.value[0], ctlg_selection, popup_window.value[1], self.current_date))
            con.commit()
        self.update_item_list()

    def catalogue_list(self):
        self.header_catalogues = Label(self.left_panel, text="Catalogues", font=("Helvetica", 54), bg=self.colour_1)
        self.indexes_catalogues = Text(self.left_panel, width=4, font=("Helvetica", 15), height=1, background=self.colour_1, borderwidth=0, highlightthickness=0)
        self.catalogue_listbox = Listbox(self.left_panel, selectmode=SINGLE, font=("Helvetica", 15), height=1, bg=self.colour_1, borderwidth=0, highlightthickness=0) #Create list box to hold catalogues
        self.update_catalogue_list() #Updates the index list as well as catalogues
        self.header_catalogues.grid(row=0, column=0, columnspan=2, sticky=W)
        self.indexes_catalogues.grid(row=1, column=0, sticky=N)
        self.catalogue_listbox.grid(row=1, column=1, sticky=NW)
        self.catalogue_listbox.configure(exportselection = False)
        """ c.execute("SELECT Catalogues.CatalogueName FROM Catalogues INNER JOIN Accounts ON Catalogues.OwnerID = Accounts.UserID WHERE Accounts.Username = '"+current_user+"'") #Select catalogue name and the owner's username
        result = c.fetchall()
        counter = 1
        for i in result: #Inserts catalogues owned by current user into the listbox
            self.catalogue_listbox.insert(counter, i)
            self.indexes.insert(END, str(counter)+"\n")
            self.indexes.configure(height=counter)
            self.catalogue_listbox.configure(height=counter)
            counter+=1
        self.header_catalogues.grid(row=0, column=0, columnspan=2)
        self.indexes.grid(row=1, column=0, sticky=N)
        self.catalogue_listbox.grid(row=1, column=1, sticky=NW)
        self.indexes.configure(state=DISABLED) """
        
        self.create_ctlg_btn = Button(self.left_panel,text="+", font=("Helvetica", 30), command=self.create_ctlg_popup, height = 1, width = 2, borderwidth=0, highlightthickness=0)
        self.delete_ctlg_btn = Button(self.left_panel, text="-", font=("Helvetica", 30), command=self.delete_ctlg, height = 1, width = 2, borderwidth=0, highlightthickness=0)
        self.create_ctlg_btn.grid(row=2, column=0)
        self.delete_ctlg_btn.grid(row=2, column=1, sticky=W)

    def item_list(self):
        self.header_items = Label(self.left_panel, text="Items", font=("Helvetica", 54), bg=self.colour_1)
        self.indexes_items = Text(self.left_panel, width=4, font=("Helvetica", 15), height=1, background=self.colour_1, borderwidth=0, highlightthickness=0)
        self.item_listbox = Listbox(self.left_panel, selectmode=SINGLE, font=("Helvetica", 15), height=1, bg=self.colour_1, borderwidth=0, highlightthickness=0) #Create list box to hold catalogues
        self.header_items.grid(row=0, column=2, sticky=W)
        self.indexes_items.grid(row=1, column=2, sticky=N)
        self.item_listbox.grid(row=1, column=3, sticky=NW)
        self.item_listbox.configure(exportselection = False)

        self.create_item_btn = Button(self.left_panel,text="+", font=("Helvetica", 30), command=self.create_item_popup, height = 1, width = 2, borderwidth=0, highlightthickness=0)
        self.delete_item_btn = Button(self.left_panel, text="-", font=("Helvetica", 30), command=self.delete_item, height = 1, width = 2, borderwidth=0, highlightthickness=0)
        self.create_item_btn.grid(row=2, column=2)
        self.delete_item_btn.grid(row=2, column=3, sticky=W)

    def update_item_list(self):
        self.indexes_items.configure(state=NORMAL)
        self.indexes_items.delete('1.0', END)
        self.item_listbox.delete(0, END)
        self.indexes_items.tag_configure("center", justify=CENTER)
        selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0]
        c.execute("SELECT ItemName FROM Items WHERE Catalogue = '"+selection+"'")
        result = c.fetchall()
        counter = 1
        for i in result:
            self.item_listbox.insert(counter, i)
            self.indexes_items.insert(END, str(counter)+"\n", "center")
            self.indexes_items.configure(height=counter)
            self.item_listbox.configure(heigh=counter)
            counter+=1
        self.indexes_items.configure(state=DISABLED)

    def update_catalogue_list(self):
        self.indexes_catalogues.configure(state=NORMAL) #Allow widget to be edited
        self.indexes_catalogues.delete('1.0', END) #Delete all contents from indexes and listbox
        self.catalogue_listbox.delete(0, END)
        self.indexes_catalogues.tag_configure("center", justify=CENTER)
        c.execute("SELECT Catalogues.CatalogueName FROM Catalogues INNER JOIN Accounts ON Catalogues.OwnerID = Accounts.UserID WHERE Accounts.Username = '"+self.current_user+"'") #Select catalogue name and the owner's username
        result = c.fetchall()
        counter = 1
        for i in result: #Inserts catalogues owned by current user into the listbox
            self.catalogue_listbox.insert(counter, i)
            self.indexes_catalogues.insert(END, str(counter)+"\n", "center")
            self.indexes_catalogues.configure(height=counter)
            self.catalogue_listbox.configure(height=counter)
            counter+=1
        self.indexes_catalogues.configure(state=DISABLED)
    
    def update_selected_catalogue(self):
        selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0] #Gets the catalogue that is selected
        self.catalogue_name.delete(0,50)
        self.catalogue_name.insert(0, selection)
        c.execute("SELECT DateCreated FROM Catalogues WHERE CatalogueName = '"+selection+"'")
        #self.date_created.configure(state=NORMAL)
        self.date_created.delete(0,50)
        self.date_created.insert(0, c.fetchone()[0])
        self.date_created.bind("<Key>", lambda e: "break")
        #self.date_created.configure(state=DISABLED)

    def catalogue_details(self):
        self.header_details = Label(self.right_panel, text="Details", font=("Helvetica", 54)) #Creating headers
        self.label_catalogue_name = Label(self.right_panel, text="Catalogue Name:")
        self.catalogue_name = Entry(self.right_panel) #Entry to hold catalogue details
        self.catalogue_name.insert(0, "-")
        self.label_date = Label(self.right_panel, text="Date Created:")
        self.date_created = Entry(self.right_panel)
        self.date_created.insert(0, "-")
        
        self.header_details.grid(row=0, column=0, columnspan=1)
        self.label_catalogue_name.grid(row=1, column=0, sticky=W)
        self.catalogue_name.grid(row=1, column=3, sticky=E)
        self.label_date.grid(row=2, column=0, sticky=W)
        self.date_created.grid(row=2, column=3, sticky=E)

        self.catalogue_listbox.bind("<ButtonRelease-1>", lambda e:[self.update_selected_catalogue(), self.update_item_list()]) #Updates catalogue details when selected

    def close_windows(self):
        self.master.quit()

    def toolbar(self):
        toolbar = Menu(self.master)
        self.master.config(menu=toolbar)

        #File Menu
        fileMenu = Menu(toolbar)
        toolbar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Exit", command=self.close_windows)
        #Catalogue
        catalogueMenu = Menu(toolbar)
        toolbar.add_cascade(label="Catalogue", menu=catalogueMenu)
        catalogueMenu.add_command(label="Create", command=self.create_ctlg_popup)
        catalogueMenu.add_command(label="Delete", command=self.delete_ctlg)
        #Item
        itemMenu = Menu(toolbar)
        toolbar.add_cascade(label="Item", menu=itemMenu)
        itemMenu.add_command(label="Create", command=self.create_item_popup)
        itemMenu.add_command(label="Delete", command=self.delete_ctlg)
        #User Menu
        userMenu = Menu(toolbar)
        toolbar.add_cascade(label="User", menu=userMenu)
        userMenu.add_command(label=self.current_user)
        userMenu.add_separator()
        userMenu.add_command(label="Preferences", command=self.user_preferences)

    def delete_ctlg(self):
        selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0]
        c.execute("DELETE FROM Catalogues WHERE CatalogueName = ?", (selection,)) #Delete selected catalogue from database
        con.commit()
        self.update_catalogue_list()
    
    def delete_item(self):
        selection = self.item_listbox.get(self.item_listbox.curselection()[0])[0]
        c.execute("DELETE FROM Items WHERE ItemName = ?", (selection,))
        con.commit()
        self.update_item_list()

    def user_preferences(self):
        pass

class CreateCtlgPopup(object):
    def __init__(self,master):
        top = self.top = Toplevel(master)
        top.title("Create Catalogue")
        self.info_label = Label(top,text="Catalogue Name: ")
        self.info_label.grid(row=0, column=0)
        self.ctlg_name_entry = Entry(top)
        self.ctlg_name_entry.grid(row=0, column=2, columnspan=2)
        self.create_ctlg_btn = Button(top,text='Create Catalogue',command=self.destroy_window)
        self.create_ctlg_btn.grid(row=2, column=2, sticky=W)
    def destroy_window(self):
        self.value = self.ctlg_name_entry.get()
        self.top.destroy()

class CreateItemPopup(object):
    def __init__(self,master):
        top = self.top = Toplevel(master)
        top.title("Create Item")
        self.info_label = Label(top, text="Item Name: ")
        self.info_label.grid(row=0, column=0)
        self.item_name_entry = Entry(top)
        self.item_name_entry.grid(row=0, column=1, columnspan=2)

        self.description_label = Label(top, text="Description: ")
        self.description_label.grid(row=1, column=0)

        self.description_entry = Entry(top)
        self.description_entry.grid(row=1, column=1, columnspan=2)

        self.create_ctlg_btn = Button(top,text='Create Item',command=self.destroy_window)
        self.create_ctlg_btn.grid(row=3, column=1, sticky=W)
    def destroy_window(self):
        self.value = [self.item_name_entry.get(), self.description_entry.get()]
        self.top.destroy()

root = Tk()
root.title("Login")
root.state('zoomed')
cls = LoginScreen(root)
root.mainloop()