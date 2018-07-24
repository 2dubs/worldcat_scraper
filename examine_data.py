import csv
from langdetect import detect
import random
import retrieve_info as ri
import urllib


# TODO: methods for reading and writing files
def read_from_file(in_path, read_header=True):
    res = []
    with open(in_path, 'r') as csvfile:
        file_reader = csv.reader(csvfile)
        if read_header is False:
            next(file_reader, None)
        for row in file_reader:
            res.append(row)
    return res


# helper function to write to file
def write_to_file(out_path, data, print_lines=False):
    counter = 0
    with open(out_path, 'w') as csvfile:
        s_writer = csv.writer(csvfile)
        for row in data:
            counter += 1
            s_writer.writerow(row)
            if print_lines is True:
                print(row)
                print("------------")
    print(counter)


# TODO: helper function to make test csv file from search_found.csv
def create_test_csv():
    data = read_from_file('data/search_found.csv', read_header=False)
    res = []
    for each in data:
        rand_num = random.random()
        if rand_num <= 0.1:
            res.append(each)
    write_to_file('data/test.csv', res, print_lines=True)


# TODO: methods to check the language of a book
def check_language(text):
    lang = detect(text)
    return lang


def check_language_main():
    data = read_from_file('data/search_missing.csv', read_header=False)
    count_dict = {}
    name_language = []
    for each in data:
        first_tokens = each[1].split('[')
        book_name = first_tokens[0]
        language = check_language(book_name)
        # keep count in count_dict
        if language in count_dict:
            count_dict[language] += 1
        else:
            count_dict[language] = 1
        # add to result list
        row = [each[1], language]
        name_language.append(row)
    for key, value in reversed(sorted(count_dict.items(), key=lambda kv: kv[1])):
        print(key, value)
    write_to_file('data/missing_name_language.csv', name_language, print_lines=True)


# TODO: helper methods for examining whether World Cat contains results for a document

# helper function to determine if a result is found
# returns True if result is found
def search_result_found(url):
    soup = ri.get_soup(url)
    checker = soup.find('div', {'class': 'error-results'})
    # if we didn't find this checker, then a result is found
    if checker is None:
        return True
    else:
        return False


def do_search_with_less_constraints(specifiers):
    try:
        all_specifiers = ri.get_advanced_search_url(specifiers)

        if search_result_found(all_specifiers):
            print("[Found]")
            return specifiers, all_specifiers

        no_year = ri.get_advanced_search_url(specifiers, yr=False)

        if search_result_found(no_year):
            print("[Found (not specifying year)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(not specifying year)' + new_specifiers[1]
            return new_specifiers, no_year

        no_ln = ri.get_advanced_search_url(specifiers, ln=False)

        if search_result_found(no_ln):
            print("[Found (not language)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(not language)' + new_specifiers[1]
            return new_specifiers, no_ln

        no_author = ri.get_advanced_search_url(specifiers, au=False)

        if search_result_found(no_author):
            print("[Found (not specifying author)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(not specifying author)' + new_specifiers[1]
            return new_specifiers, no_author

        no_year_author = ri.get_advanced_search_url(specifiers, au=False, yr=False)

        if search_result_found(no_year_author):
            print("[Found (not specifying neither year nor author)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(not specifying neither year nor author)' + new_specifiers[1]
            return new_specifiers, no_year_author

        no_year_ln = ri.get_advanced_search_url(specifiers, yr=False, ln=False)

        if search_result_found(no_year_ln):
            print("[Found (not specifying neither year nor language)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(not specifying neither year nor language)' + new_specifiers[1]
            return new_specifiers, no_year_ln

        no_author_ln = ri.get_advanced_search_url(specifiers, au=False, ln=False)

        if search_result_found(no_author_ln):
            print("[Found (not specifying neither author nor language)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(not specifying neither author nor language)' + new_specifiers[1]
            return new_specifiers, no_author_ln

        none = ri.get_advanced_search_url(specifiers, au=False, yr=False, ln=False)

        if search_result_found(none):
            print("[Found (specifying only name)]")
            new_specifiers = specifiers
            new_specifiers[1] = '(specifying only name)' + new_specifiers[1]
            return new_specifiers, none

        print("[Missing]")
        return 'missing', None

    except (UnicodeEncodeError, urllib.error.URLError):
        print("[Error]")
        return 'error', None


# main function for separating files by whether results can be found
def separate_main(name):
    entries = read_from_file('data/errors/' + name + '.csv', read_header=False)
    # dictionary = separate_found_from_missing(entries)

    # write_to_file('data/less_constraints/' + name + '_less_constraints_found.csv', dictionary['found'])
    # write_to_file('data/less_constraints/' + name + '_less_constraints_error.csv', dictionary['error'])

    for each in entries:
        print(do_search_with_less_constraints(each))


if __name__ == "__main__":
    separate_main('b0_b1_error')