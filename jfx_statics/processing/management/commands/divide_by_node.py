from django.core.management.base import BaseCommand
import pandas as pd
import copy

from datetime import datetime


class Args(object):
    INPUT_FILE = 'input_file'
    A_INPUT_FILE = '-' + INPUT_FILE

    OUTPUT_FILE = 'output_file'
    A_OUTPUT_FILE = '-' + OUTPUT_FILE

    NODE = 'node'
    A_NODE = '-' + NODE

    @staticmethod
    def get_input_file(options):
        return options[Args.INPUT_FILE][0]

    @staticmethod
    def get_output_file(options):
        return options[Args.OUTPUT_FILE][0]

    @staticmethod
    def get_node(options):
        return options[Args.NODE][0]


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument(Args.A_INPUT_FILE, nargs=1, type=str)
        parser.add_argument(Args.A_OUTPUT_FILE, nargs=1, type=str)
        parser.add_argument(Args.A_NODE, nargs=1, type=int)

    def handle(self, *args, **options):
        input_file_path = Args.get_input_file(options)
        output_file_path = Args.get_output_file(options)
        max_node = Args.get_node(options)

        df = pd.read_csv(input_file_path, encoding="Shift-Jis")

        result_list = []
        for node in range(1, max_node + 1):
            print(node)
            result_list.extend(self.cut_by_node(node, df))

        output_df = pd.DataFrame.from_dict(result_list)
        output_df.to_csv(output_file_path, encoding="Shift-Jis")

    def cut_by_node(self, node, df: pd.DataFrame):
        result_list = []
        for i, v in df.iterrows():
            row = {}
            result_key_a = 'a_'
            result_key_b = 'b_'

            ref_key = Label().set_node(node).set_times(1)
            next_ref_key = Label().set_node(node + 1).set_times(1)

            if ref_key.a().price() in v and v.isnull()[ref_key.a().price()]:
                continue

            row['node'] = node

            row[result_key_a + 'datetime'] = v[ref_key.a().datetime()]
            row[result_key_a + 'price'] = v[ref_key.a().price()]
            row[result_key_a + 'direction'] = v[ref_key.a().direction()]
            row[result_key_a + 'lot'] = v[ref_key.a().lot()]

            next_prefix_a = str(node + 1) + '_1_a_'
            if next_prefix_a + 'price' not in v:
                row[result_key_b + 'datetime'] = v[ref_key.b().datetime()]
                row[result_key_b + 'price'] = v[ref_key.b().price()]
                row[result_key_b + 'direction'] = v[ref_key.b().direction()]
                row[result_key_b + 'lot'] = v[ref_key.b().lot()]

            elif v.isnull()[next_prefix_a + 'price']:
                row[result_key_b + 'datetime'] = v[ref_key.b().datetime()]
                row[result_key_b + 'price'] = v[ref_key.b().price()]
                row[result_key_b + 'direction'] = v[ref_key.b().direction()]
                row[result_key_b + 'lot'] = v[ref_key.b().lot()]

            else:
                row[result_key_b + 'datetime'] = v[next_ref_key.a().datetime()]
                row[result_key_b + 'price'] = v[next_ref_key.a().price()]
                row[result_key_b + 'direction'] = v[next_ref_key.a().direction()]
                row[result_key_b + 'lot'] = v[next_ref_key.a().lot()]

            row['profit'] = self.calc_profit(
                row[result_key_b + 'price'],
                row[result_key_a + 'price'],
                row[result_key_a + 'direction'],
                row[result_key_a + 'lot']
            )

            result_list.append(row)
        return result_list

    @staticmethod
    def calc_profit(close_price, open_price, direction, lot):
        return (close_price - open_price) * direction * lot


class Label(object):
    DATETIME = 'datetime'
    PRICE = 'price'
    DIRECTION = 'direction'
    LOT = 'lot'

    def __init__(self):
        self.node: int = 0
        self.times: int = 0
        self.a_or_b: str = ''
        self.suffix: str = ''

    def set_node(self, node):
        self.node = node
        return copy.deepcopy(self)

    def set_times(self, times):
        self.times = times
        return copy.deepcopy(self)

    def a(self):
        self._set_a_or_b('a')
        return copy.deepcopy(self)

    def b(self):
        self._set_a_or_b('b')
        return copy.deepcopy(self)

    def datetime(self):
        return self.set_suffix(Label.DATETIME)._to_string()

    def price(self):
        return self.set_suffix(Label.PRICE)._to_string()

    def direction(self):
        return self.set_suffix(Label.DIRECTION)._to_string()

    def lot(self):
        return self.set_suffix(Label.LOT)._to_string()

    def set_suffix(self, suffix: str):
        self.suffix = suffix
        return copy.deepcopy(self)

    def _to_string(self):
        return str(self.node) + '_' + str(self.times) + '_' + self.a_or_b + '_' + self.suffix

    def _set_a_or_b(self, a_or_b: str):
        self.a_or_b = a_or_b
        return copy.deepcopy(self)
