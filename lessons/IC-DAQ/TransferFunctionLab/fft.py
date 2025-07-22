import numpy as np

def FFT(T, x):
    """ Compute the fft of sampled data.
    
    :param T: Sample period.
    :param x: Data vector.
    """
    N = len(x)
    f = np.fft.fftfreq(N, d=T)
    y = np.fft.fft(x) / N
    return f, y

