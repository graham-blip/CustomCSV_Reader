# CSV Reader

## Introduction

This goal of this work is to illustrate how a CSV file can be parsed programmatically, into an appropriate python data structure. It was essential not to use any existing CSV parsing libaries. 

## How to use the CSV Reader

The ReadCSV module must first be imported: 

```
import ReadCSV
```

Then the following function can be called with the filepath to the CSV file that should be parsed.

```
ReadCSV.read_csv(filepath, header = True)
```

The above function returns the contents of the CSV in a list of dictionaries. By default the header argument is optional and if ommitted then it assumes the first row is a header. Alternatively, this parameter can be set to False and the dictionary keys will simply be set as integers. 

## Choice of Method

There are many different ways this could have been approached either by a line by line reading method in chunks or charachter by character. In the end the chosen method used was a finite-state machine, where it changes from one state to another in reponse to the input value which it is currently parsing. Each line starts with the StartCSVReader state and then ends with the LineEnd state. In the intermediate states depending on the type of charachter it can encounter then it will transition accordingly.  

The majority of the actual methods used within the code is managed by Python's in-built system such as open and strip.  

While there are an endless number of possibilities as to what a CSV file could contain and different layout chrachters the following functions deal with the three main charachters that have been hard coded into the program:  

```
    def comment(self):
        return self.current_char == '#'

    def quotation(self):
        return self.current_char == '"'

    def delimiter(self):
        return self.current_char == ','
````

These are the hashtag #, the double quote " and the comma (delimiter) ','.

## Overview of the Code

Initial CSVReader class is:

```
class CSVReader:
    def __init__(self, line, header = None):
        self.line = line
        self.header = header
        self.state = StartCSVReader()
        self.current_char = line[0]
        self.current_field = ''
        self.value = list()
```

This calls the StartCSVReader class which is:

```
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
```

To assign a line end or comment it calls a line_end function:

```
    def line_end(self):
        return self.current_char == len(self.line)-1
```
or the comment function (above). Else it is able to assign a NextChar class which allows it to move on. The program then iterates through the entire CSV file and assigns a class at each state. Below are each of the possible classes that are used:

```
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
 
class Comment:
    def next_char(self, char_state):
        if char_state.line_end():
            char_state.state = LineEnd()
            return False
        return True
```

Finally, there are three functions:

- The parse function. This initiates the CSVReader class.
- The merge_header function. This merges the header with the values inside the columns.  
- The read_csv function this is the actual function which the end user must use to parse the CSV.

## Conclusion and Future Work

How does this CSV compare against existing readers out there?  

Well for one it is a lot slower and more work can be done to optimise the efficiency of this reader. An easy change is to allow for the dilimeter, or comment charachter to be defined by the user in the end function. Perhaps even give the user a wider selection over what type of python data format the data is returned in.  

Furthermore, the reader does not attempt to detect the datetype e.g. datetime or integer etc. However, this  often lead to issues with the existing CSV packages with data being easily miscalssified and models being built that are dealing with incorrect data types. As such for a custom CSV reader being able to then manually define the datatype may be less damaging when going on to build models and conduct further analysis with the data.
