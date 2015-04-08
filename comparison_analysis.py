__author__ = 'benjaminjohnson'

from compare_screens import *

folder = create_folder()
d1, d2 = find_input_folder()
read_inputs(d1, d2)
comparison()
makeavenndiagram(folder)
# fancyvenndiagram(folder)
writeitout(folder)