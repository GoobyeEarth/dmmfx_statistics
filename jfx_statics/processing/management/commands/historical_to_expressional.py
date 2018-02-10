from django.core.management.base import BaseCommand
import pandas as pd

from datetime import datetime


class Args(object):
    INPUT_FILE = 'input_file'
    A_INPUT_FILE = '-' + INPUT_FILE

    OUTPUT_FILE = 'output_file'
    A_OUTPUT_FILE = '-' + OUTPUT_FILE

    @staticmethod
    def get_input_file(options):
        return options[Args.INPUT_FILE][0]

    @staticmethod
    def get_output_file(options):
        return options[Args.OUTPUT_FILE][0]


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument(Args.A_INPUT_FILE, nargs=1, type=str)
        parser.add_argument(Args.A_OUTPUT_FILE, nargs=1, type=str)

    def handle(self, *args, **options):
        input_file_path = Args.get_input_file(options)
        output_file_path = Args.get_output_file(options)

        df = pd.read_csv(input_file_path, encoding="Shift-Jis")
        # print(df[df['約定区分'] == '決済約定'])

        position_count = 0
        trade_count = 0
        result_array = []
        position_existence = {}

        row_dict = {}

        for i, v in df[::-1].iterrows():
            if v['約定区分'] == '新規約定':
                position_count += 1
                trade_count += 1

                if position_count in position_existence.keys():
                    position_existence[position_count] += 1
                else:
                    position_existence[position_count] = 1

                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_a_price'] = v['新規約定値']
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_a_datetime'] = v['新規約定日時']
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_a_direction'] = 1 if v['売買'] == '買' else -1
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_a_lot'] = v['Lot数']

            else:
                trade_count += 1
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_b_price'] = v['決済約定値']
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_b_datetime'] = v['決済約定日時']
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_b_direction'] = 1 if v['売買'] == '買' else -1
                row_dict[str(position_count) + '_' + str(position_existence[position_count]) + '_b_lot'] = v['Lot数']

                position_count -= 1

            if position_count == 0:
                result_array.append(row_dict)
                position_existence = {}
                row_dict = {}
                trade_count = 0
        output_df = pd.DataFrame.from_dict(result_array)
        output_df.to_csv(output_file_path, encoding="Shift-Jis")
