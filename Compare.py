#!/usr/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from Npp import *
import socket

appConfig = None
debug = None

request = "ACTION=GET_ORIGIN_FILE;FNAME_PATTERN={};THE_END.\n"
         
def doRequest(show=True):
  global appConfig
  
  host = appConfig.get("Connection", "host")
  port = appConfig.get("Connection", "port")
  
  if debug:
    console.write("Connect: {}:{}".format(host,port))

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
    console.writeError(data)
    
  return data
  
  
def main():
    global appConfig
    global debug
    global request

# Read config
    configFile = notepad.getNppDir() + '/oacomm.conf'
    appConfig = ConfigParser()
    appConfig.read(configFile)
    debug = (appConfig.get("Common", "debug") == 'Y')
    
    console.show()
    if debug:
      console.write("\n")
    
    fname = notepad.getCurrentFilename()
    
    request = request.format(fname.replace('\\','/'))
    
    if debug:
      console.write("Request: " + request)  

    origName = doRequest(show=False)
    notepad.open(origName)
    notepad.runPluginCommand('Compare', 'Set as First to Compare', True)
    
    notepad.activateFile(fname)
    notepad.runPluginCommand('Compare', 'Compare')

if __name__ == '__main__':
    main()
