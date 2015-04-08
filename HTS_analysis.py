__author__ = 'benjaminjohnson'
from HTS import *

folder = create_folder()
fif = find_input_folder()
x,y,plateid = read_input(fif)
normalizebyz(x,y)
bindata(NORMALGFPDATA,NORMALODDATA)
a = calcz()
plotbindata(folder, a)
twodplot(folder)
findcompound()
plotCIdata(CLASSIHIT, folder)
plotCIIdata(CLASSIIHIT, folder)
plotCIIIdata(CLASSIIIHIT, folder)
plotallclassesdata(CLASSIHIT, CLASSIIHIT, CLASSIIIHIT, folder)
makecsvfile(folder)
#writealldata(folder)
#comparehits(folder)
#badwells(folder)