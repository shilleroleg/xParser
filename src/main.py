import pandas as pd

from xml_reader import XmlReader
from equipments import Breaker


def main():
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.).xml'
    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\вв пс.xml'

    # f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\в_соглас.xml'
    f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ввпс _ГОСТ 1.xml'

    xml = XmlReader(f_name)

    breaker = Breaker(xml)
    breaker_df = breaker.run()
    breaker.save_table(f_name)

    print('УРА!')


if __name__ == '__main__':
    main()
