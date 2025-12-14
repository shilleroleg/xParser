import pandas as pd

from src.comparer import Comparer
from xml_reader import XmlReader
from equipments import Breaker
from tools.logger import log


def main():
    log.info('Разбор оборудования')
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.).xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\вв пс.xml'

    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\в_соглас.xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ввпс _ГОСТ 1.xml'
    f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.)_test.xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.)_test3.xml'

    xml = XmlReader(f_name)

    breaker = Breaker(xml)
    breaker.run()

    # Второй файл для сравнения
    f_name_test = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.)_test2.xml'

    xml_test = XmlReader(f_name_test)

    breaker_test = Breaker(xml_test)
    breaker_test.run()
    #
    # Сравниваем оборуование
    breaker.compare(breaker_test)

    # Сохраняем приложения
    breaker.save_table()

    log.info('Разбор оборудования завершен')


if __name__ == '__main__':
    main()
