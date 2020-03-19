from Drivers.ExcelCtrl import *
from Drivers.Terminal.SendDataMsg import *
from Drivers.Terminal.ReadEthData import *
from Tests.commFunctions import *
from Drivers.StepEngineCtrl import *


iCD = Drivers.Terminal.iCDs
rcvD = ReceiveData()
all_strck = icd_strucks()
rcvD.send_receive_order()
sdm = Send_The_Data()
stop_thread = False
me = MyExcel()
ws1 = me.my_sheet
# my_eng = MyStepEngine("azimuth")

#read imu - roll, pitch, yaw
def rcv_the_packets():
    FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

    v = [rcvD.all_strck.PointAntStruct["imuRoll"], rcvD.all_strck.PointAntStruct["imuPitch"],
            rcvD.all_strck.PointAntStruct["imuYaw"], rcvD.all_strck.dynPointParamMsg["status"],
         rcvD.all_strck.dynPointParamMsg["latitude"], rcvD.all_strck.dynPointParamMsg["longitude"],
         rcvD.all_strck.dynPointParamMsg["altitude"]]

    ctime = time.time()
    for [data, addr] in rcvD.start_receiving():
        #log.debug(f"data {data} addr {addr}")
        #print(f"{data[0]}")
        rcvD.updateFeildsFromInputMsg()
        if time.time() - ctime > 0.1:
            update_batstat_excel()
            ctime = time.time()
        global stop_thread
        if stop_thread:
            break


def update_batstat_excel():
    global ws1
    if rcvD.all_strck.PointAntStruct["imuRoll"] != 0:
        ws1.append([rcvD.all_strck.PointAntStruct["imuRoll"], rcvD.all_strck.PointAntStruct["imuPitch"],
                    rcvD.all_strck.PointAntStruct["imuYaw"], rcvD.all_strck.dynPointParamMsg["status"],
         rcvD.all_strck.dynPointParamMsg["latitude"], rcvD.all_strck.dynPointParamMsg["longitude"],
         rcvD.all_strck.dynPointParamMsg["altitude"]])


# ipusAll()
# my_eng.check_communication()
print("imu test ...")
ws1.append(["imU Test", "azimuth - X axis", ""])
ws1.append(["imuRoll", "imuPitch", "imuYaw", "gps Status", "latitude", "longitude", "altitude"])

stop_thread = False
t1 = threading.Thread(target=rcv_the_packets)
t1.start()
#move the engine from -90 to +90 (azimuth - X axis)
time.sleep(20)
#always read


ws1.append(["imU Test", "elevation - Y axis", ""])
ws1.append(["imuRoll", "imuPitch", "imuYaw", "gps Status", "latitude", "longitude", "altitude"])

#move the engine from -90 to +90 (elevation - Y axis)

time.sleep(20)
#always read

stop_thread = True
t1.join()

#GPS - check status = 1
print("Gps test ...")
ws1.append(["GPs Test", "azimuth - X axis", ""])
ws1.append(["imuRoll", "imuPitch", "imuYaw", "gps Status", "latitude", "longitude", "altitude"])

stop_thread = False
t2 = threading.Thread(target=rcv_the_packets)
t2.start()
#move the engine from -90 to +90 (azimuth - X axis)
time.sleep(20)
#always read GPS - check status = 1

ws1.append(["GPs Test", "elevation - Y axis", ""])
ws1.append(["imuRoll", "imuPitch", "imuYaw", "gps Status", "latitude", "longitude", "altitude"])
#move the engine from -90 to +90 (elevation - Y axis)
time.sleep(20)
#always read GPS - check status = 1
stop_thread = True
t2.join()

me.saveTheWorkBookWithtimestamp()
print('Done !')
