# workshops.py
# 
# Copyright (C) 2018 Jack Conrad Kiefer II
# 
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from __future__ import division
from munkres import Munkres, print_matrix
from math import ceil
import csv
import json

# Global constants
# TODO: Start here to adjust appropriately
csvDataFileName = 'data.csv'
workshopNames = [ "BE ", "MAE", "CEE", "CS ", "ECE" ]
numRounds = 3

# Global data sets
data = []
rounds = []
studentSchedules = {}


"""
Read in workshop preference data from the CSV and construct the "data" list
SAMPLE DATA:
[ ( 'Juliana', [ 1, 2, 5, 3, 5] ),
  ( 'Chetna',  [ 3, 2, 1, 3, 2] ),
  ( 'Akumi',   [ 1, 2, 5, 1, 3] ),
  ( 'Abhu',    [ 5, 2, 1, 3, 2] ),
  ( 'Nicki',   [ 3, 2, 1, 3, 1] ),
  ( 'Cho',     [ 1, 2, 1, 3, 2] ),
  ( 'Javiera', [ 2, 2, 5, 1, 3] ) ]
"""
def readData():
    csvfile = open(csvDataFileName, 'r')
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i > 2:
            # TODO: Adjust this to actually fetch the data properly however you need it.
            data.append( (row[9], map(int, [row[17], row[18], row[19], row[20], row[21]])))
            studentSchedules[row[9]] = []
    csvfile.close()

"""
Print each workshop and its participants for a given round
"""
def printRound(wRound, f):
    for i, workshop in enumerate(wRound):
        f.write(str(workshop) + ":\n")
        for student in wRound[workshop]:
            f.write("(" + student[1] + ") " + student[0] + "\n")
        f.write('\n')

"""
Compute the optimal workshop selections for a given round using the Munkres algorithm
and store it in a human-readable schedule.
roundID is a positive integer denoting the nth round
"""
def computeRound(roundID):
    # Assume students can be evenly divided into each workshop
    studentsPerWorkshop = int(ceil(len(data) / len(workshopNames)))

   # Construct matrix with duplicated workshop rankings 
    matrix = []
    for item in data:
        matrix.append([val for val in item[1] for _ in range(studentsPerWorkshop)])

    # Compute solution with Munkres
    m = Munkres()
    indexes = m.compute(matrix)
    
    # We'll use this to store all of the solution data for the current round
    workshopRound = {x : [] for x in workshopNames}

    # Generate a list with duplicate workshop names to represent the number of "slots"
    # available for each workshop
    mulWorkshopNames = [val for val in workshopNames for _ in range(studentsPerWorkshop)]
 
    # Begin parsing Munkres solution back into human-readable data
    for row, column in indexes:
        # Fetch the data points that matter
        interestRank = str(matrix[row][column])
        name         = data[row][0]
        workshop     = mulWorkshopNames[column]

        # Store in this round's schedule
        workshopRound[workshop].append(( name , interestRank ))

        # Store in the student-wise schedule
        studentSchedules[name].append((r,workshop, interestRank))

        # This is a bit of a hack: Whatever workshop was selected, replace its
        # preference rank in the matrix with a large number so that Munkres
        # won't pick it again when we compute the next round.
        # 2*studentsPerWorkshop is an arbitrary choice that is sufficiently large.
        data[row][1][workshopNames.index(workshop)] = 2*studentsPerWorkshop

    # Finally, append this round's schedule to the master schedule
    rounds.append(workshopRound)

"""
Print the master schedule
"""
def printSchedule():
    f = open('MasterSchedule.txt','w')
    for r in range(0,numRounds):
        f.write("\n==== ROUND " + chr(r+65) + "====\n\n")
        printRound(rounds[r], f)

"""
Print the student-wise schedule
"""
def printStudentSchedules():
    f = open('StudentSchedules.txt','w')
    for name in studentSchedules:
        f.write(name + ":\n")
        for x in studentSchedules[name]:
            f.write("Round " + chr(x[0]+65) + "> " + x[1] + " (" + x[2] + ")\n")
        f.write('\n')


# Begin main 

readData()
for r in range(0,numRounds):
    computeRound(r)

printSchedule()
printStudentSchedules()
print "Successfully created StudentSchedules.txt and MasterSchedule.txt!"

# end main
