__author__ = 'benjaminjohnson'
from CP import *

folder = create_folder()
fif = find_input_folder()
x, y, plateid = read_input(fif)
normalizebyz(x, y)
bindata(NORMALGFPDATA, NORMALODDATA)
c1, c2, c3 = findcompound()
# c1 = findcompound_allhits()
# makecsvfile_allhits(folder, c1)
plotallclassesdata(CLASSIHIT, CLASSIIHIT, CLASSIIIHIT, folder)