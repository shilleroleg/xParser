import sys

import numpy as np
import pandas as pd

from src.equipments import BaseEquipment
from tools.logger import log


class Comparer:
    def __init__(self, first: BaseEquipment, second: BaseEquipment, compare_id: str = None):
        self.first = first.appendix_1
        self.second = second.appendix_1

        self.first_columns = self.first.columns
        self.second_columns = self.second.columns

        self.first_txt = first.xml.xml_txt
        self.second_txt = second.xml.xml_txt

        if compare_id is None or compare_id not in self.first_columns:
            self.compare_id = self.first_columns[0]
        else:
            self.compare_id = compare_id

    def run(self) -> pd.DataFrame:
        # Проверяем наличие ParentObject
        self._find_parent_object()

        # Проверяем, что список столбцов одинаковый
        self._compare_columns_list()

        # Запуск первой сравнялки: сравниваем две таблицы поэлементно
        check_1_df = self._compare_1()

        return check_1_df

    def _compare_1(self) -> pd.DataFrame:

        # По mRID находим, как изменился состав оборудования
        mRID_df = self._find_intersect_mRID()
        add_mRID = mRID_df.loc[mRID_df['compare_flg'] == 'Добавлено', self.compare_id].tolist()  # Только в первом файле
        chg_mRID = mRID_df.loc[
            mRID_df['compare_flg'] == 'Изменено', self.compare_id].tolist()  # Общие mRID для двух файлов
        del_mRID = mRID_df.loc[mRID_df['compare_flg'] == 'Удалено', self.compare_id].tolist()  # Только во втором файле

        # Сравниваем только общие mRID
        chg_df = self._compare_change(chg_mRID)

        # Собираем финальный датафрейм
        final_cng_df = (mRID_df
                        .merge(chg_df, on=self.compare_id, how='inner')
                        )

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
        set_first = set(self.first_columns)
        set_second = set(self.second_columns)

        uniq_firs = set_first.difference(set_second)
        uniq_second = set_second.difference(set_first)

        if len(uniq_firs) > 0:
            log.error(f'Правая таблица содержит уникальные колонки: {uniq_firs}')
        elif len(uniq_second) > 0:
            log.error(f'Левая таблица содержит уникальные колонки: {uniq_second}')
        else:
            log.info('Список колонок одинаков')

    def _find_intersect_mRID(self) -> pd.DataFrame:

        merged_df = pd.merge(self.first[[self.compare_id]], self.second[[self.compare_id]],
                             on=self.compare_id, how='outer', indicator=True)

        category_mapping = {'both': 'Изменено', 'left_only': 'Добавлено', 'right_only': 'Удалено'}
        merged_df['compare_flg'] = merged_df['_merge'].cat.rename_categories(category_mapping)

        merged_df.drop('_merge', axis=1, inplace=True)

        return merged_df

    def _compare_change(self, mrid_list: list[str]) -> pd.DataFrame:

        first = self.first[self.first[self.compare_id].isin(mrid_list)]
        second = self.second[self.second[self.compare_id].isin(mrid_list)]

        first = first.fillna('(EMPTY)')
        second = second.fillna('(EMPTY)')

        result_df = first[self.compare_id].to_frame()

        for column in self.first_columns:
            if column == self.compare_id:
                continue

            temp_df = first[[self.compare_id, column]].merge(second[[self.compare_id, column]],
                                                             on=self.compare_id, how='left',
                                                             suffixes=('_first', '_second')
                                                             )

            temp_df[f'{column}_compare'] = np.where(temp_df[f'{column}_first'] == temp_df[f'{column}_second'],
                                                    temp_df[f'{column}_first'],
                                                    temp_df[f'{column}_first'] + '&\n' + temp_df[f'{column}_second'])

            result_df = result_df.merge(temp_df[[self.compare_id, f'{column}_compare']],
                                        on=self.compare_id, how='left'
                                        )

        result_column = [col.replace('_compare', '') for col in result_df.columns]
        result_df.columns = result_column

        result_df = result_df.replace('(EMPTY)', np.nan)

        return result_df

    def _find_parent_object(self):
        """Если xml содержит ParentObject, то это ошибка"""

        check_substring = 'ParentObject'
        if check_substring in self.first_txt:
            log.error(f'Первый объект содержит {check_substring}')
            sys.exit(-1)
        elif check_substring in self.second_txt:
            log.error(f'Второй объект содержит {check_substring}')
            sys.exit(-1)
        else:
            log.info(f'Объекты не содержат {check_substring}')
