import os
from time import strftime, localtime

from tkinter import *
import tkinter.ttk as ttk
from typing import Tuple, Any

from src.equipments import Breaker, PowerTransformer, CurrentTransformer
from src.xml_reader import XmlReader

status_dict = {
    0:  'Успешное завершение',
    -999: 'Неуспешное завершение',
    -1: 'Неверно задан путь до файла собственника',
    -2: 'Неверно задан путь до файла СО',
    -3: 'Неверно задан путь до файла словарей',
    -4: 'Неизвестное оборудование',
    -5: 'Ошибка разбора',
    -6: 'Заполните путь до файла собственника',
    -7: 'Заполните путь до файла СО',

}


class Color:
    red = '#f44336'
    green = '#32CD32'
    turquoise = '#80f2d2'


class Model:
    @staticmethod
    def file_processing(current_equipment: str, fname_owner: str, fname_so: str, fname_dict: str = None,
                        fpath_save: str = None) -> int | tuple[str, str]:

        # Читаем xml
        try:
            xml_owner = XmlReader(fname_owner)
        except Exception as e:
            print(e)
            return -1

        try:
            xml_so = XmlReader(fname_so)
        except Exception as e:
            print(e)
            return -2

        if fname_dict:
            try:
                xml_dict = XmlReader(fname_dict)
            except Exception as e:
                print(e)
                return -3

        # Определяем оборудование
        if current_equipment == 'Breaker':
            equipment_owner = Breaker(xml_owner)
            equipment_so = Breaker(xml_so)
        elif current_equipment == 'PowerTransformer':
            equipment_owner = PowerTransformer(xml_owner)
            equipment_so = PowerTransformer(xml_so)
        elif current_equipment == 'CurrentTransformer':
            equipment_owner = CurrentTransformer(xml_owner)
            equipment_so = CurrentTransformer(xml_so)
        # elif current_equipment == 'VoltageTransformer':
        #     pass
        else:
            return -4

        try:
            # Запуск разбора
            equipment_owner.run()
            equipment_so.run()

            # Сравниваем оборуование
            equipment_owner.compare(equipment_so)

            # Сохраняем приложения
            fname_long, fname_short = equipment_owner.save_table(fpath_save)
        except Exception as e:
            print(e)
            return -5
        else:
            return fname_long, fname_short


class View:
    def __init__(self, root):
        self.root = root
        self.root.resizable(True, True)
        self.root.title("xParser")

        self.Main = Frame(self.root)

        position = {'padx': 5, 'pady': 5, 'anchor': NW}

        # --- Section 1
        self.section1 = Frame(self.Main)

        self.label_fpath = Label(self.section1, text='Label_0')
        self.label_fpath.pack(padx=5, pady=5, side=LEFT)

        self.field_fpath = Label(self.section1, text=' ')
        self.field_fpath.pack(padx=5, pady=5, side=LEFT)

        self.section1.pack(padx=5, pady=5, expand=True, fill=X)
        # --- END Section 1

        # --- Section 2
        self.section2 = Frame(self.Main)

        # --- Section 2 sub-frame 1 - RadioButton с оборудованием
        self.section2_1 = Frame(self.section2)

        self.label_equipment = Label(self.section2_1, text='Оборудование')
        self.label_equipment.pack(**position)

        self.Rvar = StringVar(value='Breaker')

        equipment_list = ['Breaker', 'PowerTransformer', 'CurrentTransformer', 'VoltageTransformer', '']
        for eq in equipment_list:
            r = ttk.Radiobutton(self.section2_1, text=eq, variable=self.Rvar, value=eq)
            r.pack(**position)

        self.section2_1.pack(padx=5, pady=5, side=RIGHT)
        # --- END Section 2 sub-frame 1

        # --- Section 2 sub-frame 2  Поля для ввода имен файлов
        self.section2_2 = Frame(self.section2)
        self.section2_2.grid_rowconfigure(0, weight=1)
        self.section2_2.grid_columnconfigure(0, weight=1)

        self.label_1 = Label(self.section2_2, text='Файл собственника')
        self.label_1.pack(**position)

        self.entry_1 = Entry(self.section2_2, width=30)
        self.entry_1.pack(padx=5, pady=5, expand=True, fill=X)

        self.label_2 = Label(self.section2_2, text='Файл СО')
        self.label_2.pack(**position)

        self.entry_2 = Entry(self.section2_2, width=30)
        self.entry_2.pack(padx=5, pady=5, expand=True, fill=X)

        self.label_3 = Label(self.section2_2, text='Справочник')
        self.label_3.pack(**position)

        self.entry_3 = Entry(self.section2_2, width=30)
        self.entry_3.pack(padx=5, pady=5, expand=True, fill=X)

        self.label_4 = Label(self.section2_2, text='Куда сохранить')
        self.label_4.pack(**position)

        self.entry_4 = Entry(self.section2_2, width=30)
        self.entry_4.pack(padx=5, pady=5, expand=True, fill=X)

        self.section2_2.pack(padx=5, pady=5, expand=True, side=LEFT, fill=X)
        # --- END Section 2 sub-frame 2

        self.section2.pack(padx=5, pady=5, expand=True, fill=X)
        # --- END Section 2

        # --- Section 3 Поле для логирования
        self.section3 = Frame(self.Main)

        self.label_log = Label(self.section3, text='Log')
        self.label_log.pack(**position)

        self.field_log = Text(self.section3, height=5, width=30)
        self.field_log.pack(padx=5, pady=5, expand=True, fill=X)
        # Для выделения строк цветом необходимо создать tag
        self.field_log.tag_config('red', background=Color.red)
        self.field_log.tag_config('green', background=Color.green)

        self.section3.pack(padx=5, pady=5, expand=True, fill=X)
        # --- END Section 3

        # --- Section 4 Кнопки
        self.btn_proc = Button(self.Main, text='Обработать', height=2, width=10, bg=Color.green)
        self.btn_proc.pack(padx=5, pady=5, side=LEFT)

        self.btn_open = Button(self.Main, text='Открыть', height=2, width=10)
        self.btn_open.pack(padx=5, pady=5, side=LEFT)

        self.btn_exit = Button(self.Main, text='Выход', height=2, width=10)
        self.btn_exit.pack(padx=5, pady=5, side=RIGHT)

        # --- END Section 4

        self.Main.pack(padx=5, pady=5, expand=True, fill=X)


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.btn_proc.config(command=self.btn_proc_func)
        self.view.btn_open.config(command=self.btn_open_func)
        self.view.btn_exit.config(command=self.btn_exit_func)

        self.fname_long = ''
        self.fname_short = ''

    def btn_proc_func(self) -> int:

        # Устанавливаем текст в самом верхнем поле
        self.view.field_fpath.config(text='Привет')

        # Получаем пути до файлов
        fname_owner = self.view.entry_1.get()
        fname_so = self.view.entry_2.get()
        fname_dict = self.view.entry_3.get()
        fpath_save = self.view.entry_4.get()

        # Проверка путей
        if fname_owner == '':
            self.append_log(status_dict.get(-6), 'red')
            return -6
        if fname_so == '':
            self.append_log(status_dict.get(-7), 'red')
            return -7

        # Получаем состояние переключателя RadioButton
        current_equipment = str(self.view.Rvar.get())

        self.append_log(f'Запущена обработка файла {fname_owner}')
        self.append_log(f'Выбрано оборудование {current_equipment}')

        # Запуск обработки
        status = self.model.file_processing(current_equipment, fname_owner, fname_so, fname_dict, fpath_save)

        if isinstance(status, tuple):
            self.append_log(f'{status_dict.get(0)} обработки файла {fname_owner}', 'green')
            self.fname_long = status[0]
            self.fname_short = status[1]
            self.append_log(f'Сохранен файл {self.fname_long}')
            self.append_log(f'Сохранен файл {self.fname_short}')
            return 0
        elif isinstance(status, int):
            self.append_log(status_dict.get(status), 'red')
            return status

    def btn_open_func(self):
        """Открывает файоы сравнения"""
        self.append_log(f'Открываем полный файл {self.fname_long}')
        os.startfile(self.fname_long)

        self.append_log(f'Открываем сокращенный файл {self.fname_short}')
        os.startfile(self.fname_short)

    def btn_exit_func(self):
        self.view.root.quit()

    def append_log(self, txt: str, tag: str = None) -> None:
        current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())
        if tag is None:
            self.view.field_log.insert(END, f'{current_time} - {txt}\n')
        else:
            self.view.field_log.insert(END, f'{current_time} - {txt}\n', tag)

        self.view.field_log.see('end')


if __name__ == '__main__':
    root = Tk()

    model = Model()
    view = View(root)
    controller = Controller(model, view)

    root.mainloop()
