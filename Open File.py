#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from ttk import Frame, Style
from ConfigParser import ConfigParser
from Npp import *
import socket

appConfig = None
debug = None

class formDataStorage:
  srchString = ""
  regExp = False
  opt_m = "0"
  opt_A = "0"
  opt_B = "0"
  fname_pat = ""
  srch_dir = 'db'
  srch_subdir = '*'
  maxDepth = "5"
  isOk = False


def rClicker(e):
  def rClick_Copy(e, apnd=0):
      e.widget.event_generate('<Control-c>')

  def rClick_Cut(e):
      e.widget.event_generate('<Control-x>')

  def rClick_Paste(e):
      e.widget.event_generate('<Control-v>')

  e.widget.focus()

  nclst=[('  Cut    ',   lambda e=e: rClick_Cut(e)),
         ('  Copy   ',  lambda e=e: rClick_Copy(e)),
         ('  Paste  ', lambda e=e: rClick_Paste(e)),]

  rmenu = Menu(None, tearoff=0, takefocus=0)

  for (txt, cmd) in nclst:
    if txt.strip() == 'Paste':
      rmenu.add_separator()
    rmenu.add_command(label=txt, command=cmd)

  rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")
  return "break"

  
class MyForm(Frame):
    def __init__(self, master, formData=None, applyAction=None):
        Frame.__init__(self, master)
        self.pack()
        
        if formData is None:
          self.formData = formDataStorage()
        else:
          self.formData = formData
        
        self.applyAction = applyAction
        
        self.initUI()

        master.bind('<Escape>', lambda event: self.closeWin())
        master.bind('<Return>', lambda event: self.submitData())
        
    def initUI(self):
        
        data_frame = Frame(self.master, relief=RAISED, borderwidth=1)
        data_frame.pack(fill=BOTH, expand=True, padx=5, pady=2, ipady=10)
        
        data_frame.columnconfigure(0, weight=1, minsize=30)
        data_frame.columnconfigure(1, weight=1, minsize=30)
        
# ---------------------- File Name Pattern --------------------------                             
        fname_lb = Label(data_frame, text='File Name Pattern:')
        fname_lb.grid(row=0, column=0, sticky=W, padx=10)

        self.fname_val = StringVar()
        self.fname_val.set(self.formData.fname_pat)
        
        fname = Entry(data_frame, width=50, bd=2, textvariable=self.fname_val)
        fname.grid(row=1, column=0, columnspan=2, sticky=N+S+W+E, padx=10)
        fname.bind('<Button-3>',rClicker, add='')
        
# Close button        
        self.closeButton = Button(self.master, text="Close", width=10, bd=2, 
                                  command=self.closeWin)
        self.closeButton.bind('<Return>', lambda event: self.closeWin())
        
        self.closeButton.pack(side=RIGHT, padx=5, pady=5)

# OK button        
        self.okButton = Button(self.master, text="OK", width=10, 
                                  command=self.submitData)
                                  
        self.okButton.bind('<Return>', lambda event: self.submitData())
        
        self.okButton.pack(side=RIGHT)
        
        fname.focus()

        
    def closeWin(self):
        self.formData.isOk = False
        self.master.destroy()
        
    def submitData(self):
        self.formData.fname_pat = self.fname_val.get().strip()
        if self.formData.fname_pat == "":
          return
        self.formData.isOk = True
        
        if self.applyAction is not None:
          self.applyAction(self.formData)
          
        self.master.destroy()


def composeParams (formData):
  namePattern = formData.fname_pat
  if '.' not in namePattern and \
     '*' not in namePattern :
     namePattern += "*.[p,i]"
                        
  return "ACTION=OPEN_FILE;" + \
         "FNAME_PATTERN=" + namePattern + ';' + \
         "THE_END.\n"

         
def doRequest(dlgData, show=True):
  global appConfig
  
  request = composeParams(dlgData)
  if debug:
    console.write("Requested: " + request)  

  host = appConfig.get("Connection", "host")
  port = appConfig.get("Connection", "port")
  
  if debug:
    console.write("Connection: {}:{}".format(host,port))

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((host, int(port)))
  sock.send(request.encode())

  data = ""
  if show:
   console.write("\n")
   
  while True:
    chunk = sock.recv(1024)
    if len(chunk) <= 0:
        break
    if show:
      console.write(chunk)
    else:
      data += chunk
 
  if not show and data.startswith("Error. ") :
    console.write(data)
    
  return data
  
  
def main():
    global appConfig
    global debug

# Read config
    configFile = notepad.getNppDir() + '/oacomm.conf'
    appConfig = ConfigParser()
    appConfig.read(configFile)
    debug = (appConfig.get("Common", "debug") == 'Y')
    
    root = Tk()

    root.title("Open File")
    root.attributes('-toolwindow', 1)
    root.attributes('-topmost', 1)
    root.resizable(height=False, width=True)

    dlgData = formDataStorage()
    dlgData.fname_pat = editor.getSelText()

    console.show()
    if debug:
      console.write("\n")
    
    app = MyForm(master=root, formData=dlgData, applyAction=None)
    app.focus_force()
    
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
    
    root.mainloop()
    
    if dlgData.isOk:
      answData = doRequest(dlgData, show=False)
      notepad.open(answData)


if __name__ == '__main__':
    main()
