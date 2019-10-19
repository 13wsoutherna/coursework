from tkinter import *
musicfolder = [
  ["CollegeRock/"],
  ['RnB/'],
  ['HipHop/'],
  ['Build/'],
  ['Buy/'],
  ['Techno/'],
  ['Jazz/'],
  ['Classic/']
]
def get_list(event):
    """
    function to read the listbox selection
    and put the result in an entry widget
    """
    # get selected line index
    index = listbox1.curselection()[0]
    # get the line's text
    seltext = listbox1.get(index)
    # delete previous text in enter1
    enter1.delete(0, 50)
    # now display the selected text
    enter1.insert(0, seltext)
    
root = Tk()
# create the listbox (note that size is in characters)
listbox1 = Listbox(root, width=50, height=6)
listbox1.grid(row=0, column=0)
# create a vertical scrollbar to the right of the listbox
yscroll = Scrollbar(command=listbox1.yview, orient=VERTICAL)
yscroll.grid(row=0, column=1, sticky=N+S)
listbox1.configure(yscrollcommand=yscroll.set)
# create data entry
enter1 = Entry(root, width=50, bg='yellow')
enter1.insert(0, 'Click on an item in the listbox')
enter1.grid(row=1, column=0)
# load the listbox with data
for item in musicfolder:
    listbox1.insert(END, item)
 
# left mouse click on a list item to display selection
listbox1.bind('<ButtonRelease-1>', get_list)
root.mainloop()