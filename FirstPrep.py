from Drivers.ExcelCtrl import *
from Drivers.Terminal.SendDataMsg import *
from Drivers.Terminal.ReadEthData import *
from Tests.commFunctions import *


log = logging.getLogger('start_receiving')
iCD = Drivers.Terminal.iCDs
rcvD = ReceiveData()
all_strck = icd_strucks()
rcvD.send_receive_order()
sdm = Send_The_Data()
stop_thread = False
me = MyExcel()
ws1 = me.my_sheet

def rcv_the_packets():
    FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

    v = [rcvD.all_strck.batParamRep["voltage"] / 1000, rcvD.all_strck.batParamRep["current"] / 1000,
            rcvD.all_strck.batParamRep["runTimeToEmpty"], rcvD.all_strck.batParamRep["avgTimeToFull"],
            rcvD.all_strck.batParamRep["tempK"] / 10 - 273.15 , rcvD.all_strck.batParamRep["digTemp"],
         all_strck.PICReadWriteMsg["data"]]

    ctime = time.time()
    for [data, addr] in rcvD.start_receiving():
        #log.debug(f"data {data} addr {addr}")
        #print(f"{data[0]}")
        rcvD.updateFeildsFromInputMsg()
        if time.time() - ctime > 10:
            update_batstat_excel()
            ctime = time.time()
        if rcvD.all_strck.batParamRep["voltage"] / 1000 < 11.9:
            stop_thread = True
            break

        '''
        if v!= [rcvD.all_strck.batParamRep["voltage"] / 1000, rcvD.all_strck.batParamRep["current"] / 1000,
            rcvD.all_strck.batParamRep["runTimeToEmpty"], rcvD.all_strck.batParamRep["avgTimeToFull"],
            rcvD.all_strck.batParamRep["tempK"] / 10 - 273.15 , rcvD.all_strck.batParamRep["digTemp"],
            all_strck.PICReadWriteMsg["data"]]:
            update_batstat_excel()
            v = [rcvD.all_strck.batParamRep["voltage"] / 1000, rcvD.all_strck.batParamRep["current"] / 1000,
            rcvD.all_strck.batParamRep["runTimeToEmpty"], rcvD.all_strck.batParamRep["avgTimeToFull"],
            rcvD.all_strck.batParamRep["tempK"] / 10 - 273.15 , rcvD.all_strck.batParamRep["digTemp"],
            all_strck.PICReadWriteMsg["data"]]
        '''
        global stop_thread
        if stop_thread:
            break



def update_batstat_excel():
    global ws1
    if rcvD.all_strck.batParamRep["voltage"] != 0:
        ws1.append([rcvD.all_strck.batParamRep["voltage"] / 1000, rcvD.all_strck.batParamRep["current"] / 1000,
                    rcvD.all_strck.batParamRep["runTimeToEmpty"], rcvD.all_strck.batParamRep["avgTimeToFull"],
                    rcvD.all_strck.batParamRep["tempK"] / 10 - 273.15 , rcvD.all_strck.batParamRep["digTemp"],
                    all_strck.PICReadWriteMsg["data"]])

def send_packets():
    time_to_wait = 2
    while True:
        rcvD.send_receive_order()
        all_strck = icd_strucks()
        all_strck.PICReadWriteMsg["cmd"] = iCD.SPI_READ
        all_strck.PICReadWriteMsg["addr"] = 8
        sdm.send_the_message("PICReadWriteMsg", all_strck.PICReadWriteMsg)
        time.sleep(time_to_wait)
        global stop_thread
        if stop_thread:
            break


def currentConsumptionTest():
    # turn off tx
    all_strck.MxFEAxiRegMsg["data"] = 0x3
    sdm.send_the_message("MxFEAxiRegMsg", all_strck.MxFEAxiRegMsg)

    # check bat status every 10 sec and upload to excel
    print("checking battery status ...")
    ws1.append(["bat Status: "])
    ws1.append(["voltage","current", "RunTime2Empty", "AvgTime2Full", "Temp", "Digital Temp", "Rf Temp"])
    global stop_thread
    stop_thread = False
    t1 = threading.Thread(target=rcv_the_packets)
    t1.start()
    t2 = threading.Thread(target=send_packets)
    t2.start()
    time.sleep(500)
    stop_thread = True
    t1.join()
    t2.join()
    print('thread currentConsumptionTest killed')
    # unplug unit from external voltage
    # wait for 10 min - check voltage/ current graph
    return "Pass"

def temptest():
    #asking user to unplug voltage wire from unit:
    input("Please unplug unit and press a key")
    # configuring terminal:
    all_strck.MxFEAxiRegMsg["data"] = 0x7
    sdm.send_the_message("MxFEAxiRegMsg", all_strck.MxFEAxiRegMsg)
    time.sleep(1)
    all_strck.Lmx2592FreqMsg["val"] = 29001
    sdm.send_the_message("Lmx2592FreqMsg", all_strck.Lmx2592FreqMsg)
    time.sleep(1)
    print("checking temperature status ...")
    time.sleep(10)
    # taking temperature samples :
    global stop_thread
    stop_thread = False
    t1 = threading.Thread(target=rcv_the_packets)
    t1.start()
    t2 = threading.Thread(target=send_packets)
    t2.start()
    time.sleep(500)
    stop_thread = True
    t1.join()
    t2.join()
    print('thread temptest killed')
    all_strck.MxFEAxiRegMsg["data"] = 0x3
    sdm.send_the_message("MxFEAxiRegMsg", all_strck.MxFEAxiRegMsg)
    return "Pass"


# ipusAll()

#print("Scan The unit with the barcode:")
#unitName = input()
unitName = 1117
print("Hello unit number: , " , unitName)

props = getHRprops(unitName)
print(props)

me.change_sheet_title(ws1, "First Prep")
ws1.append(["SN", "ssid_name", "SW_Ver"])
ws1.append([unitName, props[0], props[1]])
print("Check all colors: red, blue, green! ")
print("Enter OK if all colors apeared !")
colorsStatus = 'OK'#input()
ws1.append(["", "colorsStatus"])
ws1.append(["", colorsStatus])
# sendReboot()OK - SSH
ping = CheckPingAllAngles('192.168.43.1',5) #returns -1 if no ping
ws1.append(["", "pingStatus"])
ws1.append(["", round(ping*1000, 5), "msec"])
cct = currentConsumptionTest()
#לכבות את המתח של היחידה ומוציא הכל לשידור וקליטה
ws1.append(["", "current_Consumption_Test"])
ws1.append(["", cct])
tempt = temptest()
ws1.append(["", "temp_test"])
ws1.append(["", tempt])
me.saveTheWorkBookWithtimestamp()
print('Done !')

