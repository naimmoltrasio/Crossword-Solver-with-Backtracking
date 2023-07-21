from core.crossword import Crossword

crosswd_path = "assets/crossword.txt"
dict_path = "assets/dictionary.txt"

crossword = Crossword(crosswd_path, dict_path)
crossword.solve()

