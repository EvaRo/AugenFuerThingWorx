import requests
import json
import base64
import picamera
from datetime import datetime
import uuid
import tkinter


# Konstanten zur Kommunikation mit dem aktuellen ThingWorx-Servers
# Muessen fuer neuen Server hinzugefuegt werden
APPKEY = '' 
USER = ''
PASSWORD = ''
SERVER = ''

# Gibt aktuelle Zeit als formatierte Zeitmarke zurueck
def generateTimestamp():
    curr_time = datetime.now()
    return ("%04d-%02d-%02d %02d:%02d:%02d" % (curr_time.year, curr_time.month, curr_time.day, \
                                           curr_time.hour, curr_time.minute, curr_time.second))

# Das lokale gespeicherte Foto wird Base64 kodiert und als String zurueckgegeben
def encodePhoto(datapath):
    with open(datapath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    encoded_string = str(encoded_string, encoding='ascii')
    return encoded_string

# Mit der picamer API wird ein Foto aufgenommen und auf dem Desktop gespeichert
def captureFrame():
    with picamera.PiCamera() as cam:
        curr_time = datetime.now()
        filename = "/home/pi/Desktop/Testsaves/capture-" + generateTimestamp() +".jpg" 
        cam.capture(filename)
        print("Aufnahme!" )
        return filename

# MAC-Adresse des Geraets wird ausgelesen und im Format xx-xx-xx-xx-xx-xx zurueckgegeben
def getFormattedMAC():
    return ('-'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1]))

# Ein Foto wird mit captureFrame aufgenommen, enkodiert, mit Timestamp und Zustazinformationen
# besetzt und in einem HTTP Post Body an das mit "name" uebergebene Thing in ThingWorx versendet
def sendFoto(name): 
    encodedPhoto = encodePhoto(captureFrame())
    request =  ("%s%s%s" % (SERVER, "/Thingworx/Things/"+name+"/Services/ChangeProperties?appKey=", APPKEY))
    stamp= generateTimestamp()
    postargs = {"JSONInput":{"stamp":stamp,"photo":encodedPhoto,"info":"placeholder"}} 
    headerargs = {'content-type':'application/json', 'accept':'application/json'}
    r = requests.post(url=request, auth=(USER, PASSWORD), data=json.dumps(postargs), headers=headerargs)
    print ('Send Foto. Status: ' , r.status_code)
    print('Text: ' ,r.text)
    if (r.status_code == 200):
        print ('Photo was sent.')
    else:
        print ('Sending Photo not successful. Raspberry already registered?')
       
# Thing wird mit uebergebenem Namen generiert 
def createThing(name):   
    request = ("%s%s%s" % (SERVER, "/Thingworx/Resources/EntityServices/Services/CreateThing?method=post&appKey=", APPKEY))
    headerargs = {'content-type':'application/json', 'accept':'application/json'}
    postargs = {"name":name, "thingTemplateName":"RaspberryNewTemplate"}
    r = requests.post(url=request, auth=(USER, PASSWORD), data=json.dumps(postargs), headers=headerargs)
    print ('CreateThing. Status: ' , r.status_code)
    print ('Text: ' , r.text)
    print ('createThing finished.')
    return (r.status_code)

# Thing wird aktiviert
def enableThing(name):   
    request = ("%s%s%s" % (SERVER, "/Thingworx/Things/"+name+"/Services/EnableThing?appKey=", APPKEY)) 
    headerargs = {'content-type':'application/json', 'accept':'application/json'}
    postargs ={}
    r = requests.post(url=request, auth=(USER, PASSWORD), data=json.dumps(postargs), headers=headerargs)
    print ('Enable. Status: ' , r.status_code)
    print ('enabled.')

# Thing wird neugestartet
def restartThing(name): 
    request = ("%s%s%s" % (SERVER, "/Thingworx/Things/"+name+"/Services/RestartThing?appKey=", APPKEY))
    headerargs = {'content-type':'application/json', 'accept':'application/json'}
    postargs ={}
    r = requests.post(url=request, auth=(USER, PASSWORD), data=json.dumps(postargs), headers=headerargs)
    print ('Restart. Status: ' , r.status_code)
    print ('restarted.')
    
# Methode, um die MAC-Adresse eines Things zu setzen
def setMAC(mac, name):
    request = ("%s%s%s" % (SERVER, "/Thingworx/Things/"+name+"/Properties/MACAddress?appKey=", APPKEY))
    headerargs = {'content-type':'application/json', 'accept':'application/json'}
    postargs ={"MACAddress":mac}
    r = requests.put(url=request, auth=(USER, PASSWORD), data=json.dumps(postargs), headers=headerargs)
    print ('Setting MAC. Status: ' , r.status_code)
    print ('MAC-Address set.' , r.text)

# Raspberry wird registriert in den Schritten: Thing wird erstellt, akiviert, neu gestartet und seine 
# MAC-Adresse gesetzt
def registerPi(mac): 
    name = ("Pi_" + mac)
    if (createThing(name) == 200):
        enableThing(name)
        restartThing(name)
        setMAC(mac, name)
        print ("Registration successful.")
    else:
        print ("Registration failed.")


# Eigentliche Programmroutine. Mit tkinter API wird ein Fenster mit Optionsbuttons erzeugt.
# Die Buttons dienen dazu: 1. Den Raspberry Pi, der das Programm nutzt, registrieren,
# 2. Foto von dem vorliegenden Raspberry Pi aufnehmen und versenden,
# 3. Raspberry mit abweichender MAC-Adresse erzeugen,
# 4. Mit beliebigem auf TW registrierten Raspberry PI als Absender Foto versenden,
# 5. Programm Beenden.
top = tkinter.Tk()
top.wm_title("Raspberry Camera Client")
top.geometry('{}x{}'.format(500, 200))
label1=tkinter.Label(top,text="Optionen: ").pack()

def register():
    registerPi(getFormattedMAC())
def send():
    sendFoto("Pi_" + getFormattedMAC())
def testPi():
    mac=input("Bitte MAC-Adresse in die Konsole eingeben:\n")
    registerPi(mac)
def sendToName():
    name=input("Bitte Namen des PI eingeben:\n")
    sendFoto(name)
def endProgram():
    top.quit()
    
button1=tkinter.Button(top,text="Diesen PI registrieren",command = register).pack()
button2=tkinter.Button(top,text="Sende Foto",command = send).pack()
button3=tkinter.Button(top,text="Erzeuge PI mit anderer MAC-Adresse",command = testPi).pack()
button4=tkinter.Button(top,text="Send Foto von beliebigem PI",command = sendToName).pack()
button5=tkinter.Button(top,text="Beenden",command = endProgram).pack()
top.mainloop()





