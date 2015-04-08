__author__ = 'benjaminjohnson'

from knockdown import *


folder = create_folder()
fif = find_input_folder()
x, y, plateid = read_input(fif)
normalizebyz(x, y)
bindata(NORMALGFPDATA, NORMALODDATA)
c1 = findcompound_allhits()
c1d, c2d, c3d = knockdown(c1)
makecsvfile_allhits(folder, c1d, c2d, c3d)