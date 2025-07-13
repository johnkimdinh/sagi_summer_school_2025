import numpy as np

def FFT(T, x):
    """ Compute the fft of sampled data.
    
    :param T: Sample period.
    :param x: Data vector.
    """
    N = len(x)
    f = np.fft.fftfreq(N, d=T)
    y = np.fft.fft(x)
    y = np.abs(y) / N
    f, y = f[:N // 2], y[:N // 2] * 2
    return f, y

