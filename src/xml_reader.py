import sys

import pandas as pd
import chardet
import xml.etree.ElementTree as ET

from tools.logger import log


class XmlReader:

    def __init__(self, f_name: str):
        self.f_name = f_name
        # Регистрируем пространства имен
        self.namespaces = {
            'cim': 'http://iec.ch/TC57/2014/CIM-schema-cim16#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        }
        # Парсим XML
        self.root = self.get_root()

    def read_file(self) -> str:
        """Читает текстовый файл с автоматическим определенитем кодировки.
        Возвращает текст из файла."""

        log.info(f'Читаем xml-файл {self.f_name}')
        # Определяем кодировку файла
        with open(self.f_name, 'rb') as file:
            raw = file.read(32)
            encoding = chardet.detect(raw)['encoding']
        log.info(f'Кодировка файла {encoding}')

        try:
            with open(self.f_name, "r", encoding=encoding) as file:
                content = file.read()
            log.info(f'Файл успешно прочитан')
        except FileNotFoundError:
            log.error(f"Файл {self.f_name} не найден")
            sys.exit(-1)
        except Exception as e:
            log.error(f"Произошла ошибка: {e}")
            sys.exit(-1)

        return content

    def get_root(self) -> ET.Element:
        """Разбор XML"""
        xml_txt = self.read_file()
        try:
            log.info('Разбор xml')
            root = ET.fromstring(xml_txt)
            log.info('Разбор xml успешно завершен')
        except Exception as e:
            log.error(f"Разбор xml завершился с ошибкой: {e}")
            sys.exit(-1)

        return root

    def get_data_by_list(self, tag_list: list[str]) -> dict[str: pd.DataFrame]:
        """На вход получает список tag.
        Возвращает словарь со структурой tag: pd.DataFrame"""

        out_dict = {}
        for tag in tag_list:
            data = self.get_data_by_tag(tag)
            out_dict[tag] = data

        return out_dict

    def get_data_by_tag(self, parent_tag: str) -> pd.DataFrame:
        """Возвращает dataframe с данными по одному tag"""

        # Список для хранения данных
        data = []

        # Находим все элементы тэга
        equipments = self.root.findall(f'.//cim:{parent_tag}', self.namespaces)

        for equipment in equipments:
            equipment_data = {}

            # Получаем id родильского элемента
            equipment_attrs = equipment.attrib
            if equipment_attrs:
                for _, value in equipment_attrs.items():
                    equipment_data[f"{parent_tag.lower()}_mRID"] = value.replace('#_', '')

            # Обрабатываем все дочерние элементы
            for child in equipment:
                # Получаем имя тега без namespace
                tag = child.tag
                if '}' in tag:
                    tag_name = tag.split('}', 1)[1]
                else:
                    tag_name = tag

                # Если такой тэг уже есть, то обрабатываем
                if tag_name in equipment_data.keys():
                    all_name = [key for key in equipment_data.keys() if key.startswith(tag_name)]
                    tag_name = f'{tag_name}_{len(all_name) + 1}'

                # Получаем текстовое значение
                text_value = child.text.strip() if child.text else None

                # Получаем атрибуты
                attrs = child.attrib
                attr_data = {}

                if attrs:
                    for attr, value in attrs.items():
                        if '}' in attr:
                            attr_name = attr.split('}', 1)[1]
                        else:
                            attr_name = attr
                        attr_data[attr_name] = value

                # Глубоко вложенный inUseDate ищем отдельно
                if tag_name == 'Asset.inUseDate':
                    in_use_dates = self.root.findall(f'.//{{{self.namespaces.get("cim")}}}InUseDate.inUseDate')

                    text_value = in_use_dates[0].text

                # Сохраняем значение
                if text_value:
                    equipment_data[tag_name] = text_value
                # Сохраняем атрибуты
                elif attr_data:
                    for attr_name, attr_value in attr_data.items():
                        equipment_data[tag_name] = attr_value.replace('#_', '')
                else:
                    equipment_data[tag_name] = ''

            data.append(equipment_data)

        # Создаем DataFrame
        df = pd.DataFrame(data)

        return df
