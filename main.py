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
        self.right_panel_state = True
        self.master.protocol("WM_DELETE_WINDOW", self.close_windows)
        c.execute("CREATE TABLE IF NOT EXISTS Catalogues (CatalogueID INTEGER PRIMARY KEY, CatalogueName TEXT, OwnerID INTEGER, DateCreated DATE, Archived BIT, FOREIGN KEY(OwnerID) REFERENCES Accounts(UserID))") #Create catalogues table and set UserID/OwnerID as foreign key
        c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, ItemName TEXT, Description TEXT, Catalogue TEXT, DateCreated DATE)")

        self.left_panel = Frame(self.master,bg="grey", highlightbackground="black", highlightthickness=1) #Creates two frames to fill the left and right of the window
        self.right_panel = Frame(self.master,bg="white", highlightbackground="black", highlightthickness=1)

        self.left_panel.grid(row=0,column=0, sticky='nsew')
        self.right_panel.grid(row=0,column=1, sticky='nsew')

        self.master.rowconfigure(0, weight=1) #Configure grid layout
        self.master.columnconfigure(0, weight=1, uniform="x")
        self.master.columnconfigure(1, weight=1, uniform="x")
        self.catalogue_list()
        self.catalogue_details()
        self.item_list()
        self.catalogue_listbox.bind("<ButtonRelease-1>", lambda e:[self.catalogue_details(), self.update_selected_catalogue(), self.update_item_list()]) #Updates catalogue details when selected
        self.item_listbox.bind("<ButtonRelease-1>", lambda e:[self.item_details(), self.update_selected_item()])

    def item_details(self):
        self.right_panel_state = False #Flag used to distinguish between the catalogue details and an item's
        for child in self.right_panel.winfo_children(): #Removes all right_panels children
            child.destroy()
        self.header_item_details = Label(self.right_panel, text="Details", font=("Helvetica", 54))
        self.label_item_name = Label(self.right_panel, text="Item Name:")
        self.item_name = Entry(self.right_panel)
        self.item_name.insert(0, "-")

        self.item_catalogue = Label(self.right_panel, text="Catalogue:")
        self.item_catalogue_entry = Entry(self.right_panel)
        self.item_catalogue_entry.insert(0, "-")
        
        self.label_item_date = Label(self.right_panel, text="Date Created:")
        self.item_date_created = Entry(self.right_panel)
        self.item_date_created.insert(0, "-")

        self.item_description = Label(self.right_panel, text="Description:")
        self.item_description_entry = Text(self.right_panel, height=5, width=27, highlightbackground="BLACK")
        self.item_description_entry.insert(END, "-")

        self.update_item_btn = Button(self.right_panel, text="Update", command=self.update_item_details)
        
        self.header_item_details.grid(row=0, column=0, columnspan=1)
        self.label_item_name.grid(row=1, column=0, sticky=W)
        self.item_name.grid(row=1, column=3, sticky=W)
        self.item_catalogue.grid(row=2, column=0, sticky=W)
        self.item_catalogue_entry.grid(row=2, column=3, sticky=W)
        self.label_item_date.grid(row=3, column=0, sticky=W)
        self.item_date_created.grid(row=3, column=3, sticky=W)
        self.item_description.grid(row=4, column=0, sticky=NW)
        self.item_description_entry.grid(row=4, column=3, sticky=W)
        self.update_item_btn.grid(row=5, column=3)

    def update_selected_item(self):
        selection = self.item_listbox.get(self.item_listbox.curselection()[0])[0] #Gets the catalogue that is selected
        ctlg_selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0]
        if selection is not "" and self.right_panel_state is False:
            c.execute("SELECT Description, Catalogue, DateCreated, ItemID FROM Items WHERE ItemName = ? AND Catalogue = ?", (selection, ctlg_selection))
            item_details = c.fetchall()[0]
            self.item_name.delete(0,50)
            self.item_name.insert(0, selection)
            self.item_catalogue_entry.delete(0,50)
            self.item_catalogue_entry.insert(0, item_details[1])
            self.item_date_created.delete(0,50)
            self.item_date_created.insert(0, item_details[2])
            self.item_description_entry.delete('1.0',END)
            self.item_description_entry.insert(INSERT, item_details[0])
            self.current_itemid = item_details[3]

            self.item_catalogue_entry.bind("<Key>", lambda e: "break")
            self.item_date_created.bind("<Key>", lambda e: "break")

    def update_catalogue_details(self):
        old_ctlg_name = self.current_ctlgname
        new_ctlg_name = self.catalogue_name.get() #Retreives values from respective widgets
        new_archived = self.archived_state.get()
        
        c.execute("UPDATE Catalogues SET CatalogueName = ?, Archived = ? WHERE CatalogueID = ?", (new_ctlg_name, new_archived, self.current_ctlgid)) #Updates the table replacing the updated values
        con.commit()
        c.execute("UPDATE Items SET Catalogue = ? WHERE Catalogue = ?", (new_ctlg_name, old_ctlg_name))
        con.commit()
        self.update_catalogue_list()

    def update_item_details(self):
        new_item_name = self.item_name.get()
        new_item_description = self.item_description_entry.get('1.0', END)

        c.execute("UPDATE Items SET ItemName = ?, Description = ? WHERE ItemID = ?", (new_item_name, new_item_description, self.current_itemid))
        con.commit()
        self.update_item_list()

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
        self.header_catalogues = Label(self.left_panel, text="Catalogues", font=("Helvetica", 54), bg="grey")
        self.indexes_catalogues = Text(self.left_panel, width=4, font=("Helvetica", 15), height=1, background="grey", borderwidth=0, highlightthickness=0)
        self.catalogue_listbox = Listbox(self.left_panel, selectmode=SINGLE, font=("Helvetica", 15), height=1, bg="grey", borderwidth=0, highlightthickness=0) #Create list box to hold catalogues
        self.header_catalogues.grid(row=0, column=0, columnspan=2, sticky=W)
        self.indexes_catalogues.grid(row=1, column=0, sticky=NE)
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
        self.sort_ctlg_option = StringVar(self.left_panel)
        self.sort_ctlg_option.set("Index") #Sets the default option for the dropdown menu
        self.sort_ctlgs_by = OptionMenu(self.left_panel, self.sort_ctlg_option, "Index", "ABC", "Date", command=lambda e: self.update_catalogue_list()) #Drop down menu for sorting
        self.create_ctlg_btn.grid(row=2, column=0, sticky=E)
        self.delete_ctlg_btn.grid(row=2, column=1, sticky=W)
        self.sort_ctlgs_by.grid(row=2, column=1)

        self.update_catalogue_list() #Updates the index list as well as catalogues

    def item_list(self):
        self.header_items = Label(self.left_panel, text="Items", font=("Helvetica", 54), bg="grey")
        self.indexes_items = Text(self.left_panel, width=4, font=("Helvetica", 15), height=1, background="grey", borderwidth=0, highlightthickness=0)
        self.item_listbox = Listbox(self.left_panel, selectmode=SINGLE, font=("Helvetica", 15), height=1, bg="grey", borderwidth=0, highlightthickness=0) #Create list box to hold catalogues
        self.left_panel.grid_columnconfigure(2, minsize=75)
        self.header_items.grid(row=0, column=3, sticky=W, columnspan=2)
        self.indexes_items.grid(row=1, column=3, sticky=NE)
        self.item_listbox.grid(row=1, column=4, sticky=NW)
        self.item_listbox.configure(exportselection = False)

        self.sort_item_option = StringVar(self.left_panel)
        self.sort_item_option.set("Index") #Sets the default option for the dropdown menu
        self.sort_item_by = OptionMenu(self.left_panel, self.sort_item_option, "Index", "ABC", "Date", command=lambda e: self.update_item_list()) #Drop down menu for sorting

        self.create_item_btn = Button(self.left_panel,text="+", font=("Helvetica", 30), command=self.create_item_popup, height = 1, width = 2, borderwidth=0, highlightthickness=0)
        self.delete_item_btn = Button(self.left_panel, text="-", font=("Helvetica", 30), command=self.delete_item, height = 1, width = 2, borderwidth=0, highlightthickness=0)
        self.create_item_btn.grid(row=2, column=3, sticky=E)
        self.delete_item_btn.grid(row=2, column=4, sticky=W)
        self.sort_item_by.grid(row=2, column=4)

    def update_item_list(self):
        self.indexes_items.configure(state=NORMAL)
        self.indexes_items.delete('1.0', END)
        self.item_listbox.delete(0, END)
        self.indexes_items.tag_configure("center", justify=CENTER)
        selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0]
        
        if self.sort_item_option.get() == "ABC":
            c.execute("SELECT ItemName FROM Items WHERE Catalogue = ? ORDER BY ItemName ASC", (selection,))
        elif self.sort_item_option.get() == "Date":
            c.execute("SELECT ItemName FROM Items WHERE Catalogue = ? ORDER BY DateCreated ASC", (selection,))
        else:
            c.execute("SELECT ItemName FROM Items WHERE Catalogue = ? ORDER BY ItemID ASC", (selection,))

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
        if self.sort_ctlg_option.get() == "ABC": #Retrieves the dropdown variable and compares it with the options
            c.execute("SELECT Catalogues.CatalogueName FROM Catalogues INNER JOIN Accounts ON Catalogues.OwnerID = Accounts.UserID WHERE Accounts.Username = ? ORDER BY Catalogues.CatalogueName ASC", (self.current_user,))
        elif self.sort_ctlg_option.get() == "Date":
            c.execute("SELECT Catalogues.CatalogueName FROM Catalogues INNER JOIN Accounts ON Catalogues.OwnerID = Accounts.UserID WHERE Accounts.Username = ? ORDER BY Catalogues.DateCreated ASC", (self.current_user,))
        else:
            c.execute("SELECT Catalogues.CatalogueName FROM Catalogues INNER JOIN Accounts ON Catalogues.OwnerID = Accounts.UserID WHERE Accounts.Username = ? ORDER BY Catalogues.CatalogueID ASC", (self.current_user,))

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
        self.right_panel_state = True
        selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0] #Gets the catalogue that is selected
        if selection is not "" and self.right_panel_state is True:
            self.catalogue_name.delete(0,50)
            self.catalogue_name.insert(0, selection)
            c.execute("SELECT DateCreated, Archived, CatalogueID, CatalogueName FROM Catalogues WHERE CatalogueName = ?", (selection,))
            result = c.fetchall()[0]
            #self.date_created.configure(state=NORMAL)
            self.date_created.delete(0,50)
            self.date_created.insert(0, result[0])
            if result[1] == 1:
                self.archived_entry.select()
            else:
                self.archived_entry.deselect()
            self.current_ctlgid = result[2]
            self.current_ctlgname = result[3]
            c.execute("SELECT COUNT(*) FROM Items WHERE Catalogue = ?", (selection,))
            self.no_items_entry.delete(0,50)
            self.no_items_entry.insert(0, c.fetchone()[0])
            self.date_created.bind("<Key>", lambda e: "break")
            #self.date_created.configure(state=DISABLED) 
        
    def catalogue_details(self):
        self.right_panel_state = True
        for child in self.right_panel.winfo_children(): #Removes all children inside of the right_panel frame
            child.destroy()
        self.header_details = Label(self.right_panel, text="Details", font=("Helvetica", 54)) #Creating headers
        self.label_catalogue_name = Label(self.right_panel, text="Catalogue Name:")
        self.catalogue_name = Entry(self.right_panel) #Entry to hold catalogue details
        self.catalogue_name.insert(0, "-")
        self.label_date = Label(self.right_panel, text="Date Created:")
        self.date_created = Entry(self.right_panel)
        self.date_created.insert(0, "-")
        self.no_items = Label(self.right_panel, text="No. of Items:")
        self.no_items_entry = Entry(self.right_panel)
        self.archived = Label(self.right_panel, text="Archived:")
        self.archived_state = IntVar(self.right_panel)
        self.archived_entry = Checkbutton(self.right_panel, variable=self.archived_state)
        self.update_ctlg_btn = Button(self.right_panel, text="Update", command=self.update_catalogue_details)
        
        self.header_details.grid(row=0, column=0, columnspan=1)
        self.label_catalogue_name.grid(row=1, column=0, sticky=W)
        self.catalogue_name.grid(row=1, column=3, sticky=E)
        self.label_date.grid(row=2, column=0, sticky=W)
        self.date_created.grid(row=2, column=3, sticky=E)
        self.no_items.grid(row=3, column=0, sticky=W)
        self.no_items_entry.grid(row=3, column=3, sticky=E)
        self.archived.grid(row=4, column=0, sticky=W)
        self.archived_entry.grid(row=4, column=3, sticky=W)
        self.update_ctlg_btn.grid(row=5, column=3)

    def close_windows(self):
        self.master.quit()

    def toolbar(self):
        self.toolbar_menu = Menu(self.master)
        self.master.config(menu=self.toolbar_menu)

        #File Menu
        self.fileMenu = Menu(self.toolbar_menu)
        self.toolbar_menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Exit", command=self.close_windows)
        self.fileMenu.add_command(label="Update", command=self.update_catalogue_list)
        #Catalogue
        self.catalogueMenu = Menu(self.toolbar_menu)
        self.toolbar_menu.add_cascade(label="Catalogue", menu=self.catalogueMenu)
        self.catalogueMenu.add_command(label="Create", command=self.create_ctlg_popup)
        self.catalogueMenu.add_command(label="Delete", command=self.delete_ctlg)
        #Item
        self.itemMenu = Menu(self.toolbar_menu)
        self.toolbar_menu.add_cascade(label="Item", menu=self.itemMenu)
        self.itemMenu.add_command(label="Create", command=self.create_item_popup)
        self.itemMenu.add_command(label="Delete", command=self.delete_item)
        #User Menu
        self.userMenu = Menu(self.toolbar_menu)
        self.toolbar_menu.add_cascade(label="User", menu=self.userMenu)
        self.userMenu.add_command(label=self.current_user)
        self.userMenu.add_separator()
        self.userMenu.add_command(label="Preferences", command=self.user_preferences)

    def delete_ctlg(self):
        selection = self.catalogue_listbox.get(self.catalogue_listbox.curselection()[0])[0]
        c.execute("DELETE FROM Catalogues WHERE CatalogueName = ?", (selection,)) #Delete selected catalogue from database
        con.commit()
        c.execute("DELETE FROM Items WHERE Catalogue = ?", (selection,))
        con.commit()
        self.update_catalogue_list()
        self.update_item_list()
    
    def delete_item(self):
        selection = self.item_listbox.get(self.item_listbox.curselection()[0])[0]
        c.execute("DELETE FROM Items WHERE ItemName = ?", (selection,))
        con.commit()
        self.update_item_list()

    def user_preferences(self):
        popup_window = PreferencesPopup(self.master)
        self.userMenu.entryconfig(2, state=DISABLED)
        self.master.wait_window(popup_window.top)
        self.userMenu.entryconfig(2, state=NORMAL)

        """ self.left_panel.configure(bg=popup_window.value[0])
        self.header_catalogues.configure(bg=popup_window.value[0])
        self.indexes_catalogues.configure(bg=popup_window.value[0])
        self.catalogue_listbox.configure(bg=popup_window.value[0])
        self.header_items.configure(bg=popup_window.value[0])
        self.indexes_items.configure(bg=popup_window.value[0])
        self.item_listbox.configure(bg=popup_window.value[0]) """

        self.left_panel.configure(bg=popup_window.value[0])
        for child in self.left_panel.winfo_children(): #Sets background colour of all children in frame
            child.configure(bg=popup_window.value[0])

        self.right_panel.configure(bg=popup_window.value[1])
        for child in self.right_panel.winfo_children(): 
            child.configure(bg=popup_window.value[1])

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
        info_label = Label(top, text="Item Name: ")
        info_label.grid(row=0, column=0)
        self.item_name_entry = Entry(top)
        self.item_name_entry.grid(row=0, column=1, columnspan=2)

        description_label = Label(top, text="Description: ")
        description_label.grid(row=1, column=0)

        self.description_entry = Entry(top)
        self.description_entry.grid(row=1, column=1, columnspan=2)

        create_ctlg_btn = Button(top,text='Create Item',command=self.destroy_window)
        create_ctlg_btn.grid(row=3, column=1, sticky=W)
    def destroy_window(self):
        self.value = [self.item_name_entry.get(), self.description_entry.get()]
        self.top.destroy()

class PreferencesPopup(object):
    def __init__(self, master):
        top = self.top = Toplevel(master)
        top.title("Preferences")

        colours = [
            "white",
            "red",
            "orange",
            "yellow",
            "green",
            "blue",
            "indigo",
            "violet",
            "grey",
            "black"
        ]

        self.colour1 = StringVar(top)
        self.colour1.set(colours[8])
        self.colour2 = StringVar(top)
        self.colour2.set(colours[0])

        self.colour1_label = Label(top, text="Colour 1:")
        self.colour1_dropdown = OptionMenu(top, self.colour1, *colours)
        self.colour2_label = Label(top, text="Colour 2:")
        self.colour2_dropdown = OptionMenu(top, self.colour2, *colours)

        self.save_btn = Button(top, text="Save", command=self.destroy_window)

        top.grid_columnconfigure(1, minsize=50)
        self.colour1_label.grid(row=0, column=0)
        self.colour1_dropdown.grid(row=0, column=2)
        self.colour2_label.grid(row=1, column=0)
        self.colour2_dropdown.grid(row=1, column=2)
        self.save_btn.grid(row=2)
    def destroy_window(self):
        self.value = [self.colour1.get(), self.colour2.get()]
        self.top.destroy()

root = Tk()
root.title("Login")
root.state('zoomed')
cls = LoginScreen(root)
root.mainloop()