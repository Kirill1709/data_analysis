import os
import tkinter as tk
from configparser import ConfigParser
from tkinter.filedialog import askopenfilename

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from idlelib.tooltip import ToolTip
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from scipy.signal import savgol_filter

CONFIG = 'config.ini'


root = tk.Tk()
root.title("Программа расчета частоты сигнала")
root.configure(bg='#EEE9E9')
root.state('zoomed')

SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight() - 60
GRAPH_COORD_X = SCREEN_WIDTH / 5
GRAPH_COORD_Y = 0

test_x = [0, 20, 50, 100, 200] * 50
test_y = [0, 2, 5, 9, 21] * 50
test_z = [10, 20, 50, 40, 150] * 50


class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=False)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP)  # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="White", padx=2)
        s.pack(side=tk.TOP, pady=5)  # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass


def do_plot1():
    plt.close()
    fig, ax1 = plt.subplots()
    ax1.plot(time, consumption, 'blue', label='Расходная характеристика')
    ax2 = ax1.twinx()
    ax2.plot(time, temperature, 'orange', label='Температурная характеристика')
    asd = np.convolve(consumption, np.ones(
        int(ent3.get())) / int(ent3.get()), mode='valid')
    ax1.plot(time[:len(asd)], asd * (1 + (int(ent6.get()) / 100)),
             'brown', label='Граница амплитуды')
    ax1.plot(time[:len(asd)], asd * (1 - (int(ent6.get()) / 100)), 'brown')
    ax1.set_xlabel("Время, сек", fontsize=14, fontname='Times New Roman')
    ax1.set_ylabel("Расход, мл/мин", fontsize=14, fontname='Times New Roman')
    ax2.set_ylabel(
        '$\\mathregular{U_{тд},мВ}$',
        fontsize=14,
        fontname='Times New Roman')
    plt.show()


def do_plot2():
    plt.close()
    yhat = savgol_filter(
        consumption, int(
            ent1.get()), int(
            ent2.get()), mode='interp')
    asd = np.convolve(yhat, np.ones(int(ent3.get())) /
                      int(ent3.get()), mode='valid')
    plt.plot(time, yhat, 'blue')
    plt.plot(time[:len(asd)], asd, 'red')
    plt.xlabel("Время, сек", fontsize=14, fontname='Times New Roman')
    plt.ylabel("Расход, мл/мин", fontsize=14, fontname='Times New Roman')
    plt.show()


def graph_1(
        time,
        consumption,
        temperature,
        color='white',
        color_amplitude='white',
        color_temperature='white',
        status=False):
    global canvas_1
    figure_1 = Figure()
    canvas_1 = FigureCanvasTkAgg(figure_1, master=root)
    canvas_1.get_tk_widget().place(
        x=GRAPH_COORD_X,
        y=0,
        width=SCREEN_WIDTH -
        GRAPH_COORD_X,
        height=SCREEN_HEIGHT / 2 - 50)
    ax_1 = figure_1.add_subplot()
    ax_1.set_title(
        "График исследования амплитуды",
        fontsize=15,
        fontname='Times New Roman')
    ax_1.plot(time, consumption, color, label='Расходная характеристика')
    ax_3 = ax_1.twinx()
    ax_3.plot(time, temperature, color_temperature, label='Кривая температуры')
    asd = np.convolve(consumption, np.ones(
        int(ent3.get())) / int(ent3.get()), mode='valid')
    ax_1.plot(time[:len(asd)],
              asd * (1 + (int(ent6.get()) / 100)),
              color_amplitude,
              label='Граница амплитуды')
    ax_1.plot(time[:len(asd)],
              asd * (1 - (int(ent6.get()) / 100)),
              color_amplitude)
    if status:
        figure_1.legend(bbox_to_anchor=(0.88, 0.88), fontsize='x-small')
    try:
        ax_1.fill_between([time[section[0]], time[section[1]]], min(
            consumption), max(consumption), color='green', alpha=0.2)
    except Exception:
        pass
    canvas_1.draw()
    toolbar_1 = VerticalNavigationToolbar2Tk(canvas_1, root)
    toolbar_1.update()
    toolbar_1.place(x=SCREEN_WIDTH / 1.05, y=SCREEN_HEIGHT / 20 - 10)
    toolbar_1.config(background='white')
    btplot1 = tk.Button(root, text='Подробнее', command=do_plot1)
    btplot1.place(
        x=SCREEN_WIDTH /
        1.07,
        y=SCREEN_HEIGHT /
        2 -
        SCREEN_HEIGHT /
        10 -
        10,
        width=80,
        height=30)
    ax_1.set_xlabel("Время, сек", fontsize=14, fontname='Times New Roman')
    ax_1.set_ylabel("Расход, мл/мин", fontsize=14, fontname='Times New Roman')
    ax_3.set_ylabel(
        '$\\mathregular{U_{тд},мВ}$',
        fontsize=14,
        fontname='Times New Roman')
    figure_1.subplots_adjust(
        left=None,
        bottom=0.152,
        right=0.88,
        top=None,
        wspace=None,
        hspace=None)
    if max(time) > 100:
        ax_1.xaxis.set_major_locator(
            matplotlib.ticker.MultipleLocator(
                base=round(
                    max(time) // 16, -1)))
    if max(temperature) > 100:
        ax_3.yaxis.set_major_locator(
            matplotlib.ticker.MultipleLocator(
                base=round(
                    max(time) // 10, -1)))


def graph_2(time, consumption, color_average='white',
            color_smooth='white', color_bound='white', status=False):
    global canvas_2, ax_2, yhat
    error_parameters()
    figure_2 = Figure()
    canvas_2 = FigureCanvasTkAgg(figure_2, master=root)
    canvas_2.get_tk_widget().place(
        x=GRAPH_COORD_X,
        y=SCREEN_HEIGHT / 2 - 50,
        width=SCREEN_WIDTH - GRAPH_COORD_X,
        height=SCREEN_HEIGHT / 2 + 50)
    ax_2 = figure_2.add_subplot()
    ax_2.set_title(
        "График исследования частоты",
        fontsize=15,
        fontname='Times New Roman')
    yhat = savgol_filter(
        consumption, int(
            ent1.get()), int(
            ent2.get()), mode='interp')
    asd = np.convolve(yhat, np.ones(int(ent3.get())) /
                      int(ent3.get()), mode='valid')
    ax_2.plot(time[:len(asd)], asd, color_average, label='Скользящая средняя')
    ax_2.plot(time, yhat, color_smooth, label='Сглаженный график')
    ax_2.set_xlabel("Время, сек", fontsize=14, fontname='Times New Roman')
    ax_2.set_ylabel("Расход, мл/мин", fontsize=14, fontname='Times New Roman')
    figure_2.subplots_adjust(
        left=None,
        bottom=0.15,
        right=None,
        top=0.87,
        wspace=None,
        hspace=None)
    if max(time) > 100:
        ax_2.xaxis.set_major_locator(
            matplotlib.ticker.MultipleLocator(
                base=round(
                    max(time) // 16, -1)))
    canvas_2.draw()
    toolbar_2 = VerticalNavigationToolbar2Tk(canvas_2, root)
    toolbar_2.update()
    toolbar_2.place(
        x=SCREEN_WIDTH /
        1.05,
        y=SCREEN_HEIGHT /
        20 +
        SCREEN_HEIGHT /
        2)
    toolbar_2.config(background='white')
    btplot2 = tk.Button(root, text='Подробнее', command=do_plot2)
    btplot2.place(
        x=SCREEN_WIDTH /
        1.07,
        y=SCREEN_HEIGHT -
        SCREEN_HEIGHT /
        10,
        width=80,
        height=30)
    canvas_2.mpl_connect('button_press_event', onclick)
    try:
        ax_2.fill_between([time[section[0]], time[section[1]]], min(
            yhat), max(yhat), color='green', alpha=0.2)
    except Exception:
        pass
    freq_moving_user(ax_2, time, asd, yhat, color_bound, status)


def onclick(event):
    if event.button != 3:
        raise Exception("Не та кнопка")
    x_data = event.xdata

    def is_left():
        return line_1.get_xdata()[0] < line_2.get_xdata()[0]

    if len(ax_2.lines) == 4:
        line_1 = ax_2.lines[2]
        line_2 = ax_2.lines[3]
        if abs(
                line_1.get_xdata()[0] -
                x_data) <= abs(
                line_2.get_xdata()[0] -
                x_data):
            if is_left():
                ent4.delete(0, tk.END)
                ent4.insert(0, f'{round(x_data, 1)}')
            else:
                ent5.delete(0, tk.END)
                ent5.insert(0, f'{round(x_data, 1)}')
            line_1.remove()
        else:
            if not is_left():
                ent4.delete(0, tk.END)
                ent4.insert(0, f'{round(x_data, 1)}')
            else:
                ent5.delete(0, tk.END)
                ent5.insert(0, f'{round(x_data, 1)}')
            line_2.remove()
        ax_2.plot([x_data, x_data], [min(yhat), max(yhat)],
                  color='orange', label='Left')
    elif len(ax_2.lines) == 2:
        ent4.delete(0, tk.END)
        ent4.insert(0, f'{round(x_data, 1)}')
        ax_2.plot([x_data, x_data], [min(yhat), max(yhat)],
                  color='orange', label='Left')
    elif len(ax_2.lines) == 3:
        if x_data > float(ent4.get()):
            ent5.delete(0, tk.END)
            ent5.insert(0, f'{round(x_data, 1)}')
        else:
            ent5.delete(0, tk.END)
            ent5.insert(0, f'{ent4.get()}')
            ent4.delete(0, tk.END)
            ent4.insert(0, f'{round(x_data, 1)}')
        ax_2.plot([x_data, x_data], [min(yhat), max(yhat)],
                  color='orange', label='Right')
    canvas_2.draw()


def error_parameters():
    ent_1 = int(ent1.get()) + 1
    if int(ent1.get()) % 2 == 0:
        ent1.delete(0, tk.END)
        ent1.insert(0, ent_1)
    if int(ent1.get()) <= int(ent2.get()):
        diff = int(ent2.get()) - int(ent1.get()) + 1
        ent1.delete(0, tk.END)
        ent1.insert(0, ent_1 + diff)
    if int(ent3.get()) <= 0:
        ent3.delete(0, tk.END)
        ent3.insert(0, 30)


def rebuild():
    error_parameters()
    while len(ax_2.lines) > 2:
        ax_2.lines[-1].remove()
    graph_1(time, consumption, temperature, 'blue', 'brown', 'orange', True)
    graph_2(time, consumption, 'red', 'blue', 'black', True)


def binarySearch(arr, x, left, right, l_point, r_point):
    if right <= left:
        graph_2(time, consumption, 'red', 'blue', 'black', True)
        return tk.messagebox.showerror('Ошибка', 'Такого значения не найдено')
    mid = (left + right) // 2
    if x * l_point <= arr[mid] <= x * r_point:
        return mid
    elif x < arr[mid]:
        return binarySearch(arr, x, left, mid, l_point, r_point)
    else:
        return binarySearch(arr, x, mid + 1, right, l_point, r_point)


def freq_moving_user(ax_2, time, asd, yhat, color, status):
    if status:
        begin = left = section[0]
        right = section[1]
    else:
        begin = left = binarySearch(time, float(
            ent4.get()), 0, len(time) - 1, 0.98, 1)
        right = binarySearch(
            time,
            float(
                ent5.get()),
            0,
            len(time) - 1,
            1,
            1.02)
        ax_2.plot([time[begin], time[begin]], [
                  min(yhat), max(yhat)], color=color)
        ax_2.plot([time[right], time[right]], [
                  min(yhat), max(yhat)], color=color)
    list_av = []
    freq_list = []
    while left <= right:
        if (yhat[left] < asd[left] < yhat[left + 1] or
                yhat[left] > asd[left] > yhat[left + 1]):
            list_av.append(time[left])
        if len(list_av) == 3:
            freq_list.append(1 / (list_av[2] - list_av[0]))
            list_av = [time[left]]
        left += 1
    if len(freq_list) == 0:
        freque = 0
    else:
        freque = round(sum(freq_list) / len(freq_list), 2)
        ax_2.text(time[((begin + right) // 2)],
                  max(yhat),
                  f'{freque} Гц',
                  fontsize=9,
                  color='black',
                  horizontalalignment='center')
        ax_2.legend(bbox_to_anchor=(0.82, 1), fontsize='x-small')


def segment_value():
    graph_2(time, consumption, 'red', 'blue', 'black', False)


def load_data():
    global time, consumption, section, temperature
    txt = open(askopenfilename())
    time = []
    consumption = []
    section = []
    temperature = []
    for i, row in enumerate(txt):
        try:
            value = list(map(float, row.replace(',', '.').split()))
            time.append(value[0])
            consumption.append(value[1])
            temperature.append(value[2])
            if value[4] == 2000:
                section.append(i + 1)
        except Exception:
            pass
    if len(section) != 0:
        section = [section[1], section[-1]]
    graph_1(time, consumption, temperature, 'blue', 'brown', 'orange', True)
    graph_2(time, consumption, 'red', 'blue', 'black', True)


def freq():
    yhat = savgol_filter(consumption, 31, 1)
    spectrum = np.fft.fft(yhat)
    amplitude = np.abs(spectrum) * (1 / len(spectrum))
    amplitude = amplitude / amplitude[10]
    freq = np.fft.fftfreq(len(spectrum), time[1] - time[0])
    plt.plot(freq[10:int(len(yhat) / 2)], amplitude[10:int(len(yhat) / 2)])
    plt.xlabel("Частота, Гц", fontsize=14, fontname='Times New Roman')
    plt.ylabel("Амплитуда", fontsize=14, fontname='Times New Roman')
    plt.show()


def on_close():
    plt.close()
    config = ConfigParser()
    if os.path.exists(CONFIG):
        config.read(CONFIG)
    else:
        config.add_section("parameters")
    config['parameters']['ent1'] = str(ent1.get())
    config['parameters']['ent2'] = str(ent2.get())
    config['parameters']['ent3'] = str(ent3.get())
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    root.destroy()


btplot4 = tk.Button(root, text='Загрузка', command=load_data)
btplot4.place(x=10, y=10, width=80, height=40)
btplot5 = tk.Button(root, text='Перестроить', command=rebuild)
btplot5.place(x=20, y=200, width=100, height=30)
btplot6 = tk.Button(root, text='Частота', command=freq)
btplot6.place(x=20, y=290, width=100, height=30)
btplot7 = tk.Button(root, text='Вычислить', command=segment_value)
btplot7.place(x=20, y=400, width=100, height=30)
ent1 = tk.Entry(root, bd=2)
ent1.place(x=20, y=100, width=45, height=25)
ent2 = tk.Entry(root, bd=2)
ent2.place(x=20, y=130, width=45, height=25)
ent3 = tk.Entry(root, bd=2)
ent3.place(x=20, y=160, width=45, height=25)
ent4 = tk.Entry(root, bd=2)
ent4.place(x=20, y=360, width=45, height=25)
ent4.insert(0, '0')
ent5 = tk.Entry(root, bd=2)
ent5.place(x=100, y=360, width=45, height=25)
ent5.insert(0, '0')
ent6 = tk.Entry(root, bd=2)
ent6.place(x=20, y=500, width=45, height=25)
ent6.insert(0, '10')
lab1 = tk.Label(root, text='Период сглаживания', font='Times 12')
lab1.place(x=70, y=100)
lab1.configure(bg='#EEE9E9')
lab2 = tk.Label(root, text='Порядок полинома', font='Times 12')
lab2.place(x=70, y=130)
lab2.configure(bg='#EEE9E9')
lab3 = tk.Label(root, text='Период скользящей средней', font='Times 12')
lab3.place(x=70, y=160)
lab3.configure(bg='#EEE9E9')
lab4 = tk.Label(
    root,
    text='Представление сигнала в частотной области',
    font='Times 13',
    wraplength=250)
lab4.place(x=20, y=240)
lab4.configure(bg='#EEE9E9')
lab5 = tk.Label(root, text='Параметры графика', font='Times 13')
lab5.place(x=20, y=60)
lab5.configure(bg='#EEE9E9')
lab6 = tk.Label(root, text='Вычисление частоты отрезка', font='Times 13')
lab6.place(x=20, y=330)
lab6.configure(bg='#EEE9E9')
lab7 = tk.Label(root, text='Отклонение амплитуды от средней', font='Times 13')
lab7.place(x=20, y=450)
lab7.configure(bg='#EEE9E9')
lab8 = tk.Label(root, text='%', font='Times 13')
lab8.place(x=70, y=500)
lab8.configure(bg='#EEE9E9')
ToolTip(ent1, 'Нечетное число больше нуля')
ToolTip(ent2, 'Порядок полинома должен быть меньше периода сглаживания')
ToolTip(ent3, 'Период скользящей средней должен быть больше нуля')


if __name__ == "__main__":
    try:
        config = ConfigParser()
        config.read(CONFIG)
        ent1.insert(0, f"{config['parameters']['ent1']}")
        ent2.insert(0, f"{config['parameters']['ent2']}")
        ent3.insert(0, f"{config['parameters']['ent3']}")
        print(int(ent1.get()), int(ent2.get()), int(ent3.get()))
    except BaseException:
        ent1.delete(0, tk.END)
        ent2.delete(0, tk.END)
        ent3.delete(0, tk.END)
        ent1.insert(0, '15')
        ent2.insert(0, '2')
        ent3.insert(0, '15')
    graph_1(test_x, test_y, test_z)
    graph_2(test_x, test_y)
    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()
