import numpy as np
import pandas as pd

class Line():
    def __init__(self, x:pd.Series, y:pd.Series, segments:int, color:tuple, alpha:float=1.0, decay:float=11):
        assert x.size == y.size
        assert len(color) == 4
        self.x = x
        self.y = y
        self._segments = segments
        self._color = color
        self._alpha = alpha
        self._plot_count = 1
        self._decay = decay
        self._alpha_limit = 0.15
        self.all_plotted = False

    def get_plot_data(self):
        if self._plot_count < self._segments:
            x = self.x.iloc[0:round((self._plot_count/self._segments)*self.x.size)]
            y = self.y.iloc[0:round((self._plot_count/self._segments)*self.y.size)]
            self._plot_count += 1
            return x, y, self._color, self._alpha
        else:
            x = self.x
            y = self.y
            if self._alpha > self._alpha_limit:
                self._alpha = np.exp(-(self._plot_count-self._segments)/self._decay)
            self.all_plotted = True
            self._plot_count += 1
            return x, y, self._color, self._alpha
