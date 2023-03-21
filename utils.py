import csv
import json
import os
import traceback

from main import get_preferred_engines, parse_csv


def convert_JSON_file_to_CSV(output_file_name='mt_parse', source_file_path='config_files/mt.json',
                             should_ignore_defaults=False):
    """
        It converts the JSON file to a CSV file. It uses the main.py functions to parse the JSON file and
        get the preferred engines.

        :param should_ignore_defaults:
        :param output_file_name: the name of the output file
        :param source_file_path: the path of the source file
        :return: a string with the result of the operation
    """
    try:
        # get preferred engines
        preferred_engines = get_preferred_engines()
        should_ignore_defaults_str = "_without_defaults" if should_ignore_defaults else ""

        # prepare the CSV file to write
        with open(f'{output_file_name}{should_ignore_defaults_str}.csv', 'w') as file_output:
            writer = csv.writer(file_output)
            writer.writerow(
                ["source language", "target language", "translation engine", "is preferred engine?"])

            # iterate over each file in the directory
            with open(f'{source_file_path}') as file:
                engine_lines = json.load(file)

                for engine in engine_lines:

                    if should_ignore_defaults and engine == 'defaults':
                        continue

                    # get the translation engine used
                    standard = True
                    lines = engine_lines[engine]

                    # parse the CSV file
                    cvs_pairs_dict = parse_csv(engine, standard, lines)

                    for key, value in cvs_pairs_dict.items():
                        # get source and target languages, check if the value or engine is the preferred to
                        # construct
                        source, target = key.split(':', 2)
                        engine = value
                        # we will mark as true if the engine is the preferred one in the preferred_engines
                        # dictionary
                        is_preferred = 'true' if preferred_engines.get(f'{source}-{target}') == engine else 'false'
                        # add the line to the CSV file
                        writer.writerow([source, target, engine, is_preferred])

        return "We have parsed the documents and generated the CSV file!"

    except Exception as e:
        # print error trace
        print(traceback.format_exc())
        print(e)

        return "Something went wrong. Please check the logs."


def compare_differences_between_files(first_file='mt_parse_without_defaults.csv',
                                      second_file='compare_files/cx_server_parsed.csv'):
    """
        This function compares the differences between the files mt_parse_without_defaults.csv and cx_server_parsed.csv
        and prints the differences in the update.csv file.

        :return: void
        :reference: https://stackoverflow.com/questions/38996033/python-compare-two-csv-files-and-print-out-differences
        :notes:
        - part of the extract is referenced from the above link
        - the csv-diff command is used to compare the files in the terminal
            Example: csv-diff mt_parse_without_defaults.csv output_files/cx_server_parsed.csv
        - alternatively, one may use pandas to compare the files with the merge function
    """
    # read the files
    with open(first_file, 'r') as t1, open(second_file, 'r') as t2:
        file1 = t1.readlines()
        file2 = t2.readlines()

    # compare the files and write the differences in the update.csv file
    print(f'Comparing the number of differences between {first_file} and {second_file} ...')
    # count the number of differences
    count = 0
    with open('update.csv', 'w') as outFile:
        for line in file1:
            if line not in file2:
                count += 1
                outFile.write(line)

    # read generated file and print it
    with open('update.csv', 'r') as file:
        resulting_different_lines = file.read()
        print(f' The total number of differences between {first_file} and {second_file} was: {count}')
        print(resulting_different_lines)

    return count, resulting_different_lines


def compare_difference_between_all_files(target_file='mt_parse_without_defaults.csv'):
    """
        This function compares the differences between all the files in the compare_files directory and
        the mt_parse_without_defaults.csv file.

        :return: void
    """
    # get the total number of lines in the target file
    total_count_target_file = len(open(target_file).readlines())

    # prepare the CSV file to write
    with open('output_results.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(["target file", "second file", "number of differences", "percentage of closeness"])

        # iterate over each file in the directory
        for file_name in os.listdir('compare_files'):
            # skip the output file
            if file_name == 'output_results.csv':
                continue

            # compare the differences between the files
            count, resulting_different_lines = compare_differences_between_files(first_file=target_file,
                                                                                 second_file=f'compare_files/{file_name}')

            # show the percentage of closeness between the files
            percentage = (total_count_target_file - count) / total_count_target_file * 100
            print(f'The percentage of closeness between {target_file} and {file_name} is: {percentage}%')

            # write the results in the output file with csv writer
            writer.writerow([target_file, file_name, count, percentage]) # , resulting_different_lines])



if __name__ == '__main__':
    # convert the JSON file to CSV. Disable if necessary
    need_to_transform_json_to_csv = False
    if need_to_transform_json_to_csv:
        # should not ignore defaults
        convert_JSON_file_to_CSV()
        # should ignore defaults
        convert_JSON_file_to_CSV(should_ignore_defaults=True)
    '''
    # compare the differences between the files
    compare_differences_between_files()
    compare_differences_between_files(first_file='mt_parse.csv', second_file='compare_files/cx_server_parsed.csv')
    '''

    # compare the differences between all the files in the compare_files directory and the target file
    compare_difference_between_all_files(target_file='mt_parse_without_defaults.csv')