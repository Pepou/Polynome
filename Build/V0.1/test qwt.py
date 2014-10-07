import numpy as np
import PyQt4.Qwt5.iqt
from PyQt4.Qwt5.qplt import *


x = np.arange(-2*np.pi, 2*np.pi, 0.01)
 
p = Plot(Curve(x, np.cos(x), Pen(Magenta, 2), "cos(x)"),
          Curve(x, np.exp(x), Pen(Red), "exp(x)", Y2),
        Axis(Right, Log),
      "PyQwt using Qwt-%s -- http://qwt.sf.net" % QWT_VERSION_STR)
