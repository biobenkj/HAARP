__author__ = 'benjaminjohnson'
from ActivityMacs import *

folder = create_folder()
fif = find_input_folder()
x, plateid = read_input(fif)
normalizebyz(x)
bindata(NORMALGFPDATA)
c1 = findcompound_allhits()
makecsvfile_allhits(folder, c1)
