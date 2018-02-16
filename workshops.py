from __future__ import division
from munkres import Munkres, print_matrix
from math import ceil

# Quick function for printing things like "1st", "2nd", "3rd", etc
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

workshopNames = [ "Deja Vu", "Chocolate", "Monkey cells" ]

# (Student name, [workshop1 rank, workshop2 rank, ...])
data = [
    ( "Sally"   , [1, 2, 3]) ,
    ( "Jasmine" , [3, 2, 1]) ,
    ( "Cho"     , [2, 3, 1]) ,
    ( "Chetna"  , [1, 2, 3]) ,
    ( "Akumi"   , [1, 3, 2]) ,
    ]

studentsPerWorkshop = int(ceil(len(data) / len(workshopNames)))
mulWorkshopNames = [val for val in workshopNames for _ in range(studentsPerWorkshop)]

# Construct matrix with duplicated workshop rankings 
matrix = []
for item in data:
    matrix.append([val for val in item[1] for _ in range(studentsPerWorkshop)])

m = Munkres()
indexes = m.compute(matrix)
total = 0
for row, column in indexes:
    value = matrix[row][column]
    total += value
    print(data[row][0] + "\t: " + mulWorkshopNames[column] + "\t (" + ordinal(value) + " choice)")
