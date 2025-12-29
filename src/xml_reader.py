import re
import sys

import pandas as pd
import xml.etree.ElementTree as ET

from tools.logger import log


class XmlReader:

    def __init__(self, f_name: str):
        self.f_name = f_name
        # Читаем xml из файла
        self.xml_txt = self._read_file()
        # Регистрируем пространства имен
        self.namespaces = self._get_namespace()
        # Парсим XML
        self.root = self._get_root()

    def _read_file(self) -> str:
        """Читает текстовый файл с автоматическим определенитем кодировки.
        Возвращает текст из файла."""

        log.info(f'Читаем xml-файл {self.f_name}')
        # # Определяем кодировку файла
        # with open(self.f_name, 'rb') as file:
        #     raw = file.read(32)
        #     encoding = chardet.detect(raw)['encoding']
        # log.info(f'Кодировка файла {encoding}')

        encoding = 'UTF-8-SIG'

        try:
            with open(self.f_name, "r", encoding=encoding) as file:
                content = file.read()
            log.info(f'Файл успешно прочитан')
        except FileNotFoundError:
            log.error(f"Файл {self.f_name} не найден")
            raise FileNotFoundError
        except Exception as e:
            log.error(f"Произошла ошибка: {e}")
            sys.exit(-1)

        return content

    def _get_namespace(self) -> dict[str: str]:
        """Возвращает список всех namespace из xml файла"""
        namespaces = {}

        # Шаблон для поиска xmlns:prefix="uri"
        pattern = r'xmlns:([^=]+)="([^"]+)"'

        # Находим все совпадения
        matches = re.findall(pattern, self.xml_txt)

        for prefix, uri in matches:
            namespaces[prefix] = uri

        # Также ищем default namespace (без префикса)
        default_pattern = r'xmlns="([^"]+)"'
        default_matches = re.findall(default_pattern, self.xml_txt)

        if default_matches:
            namespaces[''] = default_matches[0]  # Пустая строка для default

        return namespaces

    def _get_root(self) -> ET.Element:
        """Разбор XML"""
        log.info('Разбор xml')
        try:
            root = ET.fromstring(self.xml_txt)
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
        # equipments = self.root.findall(f'.//cim:{parent_tag}', self.namespaces)
        equipments = self.root.findall(f'{{*}}{parent_tag}')

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
                    in_use_dates = equipment.find(f'.//{{{self.namespaces.get("cim")}}}InUseDate.inUseDate')

                    if in_use_dates is not None:
                        text_value = in_use_dates.text

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
