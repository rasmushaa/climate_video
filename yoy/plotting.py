import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms
import matplotlib.colors as mcol
import matplotlib.cm as cm
from matplotlib.font_manager import FontProperties
import cv2
import os
import moviepy.editor as mpe
from yoy.line import Line

plt.style.use('dark_background')


class Plotter():
    def __init__(self, data, fps=30.0, dpi=50):
        self.fps = fps
        self.dpi = dpi
        self.path = 'images/'
        self._frame = 0
        self._year = data.iloc[:,0].dt.year.min()
        self._data = data
        self._lines = []

    def add_line(self, n, seconds):
        for i in range(n):
            df_temp = self._data.loc[self._data.iloc[:,0].dt.year == self._year]
            self._lines.append(Line(x=df_temp.iloc[:, 0],
                                    y=df_temp.iloc[:, 1],
                                    segments=self.fps*seconds,
                                    color=(1,0,0,1))
            )
            self._year += 1

    def generate_new_frames(self):
        for i, line in enumerate(self._lines):
            old_data = []
            for old_line in self._lines[0:i]:
                old_data.append(old_line.get_plot_data())
            while line.all_plotted is False:
                x, y, c, a = line.get_plot_data()
                self._new_figure(date=x.iloc[-1])
                self._plot_old_lines(old_data)
                self._plot_line(x, y, c, a)
                self._save_figure()
        self._generate_mp4()

    def _plot_old_lines(self, data_list):
        for data in data_list:
            self._plot_line(data[0], data[1], data[2], data[3])

    def _plot_line(self, x, y, c, a):
        plt.plot(x.dt.dayofyear,
                y, 
                color=c, 
                alpha=a, 
                linewidth=1)  

    def _save_figure(self):
        plt.savefig(f'{self.path}{self._frame:00000000010}.png', dpi=self.dpi)
        plt.close()
        self._frame += 1

    def _generate_mp4(self):
        video_name = 'generated_video'
        music_name = 'music'
        images = [img for img in sorted(os.listdir(self.path)) if img.endswith(".png")]
        frame = cv2.imread(os.path.join(self.path, images[0]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(f'{video_name}.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), self.fps, (width,height))
        for image in images:
            video.write(cv2.imread(os.path.join(self.path, image)))
        cv2.destroyAllWindows()
        video.release()

        videoclip = mpe.VideoFileClip(f'{video_name}.mp4')
        audioclip = mpe.AudioFileClip(f'{music_name}.mp3')
        new_audioclip = mpe.CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(f'{video_name}_sound.mp4')


    def _new_figure(self, date:str):
        plt.figure('YOY Plotter')
        plt.clf()
        plt.gcf().set_size_inches(9, 5.5)
        ax = plt.gca()

        # X axis
        plt.xlim((0,365))
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        plt.xticks(np.linspace(0,335,12), months)
        dx = 20/60.; dy = 0/72. 
        offset = matplotlib.transforms.ScaledTranslation(dx, dy, plt.gcf().dpi_scale_trans)
        for label in ax.xaxis.get_majorticklabels():
            label.set_transform(label.get_transform() + offset)
        font = FontProperties()
        font.set_family('Arial Narrow')
        font.set_weight('light')
        plt.xticks(fontproperties=font, color='grey')
        ax.tick_params(axis='x', which='major', labelsize=13)
        ax.spines['top'].set_linewidth(0)
        ax.spines['bottom'].set_linewidth(2)
        ax.spines['bottom'].set_color('grey')
        ax.tick_params(colors='grey', which='major')

        # Y axis
        plt.ylim(0, 10)
        plt.tick_params(left=False)
        plt.ylabel('Temperature (C)') 
        font = FontProperties()
        font.set_family('Arial')
        font.set_weight('light')
        plt.yticks(fontproperties=font, color='grey')
        ax.tick_params(axis='y', which='major', labelsize=10)
        ax.spines['left'].set_linewidth(0)
        ax.spines['right'].set_linewidth(0)
        plt.ylabel('Temperature (°C)', fontproperties=font, color='gainsboro') 

        # Grid
        for x in np.linspace(30,335,11):
            ax.axvline(x, linestyle='-', color='grey', linewidth=0.8, alpha=0.3)
        for y in np.linspace(0,10,10):
            ax.axhline(y, linestyle='-', color='grey', linewidth=0.8, alpha=0.3)

        font = FontProperties()
        font.set_family('Arial')
        font.set_weight('bold')
        text = 'HELSINKI KAISANIEMI'
        ax.annotate(text,xy = (0.0, 1.2),xycoords='axes fraction',ha='left',va="top",fontsize=22,color='white',fontproperties=font)
        text = f"Daily air temperatures {date:%Y-%m-%d}"
        font = FontProperties()
        font.set_family('Arial')
        font.set_weight('light')
        ax.annotate(text,xy = (0.001, 1.1),xycoords='axes fraction',ha='left',va="top",fontsize=12,color='gainsboro',fontproperties=font)

        font = FontProperties()
        font.set_family('Arial')
        font.set_weight('bold')
        ax.annotate('DATA:',xy = (0.0, -0.13),xycoords='axes fraction',ha='left',va="top",fontsize=8,color='gainsboro',fontproperties=font)
        ax.annotate('SOURCE:',xy = (0.0, -0.18),xycoords='axes fraction',ha='left',va="top",fontsize=8,color='gainsboro',fontproperties=font)
        ax.annotate('GRAPHIC:',xy = (0.82, -0.13),xycoords='axes fraction',ha='left',va="top",fontsize=8,color='gainsboro',fontproperties=font)
        font = FontProperties()
        font.set_family('Arial')
        font.set_weight('light')
        ax.annotate('Finnish Meteorological Institute (FMA)',xy = (0.05, -0.13),xycoords='axes fraction',ha='left',va="top",fontsize=7,color='grey',fontproperties=font)
        ax.annotate('https://www.ilmatieteenlaitos.fi/havaintojen-lataus (2023-09-20)',xy = (0.07, -0.18),xycoords='axes fraction',ha='left',va="top",fontsize=7,color='grey',fontproperties=font)
        ax.annotate('Rasmus Haapaniemi',xy = (0.89, -0.13),xycoords='axes fraction',ha='left',va="top",fontsize=7,color='grey',fontproperties=font)

        plt.tight_layout()