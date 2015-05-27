import os
from ctypes import CDLL, c_int, c_float, c_double, c_void_p, POINTER, byref
from numpy.ctypeslib import ndpointer
import numpy as np


libpath = os.path.join(os.path.dirname(__file__), os.pardir, 'lib', 'lib_rec_filter.so')
lib_rec_filter = CDLL(libpath)

lib_rec_filter._recursive_filter_BP.argtypes = [
        ndpointer(dtype=np.float64), #signal
        ndpointer(dtype=np.float64), #filt_signal
        c_int, #npts
        c_float, #C_HP
        c_float, #C_LP
        POINTER(c_double), #filterH1
        POINTER(c_double), #filterH2
        POINTER(c_double), #filterL1
        POINTER(c_double), #filterL2
        POINTER(c_double), #prev_sample_value
        c_int #memory_sample
        ]
lib_rec_filter._recursive_filter_BP.restype = c_void_p

lib_rec_filter._recursive_filter_HP.argtypes = [
        ndpointer(dtype=np.float64), #signal
        ndpointer(dtype=np.float64), #filt_signal
        c_int, #npts
        c_float, #C_HP
        POINTER(c_double), #filterH1
        POINTER(c_double), #filterH2
        POINTER(c_double), #prev_sample_value
        c_int #memory_sample
        ]
lib_rec_filter._recursive_filter_HP.restype = c_void_p


def recursive_filter(signal, C_HP, C_LP=None, rec_memory=None):
    signal = np.array(signal, dtype=np.float64)
    filt_signal = np.zeros(len(signal))

    if rec_memory is not None:
        filterH1 = rec_memory.filterH1
        filterH2 = rec_memory.filterH2
        filterL1 = rec_memory.filterL1
        filterL2 = rec_memory.filterL2
        prev_sample_value = rec_memory.prev_sample_value
        memory_sample = rec_memory.memory_sample
    else:
        filterH1 = c_double(0)
        filterH2 = c_double(0)
        filterL1 = c_double(0)
        filterL2 = c_double(0)
        prev_sample_value = c_double(0)
        memory_sample = -1

    if C_LP is not None:
        lib_rec_filter._recursive_filter_BP(
            signal, filt_signal, signal.size, C_HP, C_LP,
            byref(filterH1), byref(filterH2),
            byref(filterL1), byref(filterL2),
            byref(prev_sample_value), memory_sample)
    else:
        lib_rec_filter._recursive_filter_HP(
            signal, filt_signal, signal.size, C_HP,
            byref(filterH1), byref(filterH2),
            byref(prev_sample_value), memory_sample)

    if rec_memory is not None:
        rec_memory.filterH1 = filterH1
        rec_memory.filterH2 = filterH2
        rec_memory.filterL1 = filterL1
        rec_memory.filterL2 = filterL2
        rec_memory.prev_sample_value = prev_sample_value

    return filt_signal


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    signal = np.zeros(500)
    signal[100] += 1
    delta = 0.01
    freq = 1.
    Tn = 1./freq
    filter_strength = 1
    wn = Tn/(filter_strength*2*np.pi)
    C_HP = wn/(wn+delta)        # high-pass filter constant
    C_LP = delta/(wn+delta)        # low-pass filter constant
    signal_filt_BP = recursive_filter(signal, C_HP, C_LP)
    signal_filt_BP /= signal_filt_BP.max()
    signal_filt_HP = recursive_filter(signal, C_HP)
    signal_filt_HP /= signal_filt_HP.max()
    plt.plot(signal, label='original')
    plt.plot(signal_filt_BP, label='band-pass')
    plt.plot(signal_filt_HP, label='high-pass')
    plt.legend()
    plt.show()
