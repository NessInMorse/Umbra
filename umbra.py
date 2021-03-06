"""
Program to get data out of a whatsapp export file
        and show that data in form of various graphs
version: 0.3
                Streaks plot added
Author: Marc (NessInMorse)
Date: 30 November 2020
"""


from re import split, findall, search
from time import time, mktime
from matplotlib.pyplot import bar,show,plot,subplot,title,pie,legend
from numpy import array


def openFile(filename = ""):
        """
        gives the key to open a file
        in: "Str" a filename
        out: the key to open a file
        """
        return open(filename,"r",encoding='utf-8')


def getData(file, chatter={},
            messages={},
            streak={}, initiator="", start=""):
        """
        Gets all the data out of the text file such as:
                all the names of the chatters with the counts
                        of all their messages,
                the words each user uses and their counts,
                the streaks, the times the users have typed most
        in:
                ~key~ to open a file
                (OPTIONAL)
                        {dict} chatter
                                containing their names as keys
                                with in that, another dictionary
                                containing the words as keys
                                and the counts as values
                        {dict} messages
                                with names as keys,
                                :_int_ counts
                        {dict} streak
                                with the starting point as key
                                :[list]
                                [ending_point,
                                messages,
                                time] as values
                        "Str" initiator
                                the person who started a streak
        out:
                {dict} chatter
                        containing their names as keys
                        with in that, another dictionary
                        containing the words as keys
                        and the counts as values
                {dict} messages
                        with names as keys,
                        :_int_ counts as values
                {dict} streak
                        with the starting point as key
                        :[list]
                        [ending_point,
                        messages,
                        time] as values
        """
        for line in file:
                line = line.strip()
                validation = validate(line)
                if validation == "OK":
                        chatter, active, messages = getChatter(chatter,messages,line)
                        messages = getMessage(messages,active)
                        if active:
                                chatter = getWords(chatter,line,active)
                                streak, initiator, start = getStreaks(line,
                                                               streak,initiator,start,active)
        return chatter, messages, streak


def validate(line):
        """
        checks whether or not a line is a valid message line
        in: "Str" a line consisting of characters
        out: "Str" a validation, either OK, for valid
                                or NOT, for non-valid strings

        """
        if len(line)>0:
                if line[0] in "1234567890":
                        if ":" in line[14:] and "-" in line[14:]:
                                return "OK"
        else:
                return "NOT"

                     
def getChatter(chatter,messages,line,active_chatter=""):
        """
        Gets the chatter in the current message
                and adds that to the dictionary ({chatter} and {messages})
        in:
                {dict} chatter containg all chatters,
                        and words per user
                        and counts for each word
                {dict} messages  (here to add new chatters)
                "Str" current message
                (optional)
                        person that sent the (current) message
        out:
                altered chatter, active_chatter, and messages dictionary

        """
        if line[14:].find(": ") != -1 and\
           line[14:].find("- ") != -1:
                active_chatter = line[14+\
                                line[14:].find("-")+2:\
                                14+line[14:].index(":")]
                if line[14+line[14:].find("- ")+2:\
                        14+line[14:].find(": ")]\
                        not in chatter.keys():
                        
                        active_chatter = line[14+\
                                        line[14:].find("-")+2:\
                                        14+line[14:].index(":")]
                        chatter[active_chatter] = {}
                        messages[active_chatter] = 0
        return chatter, active_chatter, messages


def getMessage(message,active):
        """
        Counts the amount of messages a person has sent
        in: {dict} message, containing the counts per person
                "Str" the person who sent a message
        out:
                {dict} altered message dictionary
        """
        message[active] +=1
        return message


def getWords(chatter,line,active):
        """
        Gets all the words per person and
                adds them if they weren't yet in the dictionary
        in: {dict} chatter containing all the words with their counts per user
            "Str" a line containing the characters, and words to be added
            "Str" the current person that has sent a message

        out:
                {dict} Altered chatter, containg the new words with their counts,
                        for the person that was active
        """
        line = ''.join(findall("[a-zA-Z\s]",line[14+line[14:].index(":")+2:]))
        words = split("\s",line)
        if words == ["Media","weggelaten"]:
                words = []
        for word in words:
                if word[1:].lower() == word[1:] and word!="":
                        word = word.lower()
                        if word in chatter[active]:
                                chatter[active][word] += 1
                        else:
                                chatter[active][word] = 1
        return chatter


def getStreaks(data, streak, init, start="", user="",maxpause=900):
        """
        gets the streak of messages within a max time limit of pauses
        in: "Str" a line with the data in the form of a social media message
            {dict} a streak dictionary containing dates when streaks
                started and the such
            "Str" the initiator of the streak, the person that sent the
                        first message
                (optional) _int_ the maximum amount of seconds a pause can
                                lost before counting as a new start
                                (minimum of 60 seconds or the program
                                won't run correctly)

        out:
                {dict} an altered streaks dictionary, with a new ending point
                        and length in the list
                "Str" the initiator of the message
        """
        dates = ''.join(findall("[\d]+.[\d]+.[\d]+.[\d]+:[\d]+\s", data[:15]))
        if len(dates)>0:
                split_character = search("\D",dates)[0]
                dates = dates.split(split_character)
                # year, month, day, hour, minute, second, x, y, z
                current = (int("20" + dates[2][:2]),
                                   int(dates[1]),
                                   int(dates[0]),
                                   int(dates[2][-6:-4]),
                                   int(dates[2][-3:-1]),
                                   0,
                                   0,
                                   0,
                                   0)
                current_time = data[:14]

                if streak == {}:
                        start = data[:14]
                        streak[start] = [current,current,current_time,1,user]
                elif (mktime(current)-mktime(streak[start][1])) < maxpause:
                        streak[start][1] = current
                        streak[start][2] = current_time
                        streak[start][3] += 1
                else:
                        start = data[:14]
                        streak[start] = [current,current,current_time,1,user]
        return streak, init, start


def countWords(c_chatter):
        """
        Sorts all the words per person based on count
                and prints out the top 5
        in:
                {dict} chatter dictionary containing all the words
        out:
                :print:
                        top 5 most used words per person
        """
        sortable_words = [0 for i in c_chatter]
        names = [i for i in c_chatter.keys()]
        for n in range(len(names)):
                sortable_words[n] = [(word, c_chatter[names[n]][word])
                                     for word in c_chatter[names[n]]
                                     ]
        for i in range(len(sortable_words)):
                sortable_words[i].sort(key=lambda x: x[1], reverse=True)
                for j in range(len(sortable_words[i][:5])):
                        if sortable_words[i][j][1]>50:
                                print(f"{names[i]:<15} #{j+1:<3} {sortable_words[i][j][0]:<9} {sortable_words[i][j][1]:<6}")
                        else:
                                break
                else:
                        print("")
        return sortable_words, names
        

def showCountWords(s_sortable_words,names):
        words = [[] for i in s_sortable_words]
        count = [[] for i in s_sortable_words]
        maximum = 100
        number = 0
        for person in range(len(s_sortable_words)):
                for j in range(len(s_sortable_words[person][:maximum])):
                        words[person].append(s_sortable_words[person][j][0])
                        count[person].append(s_sortable_words[person][j][1])
        
        for j in range(len(words)):
                if len(words[j])==maximum:
                        number += 1
        for i in range(number):
                if len(words[i])==maximum:
                        subplot(1,number,i+1)
                        x = array(words[i])
                        y = array(count[i])
                        plot(x,y)
                        title("wordcount: "+names[i])
        show()

def showMessageCount(messages):
        """
        Shows the messages of each user in a bargraph
        in: {dict} all the messages per user in the form of:
            "Str"       {user}:count (int)

        out: a bargraph with all the counts of users in different bars
                
        """
        x = [i for i in messages.keys()  if messages[i]>500]
        y = [i for i in messages.values()if i>500]
        pie(y, labels = x)
        title("Messagecount")
        legend(title = "Relative Message Count")
        show()


def showStreaks(streak):
        streak = sorted(streak.items(), key = lambda kv:(kv[1][3], kv[0]), reverse=True)
        print(len(streak))
        x = [f"{i[0]}-{i[1][2]}" for i in streak[:15]]
        y = [int(i[1][3]) for i in streak[:15]]
        plot(x,y)
        title("Streak and their counts")
        show()

def main():
        begin = time()
        file = openFile()
        chatter, messages, streak = getData(file)
        names = [i for i in chatter.keys()]

        for i in names:
                if messages[i]>500:
                        print(messages[i])
        print(sum([i for i in messages.values()]))
        sortable_words, names = countWords(chatter)
        showCountWords(sortable_words,names)
        showMessageCount(messages)
        showStreaks(streak)
        end = time()
        print(end-begin)
        
main()
