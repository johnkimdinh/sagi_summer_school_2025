import pyvisa
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from simple_fft import simple_fft

def connect(ip_address = '192.168.2.121'):
    """
    Connects to the oscilloscope through the ethernet interface 
    and confirms the connection by printing the instrument ID 

    :param ip_address: str, IP address of the oscilloscope 

    :return inst: pyvisa resource
    """
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource(f'TCPIP0::{ip_address}::INSTR') 
    print(inst.query('*IDN?'))
    return inst

def set_xscale(inst, xscale):
    """
    Sets the horizontal scale

    :param inst: pyvisa resource
    :param xscale: float, horizontal scale in seconds / div
    """
    inst.write(f'TIME_DIV {xscale}s')
    
def set_xoffset(inst, xoffset):
    """
    Sets the horizontal offset

    :param inst: pyvisa resource
    :param xoffset: float, horizontal scale in seconds
    """
    inst.write(f'HOR_POSITION {xoffset}s')
    
def set_yscale(inst, yscale, channel = 1):
    """
    Sets the vertical scale on the given channel

    :param inst: pyvisa resource
    :param yscale: float, vertical scale in V / div
    :param channel: int, channel index, must be in [1, 2, 3, 4]
    """
    inst.write(f'C{channel}:VOLT_DIV {yscale}V')
    
def set_yoffset(inst, yoffset, channel = 1):
    """
    Sets the vertical offset on the given channel

    :param inst: pyvisa resource
    :param yoffset: float, vertical offset in V
    :param channel: int, channel index, must be in [1, 2, 3, 4]
    """
    inst.write(f'C{channel}:OFFSET {yoffset}v')
    
def set_amplification(inst, amplification, channel = 1):
    """
    Sets the amplification on the given channel

    :param inst: pyvisa resource
    :param amplification: float, amplification
        Must be in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]
    :param channel: int, channel index, must be in [1, 2, 3, 4]
    """
    inst.write(f'C{channel}:ATTENUATION {amplification}')

def set_trigger_mode(inst, mode = 'AUTO'):
    """
    Sets the trigger mode 

    :param inst: pyvisa resource
    :param mode: str, trigger mode
        Must be in ['AUTO', 'NORM', 'SINGLE', 'STOP']
    """
    modes = ['AUTO', 'NORM', 'SINGLE', 'STOP']
    if mode not in modes:
        raise ValueError('Invalid mode')
    inst.write(f'TRIG_MODE {mode}')

def set_channel_state(inst, channel, state):
    """
    Sets the channel state to ON or OFF 

    :param inst: pyvisa resource
    :param channel: int, channel index, must be in [1, 2, 3, 4] 
    :param state: str, channel state, 'ON' or 'OFF'
    """
    inst.write(f'C{channel}:TRACE {state}')

def initialize(inst):
    """ functions
    Initializes the oscilloscope instrument to the following 
    values on every channel 

    xscale        -> 10 us / div
    xoffset       -> 0 s
    yscale        -> 1 V / div 
    yoffset       -> 0 V 
    amplification -> 1X 
    trigger mode  -> AUTO
    """
    set_xscale(inst, 10e-6)
    set_xoffset(inst, 0)
    for ch in range(1, 5):
        set_yscale(inst, 1, channel = ch)
        set_yoffset(inst, 0, channel = ch)
        set_amplification(inst, 1, channel = ch) 
    for ch in range(2, 5):
        set_channel_state(inst, ch, 'OFF')
    set_channel_state(inst, 1, 'ON')
    set_trigger_mode(inst, 'AUTO')

def get_yscale(inst, ch = 1):
    """
    Gets the vertical scale on the given channel

    :param inst: pyvisa resource
    :param ch: int, channel index, must be in [1, 2, 3, 4]

    :return yscale: float, vertical scale in V / div
    """
    response = inst.query(f'C{ch}:VOLT_DIV?')
    response = response.split('VDIV ')[1].replace('V\n', '')
    yscale = float(response)
    return yscale
    
def get_yoffset(inst, ch = 1):
    """
    Gets the vertical offset on the given channel

    :param inst: pyvisa resource
    :param ch: int, channel index, must be in [1, 2, 3, 4]

    :return yoffset: float, vertical offset in V
    """
    response = inst.query(f'C{ch}:OFFSET?')
    response = response.split('OFST ')[1].replace('V\n', '')
    yoffset = float(response)
    return yoffset

def get_xscale(inst):
    """
    Gets the horizontal scale

    :param inst: pyvisa resource
    
    :return xscale: float, horizontal scale in seconds / div
    """
    response = inst.query('TIME_DIV?')
    response = response.split('TDIV ')[1].replace('S\n', '')
    xscale = float(response)
    return xscale
    
def get_xoffset(inst):
    """
    Gets the horizontal offset

    :param inst: pyvisa resource
    
    :return xoffset: float, horizontal scale in seconds
    """
    response = inst.query('HOR_POSITION?')
    response = response.split('HPOS ')[1].replace('S\n', '')
    xoffset = float(response)
    return xoffset

def get_amplification(inst, ch = 1):
    """
    Gets the amplification on the given channel

    :param inst: pyvisa resource
    :param ch: int, channel index, must be in [1, 2, 3, 4]

    :return amplification: float, amplification
    """
    response = inst.query(f'C{ch}:ATTENsiglent_sds1104xeUATION?')
    response = response.split('ATTN ')[1].replace('\n', '')
    amplification = float(response)
    return amplification

def get_trigger_mode(inst):
    """
    Gets the trigger mode 

    :param inst: pyvisa resource
    
    :return mode: str, trigger mode
    """
    response = inst.query('TRIG_MODE?')
    response = response.split('TRMD ')[1].replace('\n', '')
    mode = response
    return mode

def get_channel_state(inst, channel):
    """
    Gets the channel state to ON or OFF 

    :param inst: pyvisa resource
    :param channel: int, channel index, must be in [1, 2, 3, 4] 
    
    :return state: str, channel state, 'ON' or 'OFF'
    """
    response = inst.query(f'C{channel}:TRACE?')
    state = response.split('TRA ')[1].replace('\n', '')
    return state

def create_log(xscale, xoffset, yscale, yoffset, 
               amplification, trigger_mode):
    """
    Creates a log file to keep track of the 
    oscilloscope parameters

    :param xscale: float, horizontal scale in seconds / div
    :param xoffset: float, horizontal scale in seconds
    :param yscale: float, vertical scale in V / div
    :param yoffset: float, vertical offset in V
    :param amplification: float, amplification
    :param trigger_mode: str, trigger mode
    """
    log = "# ---------------- SIGLENT SDS 1104X-E ----------------- #\n" 
    log += f'xscale: {xscale} s / div\n'
    log += f'xoffset: {xoffset} s\n'
    log += f'yscale: {yscale} V / div\n'
    log += f'yoffset: {yoffset} V\n'
    log += f'amplification: {amplification}X\n'
    log += f'trigger mode: {trigger_mode}\n'
    return log 

def capture_data(inst):
    """
    Captures data from the most recent trigger 

    :param inst: pyvisa resource

    :return tsample: sample time in seconds 
    :return time: np.array, time array in seconds
    :return voltage: np.array, voltage array in V
    """
    try:
        fsample = inst.query('SARA?')
    except:
        sleep(0.2)
        fsample = inst.query('SARA?')
    fsample = float(fsample.split(' ')[1].replace('Sa/s\n', ''))
    tsample = 1 / fsample

    vdiv = get_yscale(inst)
    voffset = get_yoffset(inst)

    sleep(0.2)
    raw_data = inst.query_binary_values('C1:WF? DAT2', datatype = 'B')
    data = []
    for d in raw_data:
        if d > 127:
            data.append(d - 256)
        else:
            data.append(d)
    voltage = [d * (vdiv / 25) - voffset for d in data]

    time = np.arange(0, tsample * len(voltage), tsample)
    voltage = np.array(voltage)
    return tsample, time, voltage

