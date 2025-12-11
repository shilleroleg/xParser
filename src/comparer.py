import sys

import numpy as np
import pandas as pd

from tools.logger import log


class Comparer:
    def __init__(self, first: pd.DataFrame, second: pd.DataFrame, compare_id: str):
        self.first = first
        self.second = second
        self.compare_id = compare_id

    def run(self) -> pd.DataFrame:
        log.info('Сравнение запущено')

        # Проверяем, что список столбцов одинаковый
        self._compare_columns_list()

        # Запуск первой сравнялки: сравниваем две таблицы поэлементно
        compare_1_df = self._compare_1()

        log.info('Сравнение завершено')

        return compare_1_df

    def _compare_1(self) -> pd.DataFrame:
        """Первая сравнялка для вывода таблицы с изменившимися/не изменившимися значениями"""

        log.info('Сравнение таблиц поэлементно')

        # По mRID находим, как изменился состав оборудования
        mRID_df = self._find_intersect_mRID()
        # Только в первом файле
        add_mRID = mRID_df.loc[mRID_df['compare_flg'] == 'Добавлено', self.compare_id].tolist()
        # Общие mRID для двух файлов
        chg_mRID = mRID_df.loc[mRID_df['compare_flg'] == 'Изменено', self.compare_id].tolist()
        # Только во втором файле
        del_mRID = mRID_df.loc[mRID_df['compare_flg'] == 'Удалено', self.compare_id].tolist()

        # Сравниваем только общие mRID
        chg_df = self._compare_change(chg_mRID)

        # Собираем финальный датафрейм
        final_cng_df = mRID_df.merge(chg_df, on=self.compare_id, how='inner')

        final_add_df = (mRID_df
                        .merge(self.first[self.first[self.compare_id].isin(add_mRID)], on=self.compare_id, how='inner')
                        )

        final_del_df = (mRID_df
                        .merge(self.second[self.second[self.compare_id].isin(del_mRID)], on=self.compare_id,
                               how='inner')
                        )

        final_df = pd.concat([final_cng_df, final_add_df, final_del_df], axis=0, ignore_index=True)

        return final_df

    def _compare_columns_list(self) -> None:
        """Сравнивает список колонок двух таблиц"""
        set_first = set(self.first.columns)
        set_second = set(self.second.columns)

        uniq_firs = set_first.difference(set_second)
        uniq_second = set_second.difference(set_first)

        if len(uniq_firs) > 0:
            log.error(f'Правая таблица содержит уникальные колонки: {uniq_firs}')
        elif len(uniq_second) > 0:
            log.error(f'Левая таблица содержит уникальные колонки: {uniq_second}')
        else:
            log.info('Список колонок одинаков')

    def _find_intersect_mRID(self) -> pd.DataFrame:
        """Возвращает датафрейм, в котором помечено какие mRID общие для двух таблиц (Изменено),
        какие есть только в левой (Добавлено) и какие есть только в правой таблице (Удалено)"""

        merged_df = pd.merge(self.first[[self.compare_id]], self.second[[self.compare_id]],
                             on=self.compare_id, how='outer', indicator=True)

        category_mapping = {'both': 'Изменено', 'left_only': 'Добавлено', 'right_only': 'Удалено'}
        merged_df['compare_flg'] = merged_df['_merge'].cat.rename_categories(category_mapping)

        merged_df.drop('_merge', axis=1, inplace=True)

        return merged_df

    def _compare_change(self, mrid_list: list[str]) -> pd.DataFrame:
        """Сравнивает две таблицы на наличие изменений значений ячеек. Если значения одинаковые, то они выводятся.
         Если значения отличаются, то они выводятся через разделитель separator"""

        separator = '&'

        first_ = self.first[self.first[self.compare_id].isin(mrid_list)]
        second_ = self.second[self.second[self.compare_id].isin(mrid_list)]

        first_ = first_.fillna('(EMPTY)')
        second_ = second_.fillna('(EMPTY)')

        result_df = first_[self.compare_id].to_frame()

        for column in first_.columns:
            if column == self.compare_id:
                continue

            temp_df = first_[[self.compare_id, column]].merge(second_[[self.compare_id, column]],
                                                              on=self.compare_id, how='left',
                                                              suffixes=('_first', '_second')
                                                              )

            temp_df[f'{column}_compare'] = np.where(temp_df[f'{column}_first'] == temp_df[f'{column}_second'],
                                                    temp_df[f'{column}_first'],
                                                    (temp_df[f'{column}_first']
                                                     + f'{separator}\n'
                                                     + temp_df[f'{column}_second']))

            result_df = result_df.merge(temp_df[[self.compare_id, f'{column}_compare']],
                                        on=self.compare_id, how='left'
                                        )

        result_column = [col.replace('_compare', '') for col in result_df.columns]
        result_df.columns = result_column

        result_df = result_df.replace('(EMPTY)', '')

        return result_df

    @staticmethod
    def check_xml(xml_txt: str):
        """Если xml содержит ParentObject, то это ошибка"""

        check_substring = 'ParentObject'
        if check_substring in xml_txt:
            log.error(f'Объект содержит {check_substring}')
            # sys.exit(-1)
        else:
            log.info(f'Объект не содержит {check_substring}')