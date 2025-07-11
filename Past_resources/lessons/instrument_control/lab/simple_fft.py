import numpy as np 

def simple_fft(tsample, x):
    """
    Performs a positive-frequency FFT and returns the magnitude 

    :param tsample: float, sample time in seconds 
    :param x: array-like, data to FFR 
    
    :return f: np.array, frequency array in Hz 
    :return y: np.array, array of FFT magnitudes
    """
    N = len(x) 
    y = np.fft.fft(x) 
    y = 2 * np.abs(y) / N 
    # factor of 2 because signal is split equally between 
    # negative and positive frequency
    f = np.fft.fftfreq(N, d = tsample) 
    f, y = f[:N // 2], y[:N // 2]
    return f, y