from django.core.management.base import BaseCommand
import pandas as pd

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
        node = Args.get_node(options)

        df = pd.read_csv(input_file_path, encoding="Shift-Jis")

        result_list = []
        for i, v in df.iterrows():
            row = {}
            prefix = str(node) + '_1_'
            prefix_a = prefix + 'a_'
            prefix_b = prefix + 'b_'

            if v.isnull()[prefix_a + 'price']:
                continue

            row[prefix_a + 'datetime'] = v[prefix_a + 'datetime']
            row[prefix_a + 'price'] = v[prefix_a + 'price']
            row[prefix_a + 'direction'] = v[prefix_a + 'direction']
            row[prefix_a + 'lot'] = v[prefix_a + 'lot']

            next_prefix_a = str(node + 1) + '_1_a_'
            if v.isnull()[next_prefix_a + 'price']:
                row[prefix_b + 'datetime'] = v[prefix_b + 'datetime']
                row[prefix_b + 'price'] = v[prefix_b + 'price']
                row[prefix_b + 'direction'] = v[prefix_b + 'direction']
                row[prefix_b + 'lot'] = v[prefix_b + 'lot']
            else:
                row[prefix_b + 'datetime'] = v[next_prefix_a + 'datetime']
                row[prefix_b + 'price'] = v[next_prefix_a + 'price']
                row[prefix_b + 'direction'] = v[next_prefix_a + 'direction']
                row[prefix_b + 'lot'] = v[next_prefix_a + 'lot']

            result_list.append(row)

        output_df = pd.DataFrame.from_dict(result_list)
        output_df.to_csv(output_file_path, encoding="Shift-Jis")
