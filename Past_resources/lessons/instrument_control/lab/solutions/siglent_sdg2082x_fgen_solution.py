import time
import pyvisa
import numpy as np

def connect(ip_address):
    """
    Connects to the function generator through the ethernet interface 
    and confirms the connection by printing the instrument ID 

    :param ip_address: str, IP address of the function generator

    :return inst: pyvisa resource
    """
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource(f'TCPIP0::{ip_address}::INSTR') 
    print(inst.query('*IDN?'))
    return inst


def set_wave_type(inst, channel, wave_type):
    """ Set the waveform type using the Basic Wave command.

    :param inst: PyVisa resource object corresponding to the waveform generator.
    :param channel: (int) Channel on which to change the waveform type.
    :param wave_type: (str) one of ['SINE', 'SQUARE', 'RAMP', 'PULSE', 'ARB', 'DC', 'PRBS', 'IQ']
    """
    valid_wave_types = ['SINE', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'ARB', 'DC', 'PRBS', 'IQ']
    if wave_type not in valid_wave_types:
        raise ValueError(f'wave_type must be one of {valid_wave_types}')
    cmd = f'C{channel}:BSWV WVTP,{wave_type}'
    inst.write(cmd)

    
def set_frequency(inst, channel, freq):
    """ Set the waveform fundamental frequency.
    
    :param inst: PyVisa resource object corresponding to the waveform generator.
    :param channel: (int) Channel on which to change the waveform type.
    :param freq: (float) Frequency of the waveform in Hz.
    """
    freq = float(abs(freq))
    freq_min = 1e-6
    freq_max = 1e6
    if not ((freq_min <= freq) and (freq <= freq_max)):
        raise ValueError(f'Specified frequency {freq} falls outside the range {freq_min} <= freq <= {freq_max}')
    cmd = f'C{channel}:BSWV FRQ,{freq}'
    inst.write(cmd)


def set_amplitude(inst, channel, amp):
    """ Set the waveform amplitude in peak-to-peak units.

    :param inst: PyVisa resource object corresponding to the waveform generator.
    :param channel: (int) Channel on which to change the waveform type.
    :param amp: (float) Amplitude of the waveform in volts peak-to-peak.
    """
    amp = float(abs(amp))
    amp_min = 2e-3
    amp_max = 20
    if not ((amp_min <= amp) and (amp <= amp_max)):
        raise ValueError(f'Specified amplitude {amp} falls outside the range {amp_min} <= freq <= {amp_max}')
    cmd = f'C{channel}:BSWV AMP,{amp}'
    inst.write(cmd)


def set_offset(inst, channel, offset):
    """ Set the waveform DC offset.

    :param inst: PyVisa resource object corresponding to the waveform generator.
    :param channel: (int) Channel on which to change the waveform type.
    :param offset: (float) DC offset of the waveform in volts.
    """
    offset = float(offset)
    
    # - first get the amplitude of the waveform - #
    amp = float(get_basic_wave(inst, channel)['AMP'][:-1])
    
    # - the max value of amp/2 + abs(offset) is 10 - #
    offset_check = (amp / 2) + abs(offset)
    max_offset = 10 - (amp / 2)
    if offset_check > 10:
        raise ValueError(f'Specified offset {offset}V exceeds the maximum value {max_offset} for the amplitude {amp}')

    # - set the offset - #
    cmd = f'C{channel}:BSWV OFST,{offset}'
    inst.write(cmd)


def set_channel_state(inst, channel, state):
    """ Set the state of a waveform generator channel to ON or OFF.

    :param inst: Pyvisa resource.
    :param channel: Waveform channel.
    :param state: 'ON' or 'OFF' to specify the state.
    """
    if state not in ['ON', 'OFF']:
        raise ValueError(f'Invalid state {state} specified! Must be "ON" or "OFF"!')
    cmd = f'C{channel}:OUTP {state}'
    inst.write(cmd)


def initialize(inst):
    """ Initialize both channels of the waveform generator to a sine wave with frequency 1 Hz, amplitude 1 Vpp, and offset 0V.
    Turn off both channels

    :param inst: Pyvisa resource.
    """
    for channel in [1, 2]:
        set_channel_state(inst, channel, 'OFF')
        time.sleep(0.2)
        set_wave_type(inst, channel, 'SINE')
        time.sleep(0.2)
        set_frequency(inst, channel, 1)
        time.sleep(0.2)
        set_amplitude(inst, channel, 1)
        time.sleep(0.2)
        set_offset(inst, channel, 0)
        time.sleep(0.2)


def get_basic_wave(inst, channel):
    """ Query the basic waveform parameters and return a dictionary that splits the parameters.

    :param inst: Pyvisa resource.
    :param channel: Waveform generator channel to query.
    """
    query = f'C{channel}:BSWV?'
    bswv = inst.query(query)
    params = bswv.split(' ')[1]
    params_split = params.split(',')
    bswv_params_dict = {
        param: val
        for param, val in zip(params_split[0::2], params_split[1::2])
    }
    
    return bswv_params_dict


def get_channel_state(inst, channel):
    """ Get the current state of a channel.

    :param inst: Pyvisa resource.
    :param channel: Waveform generator channel.
    """
    query = f'C{channel}:OUTP?'
    state_str = inst.query(query)
    params = state_str.split(' ')
    state = params.split(',')[0]

    return state


def create_log(channel, wave_type, freq, amp, offset):
    """ Create a string to log basic parameters of the SDG2082X waveform generator output.

    :param channel: Which channel the parameters correspond to.
    :param wave_type: Type of waveform.
    :param freq: Frequency in Hz.
    :param amp: Amplitude in volts peak-to-peak.
    :param offset: Offset voltage.
    """
    log = "# ------------- SDG2082X Waveform Settings ------------- #\n"
    log += f"Channel: {channel}\n"
    log += f"Waveform Type: {wave_type}\n"
    log += f"Frequency: {freq} Hz\n"
    log += f"Amplitude: {amp} Volts peak-to-peak\n"
    log += f"Offset: {offset} Volts\n"
    return log
    