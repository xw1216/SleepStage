import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
# rng = np.random.default_rng()
#
# fs = 10e3
# N = 1e5
# amp = 2*np.sqrt(2)
# freq = 1234.0
# noise_power = 0.001 * fs / 2
# time = np.arange(N) / fs
# x = amp*np.sin(2*np.pi*freq*time)
# x += rng.normal(scale=np.sqrt(noise_power), size=time.shape)
#
# f, Pxx_den = signal.periodogram(x, fs)
# plt.semilogy(f, Pxx_den)
# plt.ylim([1e-7, 1e2])
# plt.xlabel('frequency [Hz]')
# plt.ylabel('PSD [V**2/Hz]')
# plt.show()

a: np.ndarray = np.load(r"E:\Workspace\SleepStage\dataset\extract\02\02_wave.npy")
b = np.load(r"E:\Workspace\SleepStage\dataset\standard\02\02_wave.npy")
print((a == b).sum() / a.size)
print('a')

