import requests
from bs4 import BeautifulSoup
import csv

# TODO: some code from http://edmundmartin.com/scraping-google-with-python/, credit to Edmund Martin

tester = 'K tipologii nekotoryh yakutskih kosmonimov [To typology of some Yakut cosmonyms]'

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


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
    count = 0
    with open(out_path, 'w') as csvfile:
        s_writer = csv.writer(csvfile)
        for row in data:
            count += 1
            s_writer.writerow(row)
            if print_lines is True:
                print(row)
                print("------------")
    print(count)

# TODO: methods to handle creating google search link and obtaining fuzzy search result


def get_fuzzy_search(raw_book_name, number_results, language_code):
    name_tokens = raw_book_name.split('[')
    search_term = name_tokens[0]

    escaped_search_term = search_term.replace(' ', '+')

    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results,
                                                                          language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    checker = soup.find('a', {'class': 'spell'})
    if checker is None:
        return ''
    else:
        return checker.getText()


if __name__ == "__main__":
    name = 'b0'

    data = read_from_file('data/search_missing/' + name + '_search_missing.csv')
    data += read_from_file('data/errors/' + name + '_error.csv')
    found_list = []
    missing_list = []
    counter = 0
    hit_counter = 0
    for each in data:
        counter += 1
        print(counter)
        name = each[1]

        try:
            fuzzy_name = get_fuzzy_search(name, 1, 'en')
            print(fuzzy_name)

            if fuzzy_name is not '':
                print(name + ' --> ' + fuzzy_name)
                hit_counter += 1
                new_row = [name, fuzzy_name]
                found_list.append(new_row)
            else:
                print(name + ' not found')
                new_row = [name]
                missing_list.append(new_row)
            print("----------------")
        except AssertionError:
            print("Incorrect arguments parsed to function")
        except requests.HTTPError:
            print("You appear to have been blocked by Google")
            break
        except requests.RequestException:
            print("Appears to be an issue with your connection")
            break

    write_to_file('data/fuzzy_search/' + name + '_fuzzy_search_found.csv', found_list)
    write_to_file('data/fuzzy_search/' + name + '_fuzzy_search_missing.csv', missing_list)
    print(hit_counter)
