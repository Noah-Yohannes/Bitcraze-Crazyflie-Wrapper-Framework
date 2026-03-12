import os 

def read_sequences_from_file(file):
    with open(file,'r') as fil:
        a = fil.readlines()
        a = [float(i.replace('\n', '')) for i in a]

    return a 

def save_sequences_to_file(sequence, file):
    with open(file, 'w') as fil:
        for i in sequence:
            fil.write(str(i)+'\n')
    print("File saved successfully. ")

def read_tuple(file): 
    """Reads a tuple and returns a list of each dimension"""

    with open(file,'r') as fil:
        a = fil.readlines()
        a = [i.replace('\n', '') for i in a]
        a = [i.replace('(', '') for i in a]# replacing tuple braces
        a = [i.replace(')', '') for i in a]  # replacing tuple braces
        # check how many elements each tuple or entry has
        a = [i.split(',') for i in a]  # separating the string with the comma
        final_output = []
        for i in a:
            number_of_elements = len(i)  # how many samples does each tuple have 
            one_list_element_list = []

            # iterating over all elements/entries
            for r in range(number_of_elements):
                one_list_element_list.append(float(i[r]))  # updating each entry tuple elements
            
            one_list_element_tuple = tuple(one_list_element_list)  # converting list to tuple

            final_output.append(one_list_element_tuple)
            
    return final_output
