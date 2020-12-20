import matplotlib.pyplot as plt
import questplus as qp
from questplus import psychometric_function as pf
import xarray as xr
import numpy as np


p = pf.norm_cdf(intensity=np.arange(10,660,10),
                mean=10,
                sd=3.658,
                lower_asymptote=0.5,
                lapse_rate=0.02,
                scale="linear")
plt.plot(np.squeeze(p))
plt.show()
