#first we'll install & import libraries and packages.
import RPi.GPIO as GPIO
import sleep from time
import MFRC522
import gspread
import datetime
import time
import pprint
from oauth2client.service_account import ServiceAccountCredentials

#Define GPIO to LED,Button mapping
LED = 17
LED_R = 27
LED_G = 22
PS_IN = 23
PS_OUT = 24

#set up all GPIO pins used for leds & buttons
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)    # LED
GPIO.setup(LED_R, GPIO.OUT)  # RED_LED
GPIO.setup(LED_G, GPIO.OUT)  # GREEN_LED
GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #PUSH_SWITCH_IN
GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #PUSH_SWITCH_OUT

#* Define GPIO to LCD mapping
LCD_RS = 20
LCD_E  = 5
LCD_D4 = 26
LCD_D5 = 19
LCD_D6 = 13
LCD_D7 = 6

#* Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

#* Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#* setup all GPIO pins used in LCD
def main():
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setwarnings(False)
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7

    lcd_init()                   #initialize display
    while True:
        lcd_string("RFID Attendance",LCD_LINE_1)
        lcd_string("system",LCD_LINE_2)
        time.sleep(2)
#*
def lcd_init():
    lcd_display(0x28,LCD_CMD) # Selecting 4 - bit mode with two rows
    lcd_display(0x0C,LCD_CMD) # Display On,Cursor Off, Blink Off
    lcd_display(0x01,LCD_CMD) # Clear display
    sleep(E_DELAY)
#*
def lcd_string(message,line):
    message = message.ljust(LCD_WIDTH," ") # Send string to display
    lcd_display(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_display(ord(message[i]),LCD_CHR)
#*
def lcd_toggle_enable():      # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)
#*
def lcd_display(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True for character
    # False for command
    GPIO.output(LCD_RS, mode) # RS
    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
        if bits&0x10==0x10:
            GPIO.output(LCD_D4, True)
        if bits&0x20==0x20:
            GPIO.output(LCD_D5, True)
        if bits&0x40==0x40:
            GPIO.output(LCD_D6, True)
        if bits&0x80==0x80:
            GPIO.output(LCD_D7, True)
    # Toggle 'Enable' pin
    lcd_toggle_enable()
    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
        if bits&0x01==0x01:
            GPIO.output(LCD_D4, True)
        if bits&0x02==0x02:
            GPIO.output(LCD_D5, True)
        if bits&0x04==0x04:
            GPIO.output(LCD_D6, True)
        if bits&0x08==0x08:
            GPIO.output(LCD_D7, True)
    # Toggle 'Enable' pin
    lcd_toggle_enable()
#*
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
        GPIO.cleanup()

#Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

#Create variables for online database
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('rfid.json',scope)
client = gspread.authorize(creds)

#Open sheet from google sheets
sh = client.open ('D8')    #sheet = client.open('D8').sheet1
sheet = sh.get_worksheet(0)

#assign current time as a varriable and assign todays date as anew variable
today = datetime.today()
datem = datetime(today.year, today.month, 1)
now = datetime.datetime.now()
month = 1

#assign time variables to be compared with current time
t1 = now.replace(hour = 8, minute = 10, second = 0, microsecond = 0)
t2 = now.replace(hour = 8, minute = 20, second = 0, microsecond = 0)
t3 = now.replace(hour = 9, minute = 10, second = 0, microsecond = 0)
t4 = now.replace(hour = 9, minute = 20, second = 0, microsecond = 0)
t5 = now.replace(hour = 10, minute = 10, second = 0, microsecond = 0)
t6 = now.replace(hour = 10, minute = 35, second = 0, microsecond = 0)
t7 = now.replace(hour = 11, minute = 25, second = 0, microsecond = 0)
t8 = now.replace(hour = 11, minute = 35, second = 0, microsecond = 0)
t9 = now.replace(hour = 12, minute = 25, second = 0, microsecond = 0)
t10 = now.replace(hour = 12, minute = 55, second = 0, microsecond = 0)
t11 = now.replace(hour = 13, minute = 45, second = 0, microsecond = 0)
t12 = now.replace(hour = 13, minute = 55, second = 0, microsecond = 0)

#initialize scanning
def scan():
    # Welcome message
    print("Looking for cards")
    lcd_string("looking for",LCD_LINE_1)
    lcd_string("cards",LCD_LINE_2)
    
    # This loop checks for chips. If one is near it will get the UID
    try:
        while True:
            # Scan for cards
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            # Get the UID of the card
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            # If we have the UID, continue
            if status == MIFAREReader.MI_OK :
                GPIO.output(17,GPIO.HIGH)    
                lcd_string("Scanned",LCD_LINE_1)
                time.sleep(2)
                GPIO.output(17,GPIO.LOW)
                check_uid = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])
                # Print UID
                print("UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                return check_uid
            else:
                GPIO.output(17,GPIO.HIGH)
                lcd_string("invalid card",LCD_LINE_1)
                time.sleep(2)
                GPIO.output(17,GPIO.LOW)
                
                

#to change dimensions of row and coloumns 
def dimensions(row,coloumn):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.row_dimensions[row].height = 20
    sheet.column_dimensions['coloumn'].width = 50
    wb.save('dimensions.xlsx')

#to merge cells
def merging(cell1,cell2):
    sheet = wb.active
    sheet.merge_cells('cell1:cell2')
    wb.save('merged.xlsx')

# to create new sheet for every month
def month():
    if  today ==datem and month!=12:
        #Open sheet from google sheets 
        sh = client.open ('D8')       #sheet = client.open('D8').sheet1
        sheet = sh.get_worksheet(month)
        month = month +1

#online data
def gsheet():
    scan()
    #Import cell info. from google sheets
    cell = sheet.find(check_uid)        #find uid number in sheet
    value = cell.value
    row_number = cell.row               #store value of row
    column_number = cell.col            #store value of column
    lec = sheet.cell(2,1).value
    #conditions for entering attendance data according to lecture timing
    try:
        if value == check_uid:
            if (now <= t2) or ((now >= t1) and (now <= t2)):
                lec=lec+1
                sheet.update_cell(row_number,lec,'1')
                print('done')
                lec = lec-1
            elif (now >= t3) and (now <= t4):
                lec=lec+2
                sheet.update_cell(row_number,lec,'1')
                print('done')
                lec = lec-2
            elif (now >= t5) and (now <= t6):
                lec=lec+3
                sheet.update_cell(row_number,lec,'1')
                print('done')
                lec = lec-3
            elif (now >= t7) and (now <= t8):
                lec=lec+4
                sheet.update_cell(row_number,lec,'1')
                print('done')
                lec = lec-4
            elif (now >= t9) and (now <= t10):
                lec=lec+5
                sheet.update_cell(row_number,lec,'1')
                print('done')
                lec = lec-5
            elif (now >= t11) and (now <= t12):
                lec=lec+6
                sheet.update_cell(row_number,lec,'1')
                print('done')
                lec = lec-6
            else:
                print('you are late')
        else:
            print('invalid entry')
            lec=lec+6
            sheet.update_cell(2,1,lect)
            time.sleep(3)
    except KeyboardInterrupt:
        GPIO.cleanup()



#actual code
while True:
    input_state_in = GPIO.input(23)
    input_state_out = GPIO.input(24)
    if input_state_in == False:
        print('Button for entry is Pressed')
        GPIO.output(27,GPIO.HIGH)    #glowing red led
        lcd_string("scan card",LCD_LINE_1)
        time.sleep(0.2)
        GPIO.output(27,GPIO.LOW)
        scan()
        gsheet()
        time_in = datetime.datetime.now()
        GPIO.cleanup()
    elif input_state_out == False:
        print('Button for exit is Pressed')
        GPIO.output(22,GPIO.HIGH)    #glowing red led
        lcd_string("scan card",LCD_LINE_1)
        time.sleep(0.2)
        GPIO.output(22,GPIO.LOW)
        scan()
        gsheet()
        time_out = datetime.datetime.now()
        GPIO.cleanup()


'''Tasks still remaining:
1.writing code for when we should call merge wala method
2.when and where to call month wala method
3.we can get in and out times but whwere to store it and how to calculate attendance for the total hours he/she attended
4.changing lect1,lect2,lect3 to respective lectures taking place at that time...similiarly for day1,day2 with actual date
5.getting attendance subjectwise
6.format paintaing
7.local database
8.running the entire code and debuging the erros
9.making the sytem to work for more than one rfid card and creating databases for other classes too
10.documentation
'''
        
        
