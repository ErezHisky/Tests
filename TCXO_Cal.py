import logging
import time
from datetime import datetime
from Drivers.ExcelCtrl import *
from Drivers.Terminal.SendDataMsg import *
from Drivers.Terminal.ReadEthData import *
from Tests.commFunctions import *
from Drivers.StepEngineCtrl import *
from Drivers.DigAtt64bit import *
from Drivers.Spectrum_bb60c import *
from Drivers.SigGenCtrl import *



iCD = Drivers.Terminal.iCDs
rcvD = ReceiveData()
all_strck = icd_strucks()
rcvD.send_receive_order()
sdm = Send_The_Data()
stop_thread = False
me = MyExcel()
ws1 = me.my_sheet
myAtt = DigAtt64()
#mySig = MySignalGenerator()
Signal_freq = 26.0
'''mySig.changeFreq(Signal_freq)
mySig.changeAmp(10.0)
mySig.turnRfOn()
mySig.turnModOff()'''
# my_eng = MyStepEngine("azimuth")



# ipusAll()

my_date = datetime.datetime.now().date()
t = time.localtime()
current_time = time.strftime("%H_%M_%S", t)
logging.basicConfig(filename=f"D:/TesterLogs/TesterLog_{my_date}_{current_time}.txt", level=logging.DEBUG)

#DigAtt - 30dB (for SA protection)
myAtt.set_attenuation(30.0)

# turn on tx
print("turning Tx on...")
all_strck.MxFEAxiRegMsg["data"] = 0x7
sdm.send_the_message("MxFEAxiRegMsg", all_strck.MxFEAxiRegMsg)
time.sleep(1)
unit_Freq = 29000
all_strck.Lmx2592FreqMsg["val"] = unit_Freq
sdm.send_the_message("Lmx2592FreqMsg", all_strck.Lmx2592FreqMsg)
time.sleep(1)

# transmit LO (MB register)
print("turn LO on...")
all_strck.MxFEAxiRegMsg["addr"] = 0x71
all_strck.MxFEAxiRegMsg["data"] = 0x0
sdm.send_the_message("MxFEAxiRegMsg", all_strck.MxFEAxiRegMsg)
time.sleep(1)
# turn off modem (PIC register)
print("turn off modem...")
all_strck.PICReadWriteMsg["opcode"] = iCD.PIC_REG_SET_GET
all_strck.PICReadWriteMsg["addr"] = 4
all_strck.PICReadWriteMsg["data"] = 0x708
sdm.send_the_message("PICReadWriteMsg", all_strck.PICReadWriteMsg)
time.sleep(1)

#DigAtt - 5dB
myAtt.set_attenuation(5.0)


# check freq precision
# peak search in narrow span
print("configure bb60c sa...")
mybb60csa = bb60c_scpi()
span = 20.0*1e3
sa_results = mybb60csa.get_peak_search(3.0*1e9, span)
logging.info(sa_results)
expected_freq_in_sa = unit_Freq/1000 - Signal_freq
logging.debug(sa_results[0] - expected_freq_in_sa * 1e9)
print(sa_results[0] - expected_freq_in_sa * 1e9)

print("taking results...")
for n in range(0,20):
    val2Dac = 1000 + n*1000
    all_strck.clkDacMsg["val"] = val2Dac
    print(f"value to clkDacMsg = {val2Dac}")
    sdm.send_the_message("clkDacMsg", all_strck.clkDacMsg)
    sa_results = mybb60csa.get_peak_search(expected_freq_in_sa*1e9, span)
    tcxo_res = sa_results[0] - expected_freq_in_sa * 1e9
    print(tcxo_res)
    logging.info(tcxo_res)

# turn Tx off
print("turning tx off...")
time.sleep(1)
all_strck.MxFEAxiRegMsg["addr"] = 0x17
all_strck.MxFEAxiRegMsg["data"] = 0x3
sdm.send_the_message("MxFEAxiRegMsg", all_strck.MxFEAxiRegMsg)

mybb60csa.close_spike()

#save results to excel
print("saving to excel...")
ws1.append(["clkDac val", "Tpc", "Dig Temp", "X", "Y"])
ws1.append([val2Dac, "", "", "", ""])
me.saveTheWorkBookWithtimestamp()
print("Done !")