# workshops.py
# 
# Copyright (C) 2018 Jack Conrad Kiefer II
# 
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from __future__ import division
print "Starting up workshop matcher...\n"

from munkres import Munkres, print_matrix
from math import ceil
from nameparser import HumanName
import csv
import json
import re

# Global constants
# TODO: Start here to adjust appropriately
csvDataFileName = 'data.csv'
workshopNames = [ "BE ", "MAE", "CEE", "CS ", "ECE" ]
numRounds = 3

# Global data sets
data = []
rounds = []
studentSchedules = {}
roommatePairs = []

def lastFirstToFirstLast(s):
    list = [x.strip() for x in s.split(',')]
    return list[1] + " " + list[0]

"""
Print out the indices of each column of data in the CSV.
Useful for figuring out how to parse the CSV.
"""
def getCsvDataIndices():
    csvfile = open(csvDataFileName, 'r')
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i == 0:
            for j, item in enumerate(row):
                print j, item
    csvfile.close()

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
        if i > 0:
            # TODO: Adjust this to actually fetch the data properly however you need it.
            name = lastFirstToFirstLast(row[0])
            data.append( (name, map(int, [row[10], row[11], row[12], row[13], row[14]])))
            studentSchedules[name] = []
            if row[16] != "":
                roommatePairs.append((name, row[16]))
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
    for r in range(-numRounds + 1, 1):
        f.write("\n==== ROUND " + str(numRounds+r) + " ====\n\n")
        printRound(rounds[-r], f)

"""
Print the student-wise schedule
"""
def printStudentSchedules():
    f = open('StudentSchedules.txt','w')
    for name in studentSchedules:
        f.write(name + ":\n")
        for x in reversed(studentSchedules[name]):
            f.write("Round " + str(numRounds - x[0]) + "> " + x[1] + " (" + x[2] + ")\n")
        f.write('\n')

def parseRoommates(roommatePairs):
    parsedPairs = []
    for (a,b) in roommatePairs:
        name = a
        mates = re.split(',| and | or ',b)
        for x in mates:
            x.strip(" and ")
            x.strip(" or ")
        parsedPairs.append((name,mates))
    return parsedPairs

def toNames(pairs):
    newPairs = []
    for (a,b) in pairs:
       x = HumanName(a)
       y = map(HumanName, b)
       newPairs.append((x,y))
    return newPairs

def getHumanNameList():
    newList = []
    for entry in data:
        newList.append(HumanName(entry[0]))
    return newList

def findMatches(roommatePairs):
    newPairs = {}
    matchables = []
    allNames = getHumanNameList()
    nonMatch = False
    matchCounter = 0
    for (host,mates) in roommatePairs:
        allMatches = []
        for mate in mates:
            matches = [x for x in allNames if (x.first.lower() == mate.first.lower() and x.last.lower() == mate.last.lower())]
            if matches == []:
                print "Unable to find " + str(host) + "'s roommate preference: " + str(mate)
                nonMatch = True
            else:
                allMatches.append(matches[0])
                matchCounter = matchCounter + len(matches)
        if allMatches != []:
            m = map(str, allMatches)
            newPairs[str(host)] = m
            matchables.append(str(host))

    if nonMatch:
        print "Check to ensure that names were not misspelled. If they were, doctor the data and re-run.\n"

    print "Successfully found " + str(matchCounter) + " roommate preferences in participant pool!\n"
    print "Proceeding with schedule generation..."
    return (newPairs, matchables)

def forEveryMatchableStudent(func, matchables, mateMatches):
    # For every round
    for r in range(0,numRounds):
        #print "\n\n@@@@@ Round " + str(r) + " @@@@@\n"
        # For every workshop
        for i,workshop in enumerate(rounds[r]):
            #print "\n===== " + str(workshop) + " ====="
            # For every student in workshop that has roommate preferences
            for student in rounds[r][workshop]:
                name = student[0]
                if (name in matchables):
                   func(r, workshop, student, mateMatches, matchables) 

def swapToRound(toRound, workshop, student, fromRound, matchables):
#    print "Swapping " + str(student) + " to " + str(toRound) + str(workshop) + "..."
    # Swap in the student schedules
    a = studentSchedules[student][fromRound]
    b = studentSchedules[student][toRound]
    studentSchedules[student][fromRound] = (fromRound, b[1], b[2])
    studentSchedules[student][toRound] = (toRound, a[1], a[2])

    workshopA = a[1]
    workshopB = b[1]

    # Within the same rounds, swap student workshops

    # Find the student in workshop A in fromRound to delete them
    delIndex = 0;
    found = False;
    for i in range(0,len(rounds[fromRound][workshopA])):
        if rounds[fromRound][workshopA][i][0] == student:
            delIndex = i
            found = True
    if not found:
        #TODO actually throw exception
        print "EEEEEEEEEERRRRRRRRRRRRROOOOOOOOOOOORRRRRRRR"
            
    del rounds[fromRound][workshopA][delIndex]# = (student, 'null')

    # Add the student to workshop B in fromRound
    rounds[fromRound][workshopB].append((student, b[2]))

    found = False
    delIndex = 0
    # Find the student in workshop B in toRound to delete them
    for i in range(0,len(rounds[toRound][workshopB])):
        if rounds[toRound][workshopB][i][0] == student:
            delIndex = i
            found = True

    if not found:
        #TODO actually throw exception
        print "EEEEEEEEEERRRRRRRRRRRRROOOOOOOOOOOORRRRRRRR"
 
    del rounds[toRound][workshopB][delIndex]# = (student, 'null')
    # Add the student to workshop A in toRound
    rounds[toRound][workshopA].append((student,a[2]))
    


        
# Both student and mate have same workshop but different rounds
def pairInWorkshop(studentRound, mateRound, workshop, student, mate, matchables):
    studentWorkshopSize = len(rounds[studentRound][workshop])
    mateWorkshopSize    = len(rounds[mateRound][workshop])

    if studentWorkshopSize < mateWorkshopSize:
        swapToRound(studentRound, workshop, mate, mateRound, matchables)
    else:
        swapToRound(mateRound, workshop, student[0], studentRound, matchables)

"""
Pair roommates who were matched to the same workshops
r - Round number
workshop - workshop name
student - name and preference rank
mateMatches - dictionary of all roommates pairings
"""
def pairRoommates(r, workshop, student, mateMatches, matchables):
    name = student[0]
    rank = student[1]
    studentMatches = mateMatches[name]
    matesWithSameWorkshop = []
    for mate in studentMatches:
        for matesWorkshop in studentSchedules[mate]:
            matesWorkshopRound = matesWorkshop[0]
            matesWorkshopName  = matesWorkshop[1]
            if (matesWorkshopName == workshop) and (r != matesWorkshopRound):
#                print name + " is " + str(r) + workshop + ", but " + mate + " is " + str(matesWorkshopRound) + matesWorkshopName
                pairInWorkshop(r, matesWorkshopRound, workshop, student, mate, matchables)


# Begin main 
readData()

(mateMatches, matchables) = findMatches(toNames(parseRoommates(roommatePairs)))

for r in range(0,numRounds):
    computeRound(r)

forEveryMatchableStudent(pairRoommates, matchables, mateMatches)

printSchedule()
printStudentSchedules()
print "Successfully created StudentSchedules.txt and MasterSchedule.txt!"

# end main
