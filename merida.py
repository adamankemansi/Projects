#first we'll install & import libraries and packages required.
import RPi.GPIO as GPIO
import MFRC522
import gspread
from datetime import datetime
import time
import pprint
from time import sleep
from oauth2client.service_account import ServiceAccountCredentials

GPIO.setmode(GPIO.BOARD)   # Use Physical Pin Numbering Scheme
button1=16
button2=18
button3=40
LED1=15
LED2=13
GPIO.setwarnings(False)
GPIO.setup(button1,GPIO.IN,pull_up_down=GPIO.PUD_UP) # Make button1 an input, Activate Pull UP Resistor
GPIO.setup(button2,GPIO.IN,pull_up_down=GPIO.PUD_UP) # Make button 2 an input, Activate Pull Up Resistor
GPIO.setup(button3,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED1,GPIO.OUT,)                           # Make LED 1 an Output
GPIO.setup(LED2,GPIO.OUT)                            # Make LED 2 an Output
BS1=False                                            # Set Flag BS1 to indicate LED is initially off
BS2=False                                            # Set Flag BS2 to indicate LED is initially off

#subject uid
sub_uid=[0,"6714816839","224254182212","48193190212","48217182212","11222237112","208149134212"]

#Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

#Create variables for online database
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('rfid.json',scope)
client = gspread.authorize(creds)

#Open sheet from google sheets
sh = client.open ('D8')

#assign current time as a varriable and assign todays date as anew variable
now = datetime.now()
today= [now.day,now.month,now.year]
today= str(today)

def blacklist():
    check_month_end=[now.day,now.month]
    end_dates=[[31,1],[28,2],[29,2],[31,3],[30,4],[31,5],[30,6],[31,7],[31,8],[30,9],[31,10],[30,11],[31,12]]
    for index in range(0,12,1):
        if check_month_end ==end_dates[index]:
            return True

#define function to scan the cards
def scan():
    # This loop checks for chips. If one is near it will get the UID
    try:
        while True:
            # Scan for cards
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            
            # Get the UID of the card
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            
            # If we have the UID, continue
            if status == MIFAREReader.MI_OK :
                
                uid = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])
                
                # Print UID
                #print("UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                return(uid)
                #time.sleep(5)
                
    except KeyboardInterrupt:
        GPIO.cleanup()

def teacher():
    teacher_uid = scan()
    return(teacher_uid)

def student():
    student_uid = scan()
    return(student_uid)

#main loop
print("press button 1 for teacher")
try:

    while True:
        if GPIO.input(button1)==0:              # checks if button 1 is pressed
            print ("scan subject card")
            if BS1==False:
                global tuid
                tuid = teacher()
                print(tuid)
                index = sub_uid.index(tuid)
                print(index)
                global sheet
                sheet = sh.get_worksheet(index)
                GPIO.output(LED1,False)
                print("press button 2 to start attendance.")
                break
        
    while True:     
        if GPIO.input(button2)==0:              # checks if button 1 is pressed
            print ("scan student card")
            if BS2==False:
                global suid
                suid = student()
                #Import value to google sheets
                cell = sheet.find(suid)         #find uid number in sheet
                value = cell.value
                row_number = cell.row           #store value of row
                column_number = cell.col        #store value of column
                roll_no=sheet.cell(row_number,1).value
                print (roll_no)
                global count
                count = sheet.cell(1,1).value
                count = int(count)
                    
                if value == suid:
                    sheet.update_cell(row_number,count,'1')
                    print('done')
                    sheet.update_cell(2,count,today)
                   

                if blacklist()==True:
                    count=count+1
                    sheet.update_cell(2,count,"month_end")
                    '''f_element=str(sheet.cell(row_number,4).value)
                    if f_element=='':
                        f_element='0'
                    row_list=[int(f_element)]
                    for j in range(4,count,1):
                        element=str(sheet.cell(row_number,j).value)
                        if element=='':
                            element='0'
                            row_list.append(int(element))
                            j=j+1
                    monthly_count=0
                    for jx in range(0,(len(row_list)),1):
                        monthly_count=monthly_count+row_list[jx]
                        jx=jx+1
                    sheet.update_cell(row_number,count,monthly_count)
                    print("month end",monthly_count)'''
                    count=count+1
                    sheet.update_cell(1,1,count)
                    

    
        if GPIO.input(button3)==0:
            print('end of attendance.')
            fe=str(sheet.cell(3,count).value)
            if fe=='':
                fe='0'
            col_list=[int(fe)]
            for i in range(4,7,1):
                e=str(sheet.cell(i,count).value)
                if e=='':
                    e='0'
                col_list.append(int(e))
                i=i+1
            print(col_list)
            todays_count=0
            for ix in range(0,(len(col_list)),1):
                todays_count=todays_count+col_list[ix]
                ix=ix+1
            sheet.update_cell(8,count,todays_count)
            print("todays_count is:-",todays_count)
            count = count + 1
            sheet.update_cell(1,1,count)
            break

except KeyboardInterrupt:
    GPIO.cleanup()

