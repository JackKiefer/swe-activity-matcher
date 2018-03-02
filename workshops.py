from __future__ import division
from munkres import Munkres, print_matrix
from math import ceil
import csv
import json

# Global constants #
csvDataFileName = 'data.csv'
workshopNames = [ "BE ", "MAE", "CE ", "CS ", "ECE" ]
numRounds = 3

# Global data sets
data = []
rounds = []
studentSchedules = {}

def readData():
    csvfile = open(csvDataFileName, 'r')
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i > 2:
            data.append( (row[9], map(int, [row[17], row[18], row[19], row[20], row[21]])))
            studentSchedules[row[9]] = []
    csvfile.close()

def printRound(wRounds):
    for i, workshop in enumerate(wRounds):
        print workshop + ":"
        for student in wRounds[workshop]:
            print "(" + student[1] + ") " + student[0]
        print ""

def computeRound(roundID):
    studentsPerWorkshop = int(ceil(len(data) / len(workshopNames)))
    mulWorkshopNames = [val for val in workshopNames for _ in range(studentsPerWorkshop)]

    # Construct matrix with duplicated workshop rankings 
    matrix = []
    for item in data:
        matrix.append([val for val in item[1] for _ in range(studentsPerWorkshop)])

    m = Munkres()
    indexes = m.compute(matrix)
    
    workshopRound = {x : [] for x in workshopNames}

    for row, column in indexes:
        interestRank = str(matrix[row][column])
        name = data[row][0]
        workshop = mulWorkshopNames[column]
        workshopRound[workshop].append(( name , interestRank ))

        studentSchedules[name].append((r,workshop, interestRank))

        data[row][1][workshopNames.index(workshop)] = 2*studentsPerWorkshop

    rounds.append(workshopRound)

def printSchedule():
    for r in range(0,numRounds):
        print "\n === ROUND " + chr(r+65) + " ===\n"
        printRound(rounds[r])

def printStudentSchedules():
    for name in studentSchedules:
        print name + ":" 
        for x in studentSchedules[name]:
            print "Round " + chr(x[0]+65) + "> " + x[1] + " (" + x[2] + ")"
        print ""


readData()
for r in range(0,numRounds):
    computeRound(r)

printSchedule()
#printStudentSchedules()
