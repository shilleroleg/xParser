import pandas as pd

from xml_reader import XmlReader
from equipments import Breaker


def main():
    f_name = r'c:\Users\olega\PycharmProjects\xParser\src\xml\ПС 189 (2 этап рекон.).xml'

    xml = XmlReader(f_name)

    breaker = Breaker(xml)
    breaker_df = breaker.run()
    breaker.save_table(breaker_df, f_name)

    print('УРА!')


if __name__ == '__main__':
    main()
