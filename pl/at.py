import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import Button, Slider

def f(t, frequency):
    return 5 * np.sin(2 * np.pi * frequency * t)

t = np.linspace(0, 1, 1000)

fig, ax = plt.subplots()
line, = ax.plot(t, f(t, 1), lw=2)
ax.set_xlabel('Time [s]')
fig.subplots_adjust(bottom=0.25)

axfreq = fig.add_axes([0.25, 0.1, 0.65, 0.03])
freq_slider = Slider( ax=axfreq, label='Frequency [Hz]', valmin=1, valmax=10, valstep=1, valinit=1)

def update(val):
    line.set_ydata(f(t, freq_slider.val))
    fig.canvas.draw_idle()

freq_slider.on_changed(update)

plt.show()
