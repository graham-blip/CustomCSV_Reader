import sys 


class CSVReader:
    def __init__(self, line, header = None):
        self.line = line
        self.header = header
        self.state = StartCSVReader()
        self.current_char = line[0]
        self.current_field = ''
        self.value = list()

    def store_char(self):
        if self.current_field:
            self.value.append(self.current_field)
        self.current_field = ''

    def get_value(self):
        if self.header and len(self.value) != len(self.header):
            raise Exception('Number of columns is not equal to the number of headers')
        elif self.header:
            return {a:b for a,b in zip(self.header, self.value)}
        else:
            return {a: b for a, b in zip(range(len(self.value)), self.value)}

    def next_char(self, char):
        self.current_char = char
        return self.state.next_char(self)

    def line_end(self):
        return self.current_char == len(self.line)-1

    def comment(self):
        return self.current_char == '#'

    def quotation(self):
        return self.current_char == '"'

    def delimiter(self):
        return self.current_char == ','



class Comment:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        return True

class NextChar:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        elif char_state.quotation():
            char_state.state = QuotationMark()
            return True
        else:
            char_state.state = RegularCharachter()
            return False

class StartCSVReader:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        elif char_state.comment():
            char_state.state = Comment()
            return False
        else:
            char_state.state = NextChar()
            return False

class LineEnd:
    def next_char(self, char_state):
        char_state.store_char()
        return True

class QuotationMark:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        elif char_state.quotation():
            char_state.state = RepeatedInvertedCommas()
            return True
        else:
            char_state.current_field += char_state.current_char
            return True

class RegularCharachter:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        elif char_state.delimiter():
            char_state.state = NextChar()
            char_state.store_char()
            return True
        else:
            char_state.current_field += char_state.current_char
            return True

class RepeatedInvertedCommas:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        elif char_state.delimiter():
            char_state.state = NextChar()
            char_state.store_char()
            return True
        elif char_state.quotation():
            char_state.current_field += char_state.current_char
            char_state.state = QuotationMark()
            return True
        else:
            raise Exception('Letter after second quotation mark')


def read_csv(path, header = True):
    """ 
    Parse a csv file
    :param path: file path
    :param header: Deafult = True set to False if CSV file does not contain header
    :return: list of dictionaries with the data from the CSV file.
    """
    #Initilaise the counters
    Total = 0
    Read = 0
    Fail = 0
    #Create an empty list to insert the CSV
    Doc = []
    Col_Header = None
    with open(path, 'r+', encoding='utf-8-sig') as csv:
        for line in csv:
            stripped_line = line.strip()

            if not stripped_line:
                continue

            Total += 1
            if (Total > 999999):
                print("TExceeded size limit")
                break;

            try:
                value = parse(stripped_line)
                if header and Total==1:
                    Col_Header = list(value.values())
                else:
                    Doc.append(value)
                Read += 1
            except:
                print("Error: {1}, Line: {0} System Error: {2}".format(Total, line, sys.exc_info()[0]))
                Fail += 1
        else:
            pass

    print("{0} lines read out of {1}. {2} failed".format(Total, Read, Fail))
    return merge_header(Doc, Col_Header)

def parse(line):
    state = CSVReader(line)
    for char in line:
        while True:
            process_next = state.next_char(char)
            if process_next:
                break
    state.store_char()
    return state.get_value()

def merge_header(values, header):
    if not header:
        if values:
            cols = len(values[0])
            return [i for i in values if len(i) == cols]
        else:
            return []
    elif not values:
        return {j:None for j in header}
    else:
        cols = len(header)
        parsed_lines = [i for i in values if len(i) == cols]
        Doc = [{a:b for a,b in zip(header, rec.values())} for rec in parsed_lines]
        return Doc

