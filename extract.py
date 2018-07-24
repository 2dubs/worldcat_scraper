import csv

escape_set = ['MS', 's.a.', 'no date']


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


def tokenize(file):
    result = []
    for row in file:
        # get value from each column
        author = row[0]
        raw_title = row[1]
        raw_yr = row[2]
        journal_book = row[3]
        language = row[4]

        # clean title
        title_tokens = raw_title.split('.')
        title = title_tokens[0]
        # notes = ''.join([x for x in title_tokens[1:] if x != ''])

        # clean year
        yr_tokens = raw_yr.split('-')
        yr = yr_tokens[0]

        # create new row
        new_row = [author, title, yr, language]
        print(new_row)
        result.append(new_row)

    return result


def separate_data(name, size):
    file = read_from_file('data/errors/' + name + '.csv')
    count = 0
    res = []
    for row in file:
        count += 1
        res.append(row)
        if count%size == 0:
            i = count/size
            write_to_file('data/errors/' + name + '_' + str(int(i)) + '.csv', res)
            res = []

    write_to_file('data/errors/' + name + '_' + str(int(count/size)) + '.csv', res)


if __name__ == "__main__":
    # data = read_from_file('data/b0_b1.csv', read_header=False)
    # to_write = tokenize(data)
    # write_to_file('data/real_b0_b1.csv', to_write)

    separate_data('b0_b1_error', 600)