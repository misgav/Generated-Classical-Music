import os,sys,subprocess,codecs,csv

class compresser:

    def __init__(self,file):
        self.file = file # file name

    def decompress(self,val):
        data_file = 0

        if val == 1:
            data_file = codecs.open(self.file,"r","utf-8") # read the file
        else:
            data_file = codecs.open("./Dataset/Compressed/" + self.file,"r","utf-8") # read the file

        loc = self.file.split("/")
        self.file = loc[len(loc)-1]

        clock_time = 0 # current time
        step = 0 # step size to increment time
        start_reading = 0 # when to start decompressing the file
        control_on = 0 # whenever to hold the pedal
        note_on = 1 # checking whenever the program saw a note being pressed
        track_num = 1 # current track number

        held_on_notes = [] # notes currently being held on to
        output = "" # final output
        per_quater = 0
        track_total = 0
        
        for line in data_file:
            if ("START READING" in line):
                # starting to read and decompress the txt file
                start_reading = 1
            elif (start_reading==0):
                if "Header" in line:
                    # getting the time sequance
                    text_vec = line.split(", ")
                    per_quater = int(text_vec[5])
                    step = int(per_quater/4)/8 #1/128 of a note
                    track_total = int(text_vec[4])
                else:
                    if line != "":
                        # to avoid errors when using csvmidi, we need to follow up with the track and clock time
                        vec = line.split(", ")
                        track_num = int(vec[0])
                        clock_time = int(vec[1])
                output = output + line.replace('"',"") # this is also used to avoid errors with cvsmidi

            else:
                # starting decompressing here
                text_vec = line.split(" ")
                for i in text_vec:
                    if i == "":
                        # if the text is a blank space then we hold the pedal
                        if control_on == 0:
                            control_on = 1
                            output = output + str(track_num) + ", " + str(clock_time) + ", Control_c, 0, 64, 127\n"
                        else:
                            control_on = 0
                            output = output + str(track_num) + ", " + str(clock_time) + ", Control_c, 0, 64, 0\n"
                        note_on = 0
                    else:
                        if (i[0] == '\x9a') & (i[1:].isdigit()):
                            clock_time = clock_time + (step * int(i[1:]))
                        else:
                            # clock_time = clock_time + step #update the clock by a step
                            if i == '\x9a':
                                # a special case where the note is being played really fast
                                clock_time = clock_time + int(per_quater/10)
                            else:
                                # this is a note/notes currently being pressed
                                note_on = 1
                                for x in i:
                                    if ((x in held_on_notes) == 0) & ((ord(x)-33)>=0):
                                        # if the notes are not currently being held
                                        held_on_notes.append(x)
                                        output = output + str(track_num) + ", " + str(clock_time) + ", Note_on_c, 0, " + str(ord(x)-33) + ", 60\n"
                                for x in held_on_notes:
                                    # checking if one of the notes that previously being held onto is no longer found in the new set of notes
                                    if ((x in i) == 0):
                                        held_on_notes.remove(x)
                                        output = output + str(track_num) + ", " + str(clock_time) + ", Note_off_c, 0, " + str(ord(x)-33) + ", 0\n"

        output = output + str(track_num) + ", " + str(clock_time) + ", End_track\n"
        for track in range(1,track_total-track_num+1):
            output = output + str(track_num+track) + ", " + str(clock_time) + ", Start_track\n"  + str(track_num+track) + ", " + str(clock_time) + ", End_track\n" 
        output = output + "0, 0, End_of_file"
        data_file.close()

        # write a decompressed csv file
        rows = []
        for line in output.split("\n"):
            text_vec = line.replace('\r',"").split(", ")
            rows.append(text_vec)
        with open("./Generated/Decompressed/de" + self.file[:len(self.file) - 3] + "csv", 'w', newline = '') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the data by rows
            csvwriter.writerows(rows)

    def compress(self):
        print("compressing " + self.file + "...")
        data_file = codecs.open("./Dataset/CSVs/" + self.file,"r","utf-8") #read the file

        output = "" # final output
        held_on_notes = [] # notes which are currently held on
        pre_tmie_stamp = 0 # previous time
        division = 0 # number of clock ticks per quarter note
        add_note = 0 # check whenever a note is newly added
        started = 0 # when to start compressing

        for line in data_file:

            text_vec = line.split(",")
            time_stemp = int(text_vec[1]) # get current clock time
            notes = ""
            note = ""

            if "Note_on_c" in line:
                if started == 0:
                    # would start compressing only when the first note is being played
                    output = output + "START READING\n" # this is used for the decompressing process to let it know when to start
                    started = 1
                veloc = int(text_vec[5]) # get note velocity
                note = chr(33 + int(text_vec[4])) # get note
                if veloc == 0:
                    # the same as note_off
                    if note in held_on_notes:
                        held_on_notes.remove(note) # remove note
                        add_note = 0
                else:
                    if (note in held_on_notes) == 0:
                        held_on_notes.append(note) # add note
                        add_note = 1
            elif "Note_off_c" in line:
                note = chr(33 + int(text_vec[4]))
                if note in held_on_notes:
                    held_on_notes.remove(note) # remove note
                    add_note = 0
            if (started == 0):
                output = output + line # this is to preserve the midi custom settings
            if "Header" in line:
                division =  int(text_vec[5])
            if ("Note" in line):
                size = int(division/4)/8
                # for x in range(0,round((time_stemp-pre_tmie_stamp)/size)): # add spaces only when needed
                if ((round((time_stemp-pre_tmie_stamp)/size))>0):
                    # each space is 1/128 of a note
                    # we add the character 0xx9a before adding the number to indicate for the program that this is a time-length
                    # this is needed because some notes are represented as numbers
                    output = output + " " + '\x9a' + str(round((time_stemp-pre_tmie_stamp)/size)) + " "
                    # print all currently held notes ONLY when the clock time changed
                    for i in held_on_notes:
                        notes = notes + i
                    output = output + notes
                else:
                    # this is the case where the notes are being played together
                    if (time_stemp == pre_tmie_stamp):
                        if add_note == 1:
                            output = output + note
                    else:
                        # right here is a special condition where the notes are being played really fast (smaller than 1/128 of a note)
                        output = output + " " + '\x9a' + " "
                        for i in held_on_notes:
                            notes = notes + i
                        output = output + notes

            pre_tmie_stamp = time_stemp #update previous clock time
        data_file.close()

        # write a compressed txt file
        
        file = codecs.open("./Dataset/Compressed/compressed_" + self.file,"w","utf-8")
        file.write(output)
        file.close()

class run:
    def compress_all(self):
        for root, dirs, files in os.walk("./Dataset/CSVs/"):
            for filename in files:
                compresser(filename).compress()
    def decompress_all(self):
        for root, dirs, files in os.walk("./Dataset/Compressed/"):
            for filename in files:
                compresser(filename).decompress(0)
    def create_mid(self,file):
        loc = file.split("/")
        main_file = loc[len(loc)-1]
        if not os.path.isfile(file):
            raise Exception("MIDI ERROR: file not found!")
        compresser(file).decompress(1)
        if os.path.isdir("./midicsv-1.1/"):
            os.chdir("./midicsv-1.1/")
        else:
            raise Exception("MIDI ERROR: midicvs is missing, please download the program from the website into " + sys.path)
        os.system("./csvmidi ../Generated/Decompressed/de" + main_file[:len(main_file) - 3] + "csv ../Generated/Midis/" + main_file[:len(main_file) - 3] + "MID")
        os.chdir("../")

arguments = len(sys.argv)
coverter = run()
for i in range(0,arguments):
    if sys.argv[i] == "-c":
        coverter.compress_all()
    elif sys.argv[i] == "-d":
        coverter.decompress_all()
    elif sys.argv[i] == "-m":
        if (i+1 <= arguments) & (".txt" in (sys.argv[i+1])):
            coverter.create_mid(sys.argv[i+1])
