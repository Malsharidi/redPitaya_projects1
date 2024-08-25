import time
import numpy as np
from matplotlib import pyplot as plt
from rp_overlay import overlay
import rp

fpga = overlay()
rp.rp_Init()

# Generator parameters
channel = rp.RP_CH_1
channel2 = rp.RP_CH_2
waveform = rp.RP_WAVEFORM_SINE
freq = 100000
ampl = 1.0

# Acquisition paramters
dec = rp.RP_DEC_1

trig_lvl = 0.5
trig_dly = 0

acq_trig_sour = rp.RP_TRIG_SRC_NOW
N = 16384

rp.rp_GenReset()
rp.rp_AcqReset()

print("Gen_start")
for i in range(0,20):
    rp.rp_GenWaveform(channel, waveform)
    rp.rp_GenFreqDirect(channel, freq)
    rp.rp_GenAmp(channel, ampl)
    
    rp.rp_GenWaveform(channel2, waveform)
    rp.rp_GenFreqDirect(channel2, freq)
    rp.rp_GenAmp(channel2, ampl)
    
    rp.rp_GenTriggerSource(channel, rp.RP_GEN_TRIG_SRC_INTERNAL)
    
    rp.rp_GenOutEnableSync(True)
    rp.rp_GenSynchronise()
    
    # Set Decimation
    rp.rp_AcqSetDecimation(dec)
    
    # Set trigger level and delay
    rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trig_lvl)
    rp.rp_AcqSetTriggerDelay(trig_dly)
    
    # Start Acquisition
    print("Acq_start")
    rp.rp_AcqStart()
    
    # time.sleep(0.1)
    
    # Specify trigger - immediately
    rp.rp_AcqSetTriggerSrc(acq_trig_sour)
    
    # Trigger state
    while 1:
        trig_state = rp.rp_AcqGetTriggerState()[1]
        if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
            break
    
    # Fill state
    while 1:
        if rp.rp_AcqGetBufferFillState()[1]:
            break
    
    
    ### Get data ###
    # RAW
    ibuff = rp.i16Buffer(N)
    res = rp.rp_AcqGetOldestDataRaw(rp.RP_CH_1, N, ibuff.cast())[1]
    
    # Volts
    fbuff = rp.fBuffer(N)
    res = rp.rp_AcqGetOldestDataV(rp.RP_CH_1, N, fbuff)[1]
    
    data_V = np.zeros(N, dtype = float)
    data_raw = np.zeros(N, dtype = int)
    X = np.arange(0, N, 1)*freq/N
    
    for i in range(0, N, 1):
        data_V[i] = fbuff[i]
        data_raw[i] = ibuff[i]
    
    figure, axis = plt.subplots(1, 2) 
    signal_f = np.fft.fft(data_raw)
    
    axis[0].plot(X/1e6, data_V) 
    axis[0].set_title("Volts")
    
    axis[1].plot(X/1e6, abs(signal_f)) 
    axis[1].set_title("RAW") 
    
    plt.show()
    
    print(data_raw[0:20])
    # Release resources
    rp.rp_Release()

