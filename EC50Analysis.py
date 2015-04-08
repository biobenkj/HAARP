__author__ = 'benjaminjohnson'

from EC50 import *

folder = create_folder()
fif = find_input_folder()
x, y, plateid = read_input(fif)
normalizebyz(x,y)
bindata(NORMALGFPDATA,NORMALODDATA)
c1 = findcompound()
makecsvfile_allhits(folder, c1)