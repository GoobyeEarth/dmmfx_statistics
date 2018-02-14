from django.core.management.base import BaseCommand
import pandas as pd



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

        result_list = {}


        for node in range(1, max_node + 1):
            df_node = df[(df['node'] == node)]
            row = {}
            row['mean'] = df_node['profit'].mean()
            row['mean_accumulative'] = df[(df['node'] <= node)]['profit'].mean()
            row['std'] = df_node['profit'].std()
            row['std_accumulative'] = df[(df['node'] <= node)]['profit'].std()
            row['count'] = df_node['profit'].count()
            row['count_accumulative'] = df[(df['node'] <= node)]['profit'].count()

            result_list[node] = row



        output_df = pd.DataFrame.from_dict(result_list)
        output_df.to_csv(output_file_path, encoding="Shift-Jis")




