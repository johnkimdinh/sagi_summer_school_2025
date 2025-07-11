from time import sleep
import numpy as np 

class ResourceManager:
    def __init__(self):
        pass 
    
    def open_resource(self, address):
        return Resource(address)

class Resource:
    def __init__(self, address):
        if address != f'TCPIP0::192.168.2.125::INSTR':
            sleep(5)
            raise VisaIOError('VI_ERROR_RSRC_NFOUND (-1073807343): Insufficient location information or the requested device or resource is not present in the system.')
        self.yscale = 1
    
    def query(self, message):
        if message == '*IDN?':
            return 'SAGI Technologies fake oscilloscope'
        elif ':WF? DAT2' in message:
            try:
                channel = int(message.split(':')[0].replace('C', ''))
                if channel != 1:
                    return 'data requested on the wrong channel'
                else:
                    data = self.get_data() 
                    return data
            except:
                sleep(5)
                raise VisaIOError('VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.') 
        elif message == 'SARA?':
            return 'SARA 0.001Sa/s\n'
        else:
            sleep(5)
            raise VisaIOError('VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.')
        
    def write(self, message):
        if ':VOLT_DIV ' in message and message[-1] == 'V':
            try:
                channel = int(message.split(':')[0].replace('C', ''))
                yscale = float(message.split(' ')[1].replace('V', ''))
                if channel != 1:
                    return f'yscale set to {yscale} V on the wrong channel'
                self.yscale = yscale
                return f'yscale set to {self.yscale} V on channel 1'
            except:
                return 'nothing happened'
        else:
            return 'nothing happened'

    def get_data(self):
        fsample = 1000 # 1 kHz 
        tsample = 1 / fsample
        time = np.arange(0, 1, tsample)
        frequency = 88
        amplitude = 0.1
        delta = np.random.uniform(-np.pi, np.pi)
        x = amplitude * np.sin(2 * np.pi * time * frequency + delta)
        noise = 6 * amplitude * np.random.normal(-1, 1, len(time))
        x += noise
        x -= np.mean(x)
        x[x > self.yscale] = self.yscale 
        x[x < -self.yscale] = -self.yscale 
        return x
        
    
class VisaIOError(Exception):
    pass