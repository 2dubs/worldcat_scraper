import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import csv

header = "https://www.worldcat.org/"

edition_tail = 'editions?sd=asc&start_edition=1&referer=di&se=yr&qt=sort_yr_asc&editionsView=true&fq='

og_header = ['id', 'Original Title', 'Original Author']

brief_header = ['Title', 'Author', 'Publisher', 'Series', 'Edition/Format', 'Rating', 'Publication',
                'Dissertation', 'Summary', 'Subjects', 'More like this', 'Other Databases']

detail_header = ['Document Type', 'All Authors / Contributors', 'OCLC Number', 'Responsibility', 'Genre/Form',
                 'ISBN', 'ISSN', 'BL Shelfmark', 'Accession No', 'Unique Identifier', 'In', 'Series Title', 'Other Titles',
                 'Description', 'Contents',  'Awards', 'Details', 'Material Type', 'Additional Physical Format',
                 'Notes', 'Language Note', 'Reproduction Notes', 'More information', 'Named Person', 'Performer(s)',
                 'Credits', 'Cartographic Mathematical Data', 'Target Audience', 'Event notes', 'Number of Edition']

label_index = {'Title': 0, 'Author': 1, 'Publisher': 2, 'Series': 3, 'Edition/Format': 4, 'Rating': 5, 'Publication': 6,
               'Dissertation': 7, 'Summary': 8, 'Subjects': 9, 'More like this': 10, 'Other Databases': 11,
               'Document Type': 12, 'All Authors / Contributors': 13, 'OCLC Number': 14, 'Responsibility': 15,
               'Genre/Form': 16, 'ISBN': 17, 'ISSN': 18, 'BL Shelfmark': 19, 'Accession No': 20, 'Unique Identifier': 21,
               'In': 22, 'Series Title': 23, 'Other Titles': 24, 'Description': 25, 'Contents': 26, 'Awards': 27,
               'Details': 28, 'Material Type': 29, 'Additional Physical Format': 30, 'Notes': 31, 'Language Note': 32,
               'Reproduction Notes': 33, 'More information': 34, 'Named Person': 35, 'Performer(s)': 36, 'Credits': 37,
               'Cartographic Mathematical Data': 38, 'Target Audience': 39, 'Event notes': 40, 'Number of Edition': 41}


TOTAL_NUM = 42


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

# TODO: methods for accessing WorldCat via url manipulation and making a beautiful soup


# get original url from given author, book name and year published
# au and yr are flags to indicate whether author name and year to be included in search
def get_advanced_search_url(specifiers, au=True, yr=True, ln=True):
    # 1. get author name, book name and year from specifiers
    author_name = specifiers[0]
    book_name = specifiers[1]
    year = specifiers[2]
    language = specifiers[3]

    # 2. clean and obtain author name for search
    #   NOTE: we only take one word from author's name. we leave searching to the website itself
    author_word = author_name.split(',')[0]
    encoded_author = urllib.parse.quote(author_word).replace(' ', '')

    # 3. clean and obtain book name for search
    # first tokenize by '[' and ']'
    first_tokens = book_name.split('[')
    tokens = first_tokens[0].split(' ')
    # encode everything in ascii for url use
    encoded_book_name = ''
    counter = 0
    for each in tokens:
        new_word = urllib.parse.quote(each)
        if counter == 0:
            encoded_book_name += new_word
        else:
            encoded_book_name += '+'
            encoded_book_name += new_word
        counter += 1

    # 4. make link and return link, depending on parameters
    link = header + 'search?q=ti%3A' + encoded_book_name
    if au is True:
        link += '+au%3A' + encoded_author
    if ln is True:
        link += '+ln%3A' + language
    if yr is True:
        link += '&fq=yr%3A' + year


    link += '+%3E' + "&qt=advanced&dblist=638"
    return link


# TODO: need error checking for all soup getting and html finding

# get html of the folklore we want and turn into soup
def get_soup(raw_link):
    page = urllib.request.urlopen(raw_link)
    raw_soup = BeautifulSoup(page, 'html.parser')
    return raw_soup


# get the link to the document that we want
def get_result_link(raw_soup):

    material = raw_soup.find('tr', {'class': 'menuElem'})
    # print(material)
    detail = material.find('td', {'class': 'result details'})
    # print(detail)
    link_prev = detail.find('div',{'class': 'name'})
    real_link = link_prev.find('a', {'id': 'result-1'}, href=True, text=True)
    link_str = real_link['href']
    real_link = header + link_str

    return real_link


# TODO: scraping methods for the RESULTS section
# method to scrape "Result" section on the result page
# input:  soup from [author, book name, year published]
# output: List of tuples containing result key to result value
def scrape_results_section(soup):
    to_return = []
    raw_material = soup.find('div', {'id': 'bibdata'})

    title = raw_material.find('h1', {'class': 'title'}).getText()

    title_tuple = tuple(['Title', title])
    to_return.append(title_tuple)

    res_list = raw_material.find_all({'tr'})

    for res in res_list:
        text = res.getText()
        res_tuple = clean_result(text)
        if res_tuple is not None:
            to_return.append(res_tuple)
    return to_return


def clean_result(text):
    tokens = [x for x in text.split('\n') if x is not '' and x is not '\r']
    key = tokens[0]
    value = ''.join(tokens[1:]).replace('\xa0', '')
    if 'Publication:' in key:
        key_token = key.split(':')
        key = key_token[0]
        value = key_token[1]
    if key == 'Rating:':
        value = 'not yet rated'
    if key == 'Edition/Format:':
        value = value.split('View all editions and formats')[0]

    to_return = None
    if key != 'Search this publication for other articles with the following words:':
        to_return = tuple([key.replace(':', ''), value])

    return to_return


# TODO: scraping methods for the DETAILS section

# method to scrape "Details" section on the result page
def scrape_detail_section(soup):
    to_return = []
    raw_material = soup.find('div', {'id': 'details'})
    details_list = raw_material.find_all('tr')

    for detail in details_list:
        text = detail.getText()
        res_tuple = clean_detail(text)
        to_return.append(res_tuple)
    return to_return


# method to tokenize and clean details into a key value pair
def clean_detail(text):
    tokens = text.split(':')
    key = tokens[0].replace('\n', '')
    value = ''.join(tokens[1:]).replace('\n', '')
    value = value.replace('\xa0', '')
    to_return = [key, value]
    return tuple(to_return)


# TODO: scraping methods for the EDITION section (also getting oldest link)

def scrape_edition_section(soup, get_oldest=True):
    edition_count = '-1'
    oldest_edition_url = ''
    try:
        raw_material = soup.find('span', {'id': 'editionFormatType'})
        raw_url = raw_material.find('a')['href']

        url_token = raw_url.split('editions?')
        edition_url = header + url_token[0] + edition_tail

        edition_soup = get_soup(edition_url)

        edition_count = get_edition_count(edition_soup)

        if get_oldest is True:
            oldest_edition_url = get_oldest_url(edition_soup)

    except (TypeError, AttributeError):
        pass

    return edition_count, oldest_edition_url


def get_oldest_url(edition_soup):
    raw_material = edition_soup.find('table', {'class': 'table-results'})
    raw_string = raw_material.find('div', {'class': 'name'})
    url = header + raw_string.find('a')['href']
    return url


def get_edition_count(edition_soup):
    raw_material = edition_soup.find('div', {'id': 'fial-numresults'})
    raw_string = raw_material.find('td')
    raw_text = raw_string.getText()
    text = raw_text.split('out of ')
    return text[1]


# TODO: scraping methods for the SIMILAR ITEMS section in place of 'MORE LIKE THIS'
def scrape_similar_items(soup):
    to_return = ''
    try:
        raw_material = soup.find('ul', {'id': 'subject-terms-detailed'})
        raw_row = raw_material.getText()
        to_return = clean_similar_items(raw_row)
    except (TypeError, AttributeError):
        pass
    return to_return


def clean_similar_items(text):
    to_return = []
    tokens = text.split('\n')
    for token in tokens:
        if token != '':
            to_return.append(token)

    to_return = '; '.join(to_return)
    return to_return


# TODO: scraping methods for the LIBRARY section [Require a different set of packages]


# TODO: wrapper method for getting information from a folklore
# input:  the result link generated from advance search generated from [author, book name, year published]
# output: 1. a List composed of values fitting to the formal
#         2. (optional) when get_oldest=True, a string for the url of oldest edition
def get_info(result_link, get_oldest=True):
    # build row as default
    row = ['No info' for i in range(TOTAL_NUM)]
    # get result of advance research for folklore in html format
    result_soup = get_soup(result_link)

    # get brief result and detail for this folklore
    result = scrape_results_section(result_soup)
    detail = scrape_detail_section(result_soup)

    # get information from the similar items section
    similar_items = scrape_similar_items(result_soup)

    # create a holder for oldest link and edition info
    if get_oldest is True:
        edition_count, oldest_link = scrape_edition_section(result_soup, get_oldest=True)
    else:
        edition_count, oldest_link = scrape_edition_section(result_soup, get_oldest=True)

    # modify row
    raw_row = result + detail
    for each in raw_row:
        key = each[0]
        value = each[1]
        index = label_index[key]
        row[index] = value

    if similar_items != '':
        row[label_index['More like this']] = similar_items
    else:
        row[label_index['More like this']] = 'No Info'

    if edition_count != '-1':
        row[label_index['Number of Edition']] = edition_count
    else:
        row[label_index['Number of Edition']] = 'No Info'
    return row, oldest_link


# TODO: helper method to make a dictionary out of brief_result header and details header
# TODO: Uncomment only when need to change header. Used to generate {label:index}
def generate_label_index():
    total_header = brief_header + detail_header
    label_index = {}
    for i, value in enumerate(total_header):
        print(i)
        label_index[value] = i
    print(label_index)
    return label_index


if __name__ == "__main__":
    # generate_label_index()
    name = 'b0_b1_1'

    data = read_from_file('data/real_' + name + '.csv')

    result_file = []
    error_file = []
    real_header = og_header + list(label_index.keys())
    result_file.append(real_header)
    # generate id_counter
    id_counter = 3336
    print(real_header)
    for folklore in data:
        id_counter += 1
        basic_info = [str(id_counter), folklore[1], folklore[0]]
        try:
            # get info for current version info
            search_link = get_advanced_search_url(folklore)
            soup = get_soup(search_link)
            result_link = get_result_link(soup)
            temp_row, old_link = get_info(result_link, get_oldest=True)
            row = basic_info + temp_row
            print(row)
            # print(id_counter)
            result_file.append(row)
        except (TypeError, AttributeError, UnicodeEncodeError):
            print('*** UNFOUND ***')
            id_counter -= 1
            print(basic_info[2] + '; ' + basic_info[1])
            error_file.append(folklore)
            print("------------------------------------------")
            continue
        except urllib.error.HTTPError as err:
            if str(err).split(':')[0] == 'HTTP Error 403':
                error_file.append(folklore)
                print('quota exceeded at ')
                print('         ' + str(folklore))
                break
            else:
                print('*** ERROR ***')
                id_counter -= 1
                print(basic_info[2] + '; ' + basic_info[1])
                error_file.append(folklore)
                print("------------------------------------------")
                continue

        try:
            # get info for oldest version info
            if old_link != '':
                basic_info = [str(id_counter) + '_F', folklore[1] + ' (oldest version)', folklore[0]]
                # print(old_link)
                temp_row, _ = get_info(old_link, get_oldest=False)
                row = basic_info + temp_row
                print(row)
                # print(id_counter)
                result_file.append(row)
        except urllib.error.HTTPError as err:
            if str(err).split(':')[0] == 'HTTP Error 403':
                error_file.append(folklore)
                print('quota exceeded at ')
                print('         ' + str(folklore))
                break
            else:
                print('*** ERROR ***')
                id_counter -= 1
                print(basic_info[2] + '; ' + basic_info[1])
                error_file.append(folklore)
                print("------------------------------------------")
                continue
            # break
        except (TypeError, AttributeError, UnicodeEncodeError):
            print("**********")
            print('failed to obtain oldest info for ' + folklore[1])
            print("**********")
        print("------------------------------------------")
    print(id_counter)

    write_to_file('data/results/' + name + '_result.csv', result_file)
    write_to_file('data/errors/' + name + '_error.csv', error_file)
