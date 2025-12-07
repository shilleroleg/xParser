import pandas as pd

from src.comparer import Comparer
from xml_reader import XmlReader
from equipments import Breaker
from tools.logger import log


def main():
    log.info('Разбор оборудования')
    f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.).xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\вв пс.xml'

    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\в_соглас.xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ввпс _ГОСТ 1.xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.)_test.xml'

    xml = XmlReader(f_name)

    breaker = Breaker(xml)
    breaker.run()
    breaker.save_table(f_name)

    # Второй файл для сравнения
    f_name_test = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.)_test2.xml'

    xml_test = XmlReader(f_name_test)

    breaker_test = Breaker(xml_test)
    breaker_test.run()
    #
    # Сравниваем
    comparer = Comparer(breaker, breaker_test)
    comp_df = comparer.run()

    with pd.ExcelWriter('compare3.xlsx') as writer:
        comp_df.to_excel(writer, sheet_name='Лист1', index=False, )

    log.info('Разбор оборудования завершен')


if __name__ == '__main__':
    main()
