import random
from tkinter import Tk, Button, Label, Text, DISABLED, NORMAL, END, Checkbutton, BooleanVar
import tkinter.filedialog as fd
from tkinter.ttk import Combobox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def read_crv_file(f):
    with open(f, 'r') as f:
        f.readline()
        f.readline()
        disc = f.readline()
        disc = float(disc[17:-3].replace(',', '.'))
        f.readline()
        f.readline()
        arr = [[int(item) for item in line.split()] for line in f]
    return disc, arr


class Application(Tk):

    def __init__(self):
        super().__init__()
        self.btn_file = None
        self.btn_entire_ekg = None
        self.btn_middle_ekg = None
        self.label_filename = None
        self.combo_box = None
        self.label_side = None
        self.text_field = None
        self.is_moving = False
        self.current_line = None
        self.points = []
        self.figure = Figure(figsize=(12, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.plot = self.figure.add_subplot(111)
        self.current_graph = None
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.var_points = BooleanVar()
        self.var_lines = BooleanVar()
        self.check_btn_points = Checkbutton(self, variable=self.var_points,
                                            onvalue=1, offvalue=0)
        self.check_btn_lines = Checkbutton(self, variable=self.var_lines,
                                           onvalue=1, offvalue=0)
        self.btn_save_RR_PP = Button(self)
        self.fileName = ''
        self.RR_period_list = []
        self.PP_period_list = []
        self.rr_list = []
        self.r_list = []
        self.s_list = []
        self.t_list = []
        self.p_list = []
        self.x_list = []
        self.p_markers = []
        self.t_markers = []
        self.qrs_markers = []
        self.y_list = {1: [], 2: [], 3: []}
        self.disc = 0
        self.current_side = 1
        self.initUI()

    def centerWindow(self):

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        w = sw
        h = sh

        x = (sw - w) / 2
        y = (sh - h) / 2
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
        self.title('EKG')
        self.centerWindow()
        self.btn_file = Button(self, text="Выбрать файл",
                               command=self.choose_file,
                               font=('Times', '12'),
                               width=12)
        self.btn_file.place(x=20, y=20)
        self.btn_entire_ekg = Button(self, text="Показать ЭКГ",
                                     command=self.show_ekg,
                                     font=('Times', '12'),
                                     width=12)
        self.btn_entire_ekg.place(x=20, y=70)
        self.btn_middle_ekg = Button(self, text="Усреднённый комплекс",
                                     command=self.show_middle_complex,
                                     font=('Times', '12'),
                                     width=18)
        self.btn_middle_ekg.place(x=150, y=70)
        self.label_filename = Label(self, text='Файл не выбран',
                                    font=('Times', '12'),
                                    )
        self.label_filename.place(x=150, y=20)
        self.btn_save_RR_PP = Button(self, text="Сохранить RR и PP",
                                     command=self.save_RR_PP,
                                     font=('Times', '12'),
                                     width=14)
        self.btn_save_RR_PP.place(x=20, y=600)
        self.combo_box = Combobox(self, values=[1, 2, 3], font=("Times", 12), width=12, state="readonly")
        self.combo_box.set('Отведение')
        self.combo_box.bind("<<ComboboxSelected>>", self.change_side)
        self.combo_box.place(x=150, y=120)
        self.label_side = Label(self, text='Отведение №', font=("Times", 12))
        self.label_side.place(x=20, y=120)
        self.toolbar.place(x=350, y=700)
        self.canvas.draw()
        self.plot.grid()
        self.canvas.get_tk_widget().place(x=350, y=0)
        btn_save = Button(self, text='Сохранить параметры', command=self.save_params, font=('Times', '12'),
                          width=28)
        btn_save.place(x=20, y=150)
        self.text_field = Text(self, width=35, height=20, bg="white",
                               fg='black', state=DISABLED)
        self.text_field.place(x=20, y=200)
        self.check_btn_points.config(text='Пики зубцов')
        self.check_btn_points.place(x=20, y=540)
        self.check_btn_lines.config(text='Периоды')
        self.check_btn_lines.place(x=20, y=560)

    def write_params(self):
        string = 'Усреднённые параметры: \n P = ' + str(self.s_a_P()) + 'мВ\n R = ' + str(
            self.s_a_R()) + 'мВ\n S = ' + str(self.s_a_S()) + 'мВ\n T = ' + str(self.s_a_T()) + 'мВ\n P = ' + str(
            self.s_period_P()) + 'мс\n RS = ' + str(self.s_period_RS()) + 'мс\n T = ' + str(
            self.s_period_T()) + 'мс\n PR = ' + str(self.s_period_PR()) + 'мс\n ST = ' + str(self.s_period_ST()) + 'мс'
        self.text_field.config(state=NORMAL)
        self.text_field.delete(1.0, END)
        self.text_field.insert(END, string)
        self.text_field.config(state=DISABLED)

    def choose_file(self):
        filename = fd.askopenfilename(title="Выбрать файл", initialdir=".\\",
                                      filetypes=(('TXT File', '*.crv'), ("All Files", "*")))
        if filename:
            self.fileName = filename
            s = [x for x in filename.split("/")]
            self.label_filename.config(text=s[len(s) - 1])
            self.set_y_x()
        else:
            self.label_filename.config(text="Файл не выбран")

    def save_params(self):
        filename = fd.asksaveasfilename(title="Выбрать файл", initialdir="D:\\",
                                        filetypes=(('TXT File', '*.txt'), ("All Files", "*")))
        if filename != '':
            f = open(filename, 'w')
            s = self.text_field.get(1.0, END)
            s += '\n'
            for x in range(64):
                s += str(self.p_list[x][1]) + ', ' + str(self.r_list[x][1]) + ', ' + str(
                    self.s_list[x][1]) + ', ' + str(self.t_list[x][1]) + '\n'
            s += 'Все значения \n'
            for x in range(len(self.y_list[self.current_side])):
                s += str(self.y_list[1][x]) + ', ' + str(self.y_list[2][x]) + ', ' + str(self.y_list[3][x]) + '\n'
            f.write(s)
            f.close()

    def change_side(self, event):
        self.current_side = int(self.combo_box.get())

    def s_a_P(self):
        res = 0
        for item in self.p_list:
            res += item[1]
        return res / len(self.p_list)

    def s_period_P(self):
        res = 0
        for item in self.p_markers:
            res += item[1] - item[0]
        return res / len(self.p_markers)

    def s_period_RS(self):
        res = 0
        for item in self.qrs_markers:
            res += item[1] - item[0]
        return res / len(self.qrs_markers)

    def s_period_PR(self):
        res = 0
        for item in self.qrs_markers:
            res += item[0]
        for item in self.p_markers:
            res -= item[1]
        return res / len(self.qrs_markers)

    def s_period_ST(self):
        res = 0
        for item in self.qrs_markers:
            res -= item[1]
        for item in self.t_markers:
            res += item[0]
        return res / len(self.qrs_markers)

    def s_period_T(self):
        res = 0
        for item in self.t_markers:
            res += item[1] - item[0]
        return res / len(self.t_markers)

    def s_a_R(self):
        res = 0
        for item in self.r_list:
            res += item[1]
        return res / len(self.r_list)

    def s_a_S(self):
        res = 0
        for item in self.s_list:
            res += item[1]
        return res / len(self.s_list)

    def s_a_T(self):
        res = 0
        for item in self.t_list:
            res += item[1]
        return res / len(self.t_list)

    def set_y_x(self):
        a = read_crv_file(self.fileName)
        self.disc = a[0]
        self.y_list = {1: [], 2: [], 3: []}
        self.x_list.clear()
        for item in a[1]:
            self.y_list[1].append(a[0] * item[0])
            self.y_list[2].append(a[0] * item[1])
            self.y_list[3].append(a[0] * item[2])
        self.x_list = [x for x in range(len(self.y_list[1]))]

    def show_ekg(self):
        self.plot.clear()
        self.points.clear()
        self.p_markers.clear()
        self.t_markers.clear()
        self.qrs_markers.clear()
        self.r_list.clear()
        self.p_list.clear()
        self.s_list.clear()
        self.t_list.clear()
        self.RR_period_list.clear()
        self.PP_period_list.clear()
        self.figure.clear()
        self.plot = self.figure.add_subplot(111)
        self.plot.grid()
        self.current_graph = self.plot.plot(self.x_list, self.y_list[self.current_side], color='black')
        self.plot.set_xlim([0, 4000])
        self.plot.set_xlabel("мс")
        self.plot.set_ylabel("мВ")
        self.find_R_maximums()
        self.find_S_maximums()
        self.find_T_maximums()
        self.find_P_maximums()
        if self.var_points.get():
            self.draw_points(self.r_list)
            self.draw_points(self.s_list)
            self.draw_points(self.p_list)
            self.draw_points(self.t_list)
        self.P_markers()
        self.T_markers()
        self.QRS_markers()
        self.write_params()
        self.toolbar.update()
        self.draw_RR_periods()
        self.draw_PP_periods()
        self.add_RR_periods()
        self.add_PP_periods()
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.canvas.draw()

    def save_RR_PP(self):
        self.add_PP_periods()
        self.add_RR_periods()
        s = 'R координаты, R периоды\n'
        sred_R = 0
        sred_P = 0
        for item in self.RR_period_list:
            s += str(item[0]) + ', ' + str(item[1]) + '\n'
            sred_R += item[1]
        s += '\n\nP координаты, P периоды\n'
        for item in self.PP_period_list:
            s += str(item[0]) + ', ' + str(item[1]) + '\n'
            sred_P += item[1]
        s += 'RR среднее = ' + str(sred_R / len(self.RR_period_list)) + '\nPP среднее = ' + str(
            sred_P / len(self.PP_period_list))
        filename = fd.asksaveasfilename(title="Выбрать файл", initialdir="D:\\",
                                        filetypes=(('TXT File', '*.txt'), ("All Files", "*")))
        if filename != '':
            f = open(filename, 'w')
            f.write(s)
            f.close()

    def draw_points(self, points):
        for item in points:
            self.points.append(
                self.plot.scatter(item[0], item[1],
                                  color='orange', s=15))

    def draw_RR_periods(self):
        for item in self.RR_period_list:
            item[2] = self.draw_vertical_line(item[0], 'red')

    def draw_PP_periods(self):
        for item in self.PP_period_list:
            item[2] = self.draw_vertical_line(item[0], 'green')

    def draw_vertical_line(self, x, colour):
        return self.plot.plot([x, x], [-0.5, 1.5], color=colour, picker=True)

    def on_pick(self, event):
        self.is_moving = not self.is_moving
        self.current_line = event.artist

    def on_move(self, event):
        if self.is_moving:
            self.current_line.set_xdata([event.xdata, event.xdata])
            self.current_line.set_ydata([-0.5, 1.5])
            self.canvas.draw()

    def add_RR_periods(self):
        for item in self.RR_period_list:
            item[0] = round(item[2][0].get_data()[0][0])
        self.RR_period_list[0][1] = self.RR_period_list[0][0]
        for i in range(1, len(self.RR_period_list)):
            self.RR_period_list[i][1] = self.RR_period_list[i][0] - self.RR_period_list[i - 1][0]

    def add_PP_periods(self):
        for item in self.PP_period_list:
            item[0] = round(item[2][0].get_data()[0][0])
        self.PP_period_list[0][1] = self.PP_period_list[0][0]
        for i in range(1, len(self.PP_period_list)):
            self.PP_period_list[i][1] = self.PP_period_list[i][0] - self.PP_period_list[i - 1][0]

    def find_R_maximums(self):
        a = max(self.y_list[self.current_side][50:1000])
        self.r_list.append([self.y_list[self.current_side].index(a), a])
        self.RR_period_list.append([self.y_list[self.current_side].index(a), 0, 0])
        self.plot.annotate(xy=(self.y_list[self.current_side].index(a) + 12, a), text='R')
        i = 0
        while i <= len(self.x_list) - 1000:
            i = self.find_local_R(self.r_list[len(self.r_list) - 1][0])

    def find_local_R(self, i):
        ext = [0, 0]
        for k in range(800):
            if self.y_list[self.current_side][i + 200 + k] > ext[1]:
                ext[0] = k + i + 200
                ext[1] = self.y_list[self.current_side][ext[0]]
        self.r_list.append(ext)
        self.RR_period_list.append([ext[0], 0, 0])
        self.plot.annotate(xy=(ext[0] + 12, ext[1]), text='R')
        return ext[0]

    def find_S_maximums(self):
        for item in self.r_list:
            ext = [0, 0]
            ext[1] = min(self.y_list[self.current_side][item[0]:item[0] + 150])
            ext[0] = item[0] + self.y_list[self.current_side][item[0]:item[0] + 150].index(ext[1])
            self.s_list.append(ext)
            self.plot.annotate(xy=(ext[0] + 12, ext[1]), text='S')

    def find_T_maximums(self):
        for item in self.s_list:
            ext = [0, 0]
            ext[1] = max(self.y_list[self.current_side][item[0]:item[0] + 400])
            ext[0] = item[0] + self.y_list[self.current_side][item[0]:item[0] + 400].index(ext[1])
            self.t_list.append(ext)
            self.plot.annotate(xy=(ext[0] + 12, ext[1]), text='T')

    def find_P_maximums(self):
        for item in self.r_list:
            try:
                ext = [0, 0]
                ext[1] = max(self.y_list[self.current_side][item[0] - 300:item[0] - 50])
                ext[0] = item[0] - 300 + self.y_list[self.current_side][item[0] - 300:item[0] - 50].index(ext[1])
                self.p_list.append(ext)
                self.plot.annotate(xy=(ext[0] + 12, ext[1]), text='P')
            except Exception:
                continue

    def P_markers(self):
        for x in self.p_list:
            temp = self.get_left_P_marker(x[0])
            self.p_markers.append([temp, self.get_right_P_marker(x[0])])
            self.PP_period_list.append([temp, 0, 0])
            if self.var_lines.get():
                self.draw_marker(self.p_markers[len(self.p_markers) - 1][0], 'P')
                self.draw_marker(self.p_markers[len(self.p_markers) - 1][1], 'P')

    def get_left_P_marker(self, x):
        t = min(self.y_list[self.current_side][x - 75:x])
        coord = x - 75 + self.y_list[self.current_side][x - 75:x].index(t)
        return coord

    def get_right_P_marker(self, x):
        t = min(self.y_list[self.current_side][x:x + 55])
        coord = x + self.y_list[self.current_side][x:x + 55].index(t)
        return coord

    def T_markers(self):
        for x in self.t_list:
            self.t_markers.append([self.get_left_T_marker(x[0]), self.get_right_T_marker(x[0])])
            if self.var_lines.get():
                self.draw_marker(self.t_markers[len(self.t_markers) - 1][0], 'T')
                self.draw_marker(self.t_markers[len(self.t_markers) - 1][1], 'T')

    def get_left_T_marker(self, x):
        t = min(self.y_list[self.current_side][x - 100:x])
        coord = x - 100 + self.y_list[self.current_side][x - 100:x].index(t)
        return coord

    def get_right_T_marker(self, x):
        t = min(self.y_list[self.current_side][x:x + 100])
        coord = x + self.y_list[self.current_side][x:x + 100].index(t)
        return coord

    def QRS_markers(self):
        for x in range(len(self.r_list)):
            self.qrs_markers.append(
                [self.get_left_QRS_marker(self.r_list[x][0]), self.get_right_QRS_marker(self.s_list[x][0])])
            if self.var_lines.get():
                self.draw_marker(self.qrs_markers[len(self.qrs_markers) - 1][0], 'R')
                self.draw_marker(self.qrs_markers[len(self.qrs_markers) - 1][1], 'S')

    def get_left_QRS_marker(self, x):
        i = x - 1
        while self.y_list[self.current_side][i - 1] < self.y_list[self.current_side][i] and i - 1 > 0:
            i -= 1
        coord = i - random.randint(5, 15)
        return coord

    def get_right_QRS_marker(self, x):
        i = x + 1
        while self.y_list[self.current_side][i + 1] < 0 and i + 1 < len(self.x_list):
            i += 1
        coord = i + random.randint(7, 12)
        return coord

    def draw_marker(self, x_coord, string):
        self.plot.plot([x_coord for _ in range(4)],
                       [self.y_list[self.current_side][x_coord] + 0.01 * y for y in range(4)], color='red')
        self.plot.annotate(xy=(x_coord, self.y_list[self.current_side][x_coord] - 0.04), text=string)

    def middle_start_p(self) -> list:
        res = [0 for _ in range(160)]
        for i in range(64):
            for k in range(160):
                res[k] += self.y_list[self.current_side][self.p_list[i][0] - 159 + k]
        for x in range(160):
            res[x] /= 64
        return res

    def middle_end_t(self) -> list:
        res = [0 for _ in range(160)]
        for i in range(64):
            for k in range(160):
                res[k] += self.y_list[self.current_side][self.t_list[i][0] + k]
        for x in range(160):
            res[x] /= 64
        return res

    def middle_left_r(self) -> list:
        res = [0 for _ in range(55)]
        for i in range(64):
            for k in range(55):
                res[k] += self.y_list[self.current_side][self.r_list[i][0] - 55 + k]
        for x in range(55):
            res[x] /= 64
        return res

    def middle_right_r(self) -> list:
        res = [0 for _ in range(55)]
        for i in range(64):
            for k in range(55):
                res[k] += self.y_list[self.current_side][self.r_list[i][0] + k]
        for x in range(55):
            res[x] /= 64
        return res

    def middle_right_p(self) -> list:
        res = [0 for _ in range(90)]
        for i in range(64):
            for k in range(90):
                res[k] += self.y_list[self.current_side][self.p_list[i][0] + k]
        for x in range(90):
            res[x] /= 64
        return res

    def middle_left_t(self) -> list:
        res = [0 for _ in range(135)]
        for i in range(64):
            for k in range(135):
                res[k] += self.y_list[self.current_side][self.t_list[i][0] - 135 + k]
        for x in range(135):
            res[x] /= 64
        return res

    def coger_s_a_P(self):
        s_a = 0
        for item in self.p_list[:64]:
            s_a += item[1]
        return s_a / 64

    def d_i_P(self):
        s_a = self.coger_s_a_P()
        dispers = 0
        for item in self.p_list[:64]:
            dispers += (item[1] - s_a) ** 2
        dispers /= 64
        q = dispers ** 0.5
        return 0.25 * q

    def coger_s_a_R(self):
        s_a = 0
        for item in self.r_list[:64]:
            s_a += item[1]
        return s_a / 64

    def d_i_R(self):
        s_a = self.coger_s_a_R()
        dispers = 0
        for item in self.r_list[:64]:
            dispers += (item[1] - s_a) ** 2
        dispers /= 64
        q = dispers ** 0.5
        return 0.25 * q

    def coger_s_a_S(self):
        s_a = 0
        for item in self.s_list[:64]:
            s_a += item[1]
        return s_a / 64

    def d_i_S(self):
        s_a = self.coger_s_a_S()
        dispers = 0
        for item in self.s_list[:64]:
            dispers += (item[1] - s_a) ** 2
        dispers /= 64
        q = dispers ** 0.5
        return 0.25 * q

    def coger_s_a_T(self):
        s_a = 0
        for item in self.t_list[:64]:
            s_a += item[1]
        return s_a / 64

    def d_i_T(self):
        s_a = self.coger_s_a_T()
        dispers = 0
        for item in self.t_list[:64]:
            dispers += (item[1] - s_a) ** 2
        dispers /= 64
        q = dispers ** 0.5
        return 0.25 * q

    def write_D_I(self):
        string = 'Доверительные интервалы: \n P = ' + str(self.coger_s_a_P()) + '+-' + str(
            self.d_i_P()) + 'мв\n R = ' + str(self.coger_s_a_R()) + '+-' + str(
            self.d_i_R()) + 'мв\n T = ' + str(self.coger_s_a_T()) + '+-' + str(
            self.d_i_T()) + 'мв'
        self.text_field.config(state=NORMAL)
        self.text_field.delete(1.0, END)
        self.text_field.insert(END, string)
        self.text_field.config(state=DISABLED)

    def r_mid(self):
        l = [0 for _ in range(701)]
        for i in range(1, 64):
            k = 0
            for x in self.y_list[self.current_side][self.r_list[i][0] - 350:self.r_list[i][0] + 350]:
                l[k] += x
                k += 1
        for t in range(len(l)):
            l[t] /= 64
        return l

    def p_mid(self):
        l = [0 for _ in range(701)]
        for i in range(1, 64):
            k = 0
            for x in self.y_list[self.current_side][self.p_list[i][0] - 100:self.p_list[i][0] + 600]:
                l[k] += x
                k += 1
        for t in range(len(l)):
            l[t] /= 64
        return l

    def t_mid(self):
        l = [0 for _ in range(701)]
        for i in range(1, 64):
            k = 0
            for x in self.y_list[self.current_side][self.t_list[i][0] - 500:self.t_list[i][0] + 200]:
                l[k] += x
                k += 1
        for t in range(len(l)):
            l[t] /= 64
        return l

    def show_middle_complex(self):
        l_y = self.r_mid()
        d_i = self.d_i_R()
        l_r_y1 = [i + d_i for i in l_y]
        l_r_y2 = [i - d_i for i in l_y]
        self.plot.clear()
        self.points.clear()
        self.plot.grid()
        self.figure.clf()
        plot1 = self.figure.add_subplot(221)
        plot1.plot([x for x in range(len(l_y))], l_y, color='black', linewidth=1)
        plot1.plot([x for x in range(len(l_y))], l_r_y1, color='green', linewidth=1)
        plot1.plot([x for x in range(len(l_y))], l_r_y2, color='green', linewidth=1)
        plot1.set_xlabel("мс")
        plot1.set_ylabel("мВ")
        plot1.set_title('R')
        plot1.grid()

        l_y = self.p_mid()
        d_i = self.d_i_P()
        l_r_y1 = [i + d_i for i in l_y]
        l_r_y2 = [i - d_i for i in l_y]
        plot2 = self.figure.add_subplot(222)
        plot2.plot([x for x in range(len(l_y))], l_y, color='black', linewidth=1)
        plot2.plot([x for x in range(len(l_y))], l_r_y1, color='orange', linewidth=1)
        plot2.plot([x for x in range(len(l_y))], l_r_y2, color='orange', linewidth=1)
        plot2.set_xlabel("мс")
        plot2.set_ylabel("мВ")
        plot2.set_title('P')
        plot2.grid()

        l_y = self.t_mid()
        d_i = self.d_i_T()
        l_r_y1 = [i + d_i for i in l_y]
        l_r_y2 = [i - d_i for i in l_y]
        plot2 = self.figure.add_subplot(223)
        plot2.plot([x for x in range(len(l_y))], l_y, color='black', linewidth=1)
        plot2.plot([x for x in range(len(l_y))], l_r_y1, color='red', linewidth=1)
        plot2.plot([x for x in range(len(l_y))], l_r_y2, color='red', linewidth=1)
        plot2.set_xlabel("мс")
        plot2.set_ylabel("мВ")
        plot2.set_title('     T')
        plot2.grid()
        self.write_D_I()
        self.toolbar.update()
        self.canvas.draw()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
