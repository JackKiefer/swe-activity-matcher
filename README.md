# SWE Activity Matcher

This program is designed to match USU SWE Engineering Extravaganza participants to their preferred workshops in a mathematically optimized way that maximizes satisfaction and minimizes your valuable time as an engineering student having to think about this.

## Usage

**Information last updated Spring 2018.** If this was a previous year to you, some slight adjustments may need to be made to the program. See the next section for details, or make a CS minion do it for you _(recommended)_.

Usage requires knowledge of Python 2.7 and pip. :)

0. Install the only dependency:
```
sudo pip install munkres
```
1. Convert the spreadsheet of signup data to ``.csv`` format. I do this by opening it up in Google Sheets and going to ``File > Download As > Comma-separated values (.csv, current sheet)``. If you use Excel or something else there should be a similar option somewhere. 
2. Rename the file to ``data.csv``
3. Ensure that ``data.csv`` is in the same folder as ``workshops.py``, and simply:
```
python workshops.py
```
4. Voila! Your schedules now exist as ``MasterSchedule.txt`` and ``StudentSchedules.txt`` (they're two different versions of the same schedule). The numbers in parenthesis indicate the particular student's preference ranking for the workshop she's assigned to.

## Maintainence

Howdy! So, there's only a few things that might need to be adjusted year-to-year: the workshop count and names, the number of rounds, and how to parse the signup data.

Luckily, those first two are easily defined right near the top of the file:

```
workshopNames = [ "BE ", "MAE", "CEE", "CS ", "ECE" ]
numRounds = 3
```

Here, we have five workshops (one for each engineering deparment) and three rounds of workshops that each participant will attend. You're free to change these as needed, but...

### Parsing
This is the only kind of tricky thing. By nature of the way that the data comes in to us, the parsing of the CSV file had to be hard-coded in. You may get away with only changing the indices in the following line:

```
data.append( (row[9], map(int, [row[17], row[18], row[19], row[20], row[21]])))
```

Here, we're pulling names from column 9 and preference rankings from columns 17-21. The goal is to construct ``data`` in such a manner:

```
[ ( 'Juliana', [ 1, 2, 5, 3, 4] ),
  ( 'Chetna',  [ 3, 2, 1, 3, 2] ),
  ( 'Akumi',   [ 1, 2, 5, 1, 3] ),
  ( 'Abhu',    [ 5, 2, 1, 3, 2] ),
  ( 'Nicki',   [ 3, 2, 1, 3, 1] ),
  ( 'Cho',     [ 1, 2, 1, 3, 2] ),
  ( 'Javiera', [ 2, 2, 5, 1, 3] ) ]
```

Where the entries in the list of preference rankings correspond to the workshops in ``workshopNames`` (that is, Juliana ranked "BE" her 1st choice, "MAE" her 2nd, "CEE" 5th, "CS" 3rd, and "ECE" 4th). Once you do this, the program will handle the rest! (...in theory)

Finally, if you have any questions, feel free to reach out to me at jack.c.kiefer@gmail.com. No, really, I'm happy to help. :)

## How it works

Wow, you're actually reading this section? Awesome! I think it's actually super cool how this works, too.

As it turns out, this business of assigning a bunch of high-schoolers to workshops and letting them rank which ones they prefer the most can be framed as a variant of the classic [assignment problem.](https://en.wikipedia.org/wiki/Assignment_problem). The algorithm this program uses to solve the problem is the [Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm), also known as the **Munkres assignment algorithm** (hence the name of the python module you have to install). The algorithm actually runs in O(_n³_), but, of course, this is fine as we have a very small dataset to work on.  

In the Hungarian article linked, it gives the example of Armond, Francine, and Herbert each charging a different price to clean the bathroom, sweep the floors, and wash the windows. The goal, then, is to minimize the amount that you have to pay each person to get every job done.

What our program does is arrange a similar matrix but with students instead of workers, workshops instead of cleaning tasks, and preference ranks instead of dollar charges. Now, our goal is to give each student their most preferred workshops, and lo-and-behold the smaller numbers indicate the greater preferences (1 is most preferred, 5 is least), thus our goal is to "minimize" the rankings! 

Internally, the program generates a number of "slots" for each workshop in order to totally frame it in terms of the assignment problem. For example, if there's 50 students and 5 workshops, each workshop will be given 10 "slots" where only one student can be assigned to each slot. A student's preference for a workshop would simply replicated 10 times for each slot. This effectively generates a square matrix for the Hungarian algorithm to solve.

I won't get into details about how the Hungarian algorithm itself works (it's abstracted away by the Python module, anyway), but I hope you've been enlightened a bit by a surprisingly cool real-world application of Computer Science!

