#!/usr/bin/python
# -*- coding: utf-8 -*-

#from Tkinter import Tk, Entry, Label, Button, RIGHT, BOTH, RAISED, SUNKEN, \
#      W, N, E, S, StringVar
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
        
        self.srchDir = ["db","cui","dat","scripts"]
            
        try : 
          self.srch_dir_idx = self.srchDir.index(self.formData.srch_dir)
        except :
          self.srch_dir_idx = 0
        
        self.reg_exp_val = int(self.formData.regExp)
        
        self.initUI()

        master.bind('<Escape>', lambda event: self.closeWin())
        master.bind('<Return>', lambda event: self.submitData())
        
    def initUI(self):
        
        data_frame = Frame(self.master, relief=RAISED, borderwidth=1)
        data_frame.pack(fill=BOTH, expand=True, padx=5, pady=2)

        data_frame.columnconfigure(0, weight=1, minsize=30)
        data_frame.columnconfigure(1, weight=1, minsize=30)
        
# ---------------------- File Name Pattern --------------------------                             
        fname_lb = Label(data_frame, text='File Name Pattern:')
        fname_lb.grid(row=4, column=0, sticky=W, padx=10)

        self.fname_val = StringVar()
        self.fname_val.set(self.formData.fname_pat)
        
        fname = Entry(data_frame, width=50, bd=2, textvariable=self.fname_val)
        fname.grid(row=5, column=0, columnspan=2, sticky=N+S+W+E, padx=10)
        fname.bind('<Button-3>',rClicker, add='')
# ---------------------- Location -----------------------------
        loc_frame = LabelFrame(data_frame, text='Location')
        loc_frame.columnconfigure(0, weight=1, minsize=50)
        loc_frame.columnconfigure(1, weight=1, minsize=50)
        loc_frame.columnconfigure(2, weight=1, minsize=50)
        loc_frame.columnconfigure(3, weight=1, minsize=50)

        self.location_val = IntVar()        
        self.location_val.set(self.srch_dir_idx)
        
# Search in Db Location
        RBox0 = Radiobutton(loc_frame, text='db', 
                                  variable=self.location_val, value=0)
        RBox0.grid(row=0, column=0, sticky=W, padx=10)

# Search in cui localion                           
        RBox1 = Radiobutton(loc_frame, text='cui', 
                                  variable=self.location_val, value=1)
        RBox1.grid(row=0, column=1, sticky=W, padx=10)
        
# Search in Dat localion                           
        RBox2 = Radiobutton(loc_frame, text='dat', 
                                  variable=self.location_val, value=2)
        RBox2.grid(row=0, column=2, sticky=W, padx=10)

# Search in scripts localion                           
        RBox3 = Radiobutton(loc_frame, text='scripts', 
                                  variable=self.location_val, value=3)
        RBox3.grid(row=0, column=3, sticky=W, padx=10)

# Search in sub-folders                           
        lb2 = Label(loc_frame, text='Sub-dirs:')
        lb2.grid(row=1, column=0, sticky=E)

        self.subDir_val = StringVar()
        self.subDir_val.set(self.formData.srch_subdir)
        
        subFolders  = Entry(loc_frame, width=30, bd=2, 
                           textvariable=self.subDir_val)
                           
        subFolders.grid(row=1, column=1, columnspan=3, 
                        pady = 5, padx = 10, sticky=W+E)

        subFolders.bind('<Button-3>',rClicker, add='')
                           
# Search maxdepth                           
        lb3 = Label(loc_frame, text='Dir Depth:')
        lb3.grid(row=2, column=0, sticky=E)

        self.maxDepth_val = StringVar()
        self.maxDepth_val.set(self.formData.maxDepth)
        
        maxDepth  = Entry(loc_frame, width=10, bd=2, 
                          textvariable=self.maxDepth_val)
                          
        maxDepth.grid(row=2, column=1, columnspan=1, 
                      pady = 5, padx = 10, sticky=W)
                           
# Put on the form
        loc_frame.grid(row=6, column=0, columnspan=2, padx=10, 
                            pady=5, sticky=N+S+W+E)

  
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
        self.master.destroy()
        
    def submitData(self):
        self.formData.fname_pat = self.fname_val.get().strip()
        if self.formData.fname_pat == "":
          return
        self.formData.srch_dir = self.srchDir[self.location_val.get()]
        self.formData.srch_subdir = self.subDir_val.get()
        self.formData.maxDepth  = self.maxDepth_val.get()
        self.formData.isOk = True
        
        if self.applyAction is not None:
          self.applyAction(self.formData)
          
        self.master.destroy()


def composeParams (formData):
  # 1) *.[p,i]  2) name*.[p,i]  3) name.ext
  namePattern = formData.fname_pat
  if '.' not in namePattern :
    if formData.srch_dir == "dat" :
      fextention = ".s"
    elif formData.srch_dir == "scripts" :
      fextention = ".js"
    else :
      fextention = ".[p,i]"
      
    if '*' not in formData.fname_pat :
      fextention = '*' + fextention

    namePattern += fextention

  if formData.srch_dir == "dat" :
    namePattern = namePattern.lower()
    if namePattern[0] == '%' and not namePattern.startswith("%25") :
      namePattern = namePattern.replace('%','%25',1)
  
  # 1) blank - no subdir  2) * - all  3) subdir list
  sub_dir = formData.srch_subdir  
  if sub_dir != "" and sub_dir != "*" :
    sub_dir = ''
    for cDir in formData.srch_subdir.split() :
      sub_dir =  sub_dir + ( " " if sub_dir != '' else '' ) + cDir
      
  findOptions = "FNAME_PATTERN=" + namePattern + ';' \
              + "FIND_IN_DIR=" + formData.srch_dir + ';'     \
              + "SUBDIR_LIST=" + sub_dir + ';'               \
              + "MAX_DEPTH=" + ("1" if int(formData.maxDepth) < 1 \
                                    else formData.maxDepth)
                  
  return "ACTION=FIND_FILE;" + findOptions + ';' + "THE_END.\n"

         
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
    size = (300,205)
    xpos = (root.winfo_screenwidth() - size[0])/2
    ypos = (root.winfo_screenheight() - size[1])/2
    root.geometry("{}x{}+{}+{}".format(*(size + (xpos, ypos))))
    root.resizable(height=False, width=True)

    root.title("Find File")
    root.attributes('-toolwindow', 1)
    root.attributes('-topmost', 1)

    dlgData = formDataStorage()
    dlgData.fname_pat = editor.getSelText()

    console.show()
    if debug:
      console.write("\n")
    
    app = MyForm(master=root, formData=dlgData, applyAction=doRequest)
    app.focus_force()
    
    root.mainloop()
    
#    if dlgData.isOk:
#      answData = doRequest(dlgData)


if __name__ == '__main__':
    main()
