import copy
from shapely.geometry import LineString


class Word:
    """
    Class attributes:

    @attr start_coord   coordinates of the starting point
    @attr end_coord     coordinates of the ending point
    @attr orientation   horizontal word = 0, vertical word = 1
    @attr length        total word length
    @attr value         text assigned to the word

    """
    start_coord = ()
    end_coord = ()
    orientation = 0
    length = 0
    value = ''


class Crossword:
    """
    Class attributes:

    @attr crossword         array representing the crossword layout
    @attr word_lst          list of words from the dictionary
    @attr valid_word_lst    list of valid words for the current crossword
    @attr solution          crossword solution
    @attr solved_crossword  representation of the solved crossword
    """
    word_lst = []
    crossword = []
    valid_word_lst = []
    solution = []
    solved_crossword = []

    """
    Initialices crossword object
    @param cross_path   path of the file containing the crossword txt
    @param dict_path    path of the file containing the dictionary txt
    """
    def __init__(self, cross_path: str, dict_path: str):
        self._load_crossword(cross_path)
        self._load_dictionary(dict_path)
        self.valid_word_lst = self._find_horizontal_words() + self._find_vertical_words()
        self.solved_crossword = copy.deepcopy(self.crossword)

    """
    Loads the crossword from a txt file and parses it into an array
    
    @param file_path relative/absolute path of the file
    @return array representing the crossword
    """
    def _load_crossword(self, file_path: str):
        # open file object
        with open(file_path, 'r') as cfile:
            file = cfile.readlines()
        # parse each line of the document and append it to the list
        for line in file:
            replaced = line.replace("\t", "")
            replaced = replaced.replace("\n", "")
            replaced = replaced.replace(" ", "")
            self.crossword.append(list(replaced))

    """
    Loads the dictionary from a txt file and pareses it into a list
    
    @param file_path relative/absolute path of the file
    @return word list of the dictionary
    """
    def _load_dictionary(self, file_path: str):
        # open file object
        with open(file_path, 'r') as dfile:
            file = dfile.readlines()
        # parse each line of the document and append it to the list
        for line in file:
            replaced = line.replace("\n", "")
            self.word_lst.append(replaced)

    """
    Gets all the possible horizontal words for the crossword layout
    
    @return  list of horizontal words   
    """
    def _find_horizontal_words(self):
        horizontal_words = []

        # for each row check the word with the length and put it in the list
        for row in range(len(self.crossword)):
            column = 0
            word = Word()
            finished = False
            prev = '#'  # prev mean the previous char in the word

            # while not in the last column
            while column <= len(self.crossword[row]) - 1:
                if self.crossword[row][column] == '0':
                    if prev == '0':
                        word.length += 1
                        prev = '0'
                        if column == len(self.crossword[row]) - 1:
                            if not finished:
                                finished = True
                            word.end_coord = (row, column)
                            prev = '#'

                    elif prev == "#":
                        if finished:
                            finished = False
                        word.start_coord = (row, column)
                        word.length += 1
                        prev = '0'

                elif self.crossword[row][column] == '#':
                    if prev == '0':
                        if not finished:
                            finished = True
                        if word.length > 1:
                            word.end_coord = (row, column - 1)
                        else:
                            word = Word()
                        prev = '#'

                if word.length > 1 and finished:
                    word.orientation = 0
                    horizontal_words.append(word)
                    word = Word()
                    finished = False

                column += 1
        return horizontal_words

    """
    Gets all the possible vertical words for the crossword layout

    @return  list of vertical words   
    """
    def _find_vertical_words(self):
        vertical_words = []
        word = Word()

        for column in range(0, len(self.crossword[0])):
            started = False
            for row in range(0, len(self.crossword) - 1):
                if self.crossword[row][column] == '0' and self.crossword[row + 1][column] == '0':
                    # for x in starting_points:
                    if not started:
                        started = True
                        word.start_coord = (row, column)
                        # break
                    if row == len(self.crossword) - 2 and started:
                        word.end_coord = (row + 1, column)
                        word.length = word.end_coord[0] - word.start_coord[0] + 1
                        word.orientation = 1
                        vertical_words.append(word)
                        word = Word()
                        started = False
                else:
                    if started:
                        word.end_coord = (row, column)
                        word.length = word.end_coord[0] - word.start_coord[0] + 1
                        word.orientation = 1
                        vertical_words.append(word)
                        word = Word()
                        started = False
        return vertical_words

    """
    Prints the crossword layout into the terminal console
    """
    def print_layout(self):
        print("---------- Crossword ---------")
        for line in self.crossword:
            print(line)
        print("------------------------------")

    """
    Recursive function wich bruteforcess all the posible words for each space in the crossword
    
    @param avl assigned variable list
    @param navl not assigned variable list
    """
    def _backtracking(self, avl, navl):
        # there are no variables to assign a value, so we are done
        if len(navl) == 0:
            return avl

        var = navl[0]
        possible_val = self._get_possible_values(var, avl)

        for val in possible_val:
            # we create the variable check_var to do the checking and avoid assigning values which do not comply with
            # the constraint
            check_var = copy.deepcopy(var)
            check_var.value = val

            if self._check_constraint(check_var, avl):
                var.value = val
                result = self._backtracking(avl + [var], navl[1:])
                if result is not None:
                    return result
                # we've reached here because the choice we made by putting some 'word' here was wrong
                # hence now leave the word cell unassigned to try another possibilities
                var.value = ''
        return None

    """
    Get all the domain values for the current word length
    
    @param var word to be checked
    @param avl assigned variable list
    @return word list for the given word length
    """
    def _get_possible_values(self, var, avl):
        possibles_values = []
        # check if they have the same size
        for val in self.word_lst:
            if len(val) == var.length:
                possibles_values.append(val)
        # if exists in avl, remove from possible values
        for item in avl:
            if item.value in possibles_values:
                possibles_values.remove(item.value)

        return possibles_values

    """
    Treat words here like lines so we find the intersection point of horizontal and vertical words (the character 
    position - intersection point is the constraints which the algorithm must apply to get a valid solution)
    
    @param word1 Word object
    @param word2 Word object
    @return coordenates where the intesection has happened
    """
    def _check_intersections(self, word1, word2):
        line1 = LineString([word1.start_coord, word1.end_coord])
        line2 = LineString([word2.start_coord, word2.end_coord])

        intersection_point = line1.intersection(line2)

        if not intersection_point.is_empty:
            return [intersection_point.coords[0]]  # result(float)
        else:
            return []

    """
    Checks if the given value (var) meets the restrictions
    @param var word to be checked
    @param assigned variable list
    
    @retur true if meets the restriction, false if not
    """
    def _check_constraint(self, var, avl):
        if avl is not None:
            for word in avl:
                # if orientation is equal they will never interesect!
                if var.orientation != word.orientation:
                    intersection = self._check_intersections(var, word)
                    if len(intersection) != 0:
                        if var.orientation == 0:  # horizontal
                            if var.value[int(intersection[0][1] - var.start_coord[1])] != \
                                    word.value[int(intersection[0][0] - word.start_coord[0])]:
                                return False
                        else:  # vertical
                            if var.value[int(intersection[0][0] - var.start_coord[0])] != \
                                    word.value[int(intersection[0][1] - word.start_coord[1])]:
                                return False
        return True

    """
    Inserts word value to the crossword layout
    
    @param word     value to be inserted
    @param coord    coordinates of the crossword
    @param orientation 
    """
    def _insert_to_crossword(self, word, coord, orientation):
        pos_count = 0

        for char in word:
            if orientation == 0:  # horizontal if orientation == 0
                self.solved_crossword[coord[0]][coord[1] + pos_count] = char
            else:
                self.solved_crossword[coord[0] + pos_count][coord[1]] = char
            pos_count += 1

    """
    Prints the crossword solution
    """
    def print_solution(self):
        for word in self.solution:
            self._insert_to_crossword(word.value, word.start_coord, word.orientation)

        for line in self.solved_crossword:
            print(line)


    """
    Solves the crossword
    """
    def solve(self):
        avl = []
        navl = self.valid_word_lst
        self.solution = self._backtracking(avl, navl)

        if self.solution is not None:
            self.print_solution()
        else:
            print("No solution found")

