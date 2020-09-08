print("\nloading modules, please wait...\n")

from keras.layers import Dropout, LSTM, Dense
from keras import Sequential
from keras.models import save_model, load_model
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping

import numpy as np
import os, sys, time, random, Convert, codecs

batch_size = 60
epoch_size = 5
length = 60

chars = [] # an array of all unique characters, which includes 120 different piano keys
for i in range(0,120):
    chars.append(chr(i+33))
chars.append(" ")
chars.append('\x9a') # a special case of a note being played faster than 1/128 of a note

print("Getting text files from ./Dataset/Converted/ ...\n")

data = [] # here we will store all the text files data

for root, folder, files in os.walk('./Dataset/Converted/'):
    for filename in files:
        if '.txt' in filename:
            data.append(filename)
                    
def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    # this was taken from the official TensorFlow team
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

class RNN():
    
    def __init__(self, model = None):
        
        print("Setting up model...\n")
        
        if model == None:
        
            # setting up a sequential model
            self.model = Sequential()
            
            # setting up a long-short-term-memory cell, with an input size of the substring and the unique characters
            # the LSTM cell will be connected to a 32 dense layer
            self.model.add(LSTM(32, return_sequences=False, input_shape = (length,len(chars))))
            
            # here we set up a drop out cell of 10%, this is used to make sure that we won't be overfitting the model in the long run 
            self.model.add(Dropout(0.1))
            
            self.model.add(Dense(512))
            # self.model.add(Dropout(0.3))
            
            # this is the final layer, it is the size of the unique characters
            # it will spill out a probability of what the next character should be,
            # we used a softmax activation function to normalize the vector between [-1,1]
            self.model.add(Dense(len(chars), activation = 'softmax'))
            
            # we are going to use Adam optimizer on the model, with a learning rate of 0.01
            optimizer = Adam(learning_rate=0.01)
            self.model.compile(loss='categorical_crossentropy', optimizer=optimizer)
            
        else:
            # in the case a user want to load up a previous model
            print("Loading model...\n")
            self.model = load_model(model)
            print("\nModel loaded!\n")
        
        self.model.summary()
        
        
    def train(self):

        print("\nSetting up the data...\n")
        
        # we first going to shuffle the files
        random.shuffle(data)
        
        # the model name will be always unique as we attach the time into it
        # each model is named based on the substring length, batch size, and epoch size
        # this is used for setting up the program later when loading the model
        NAME = "Model_" + str(int(time.time())) + "x" + str(length) + "x" + str(batch_size) + "x" + str(epoch_size) + ".h5"
        
        # while we could specify the epoch size when compiling the model,
        # it was necessary to use a for loop on each file. That is because if ...
        # each data from the file was extracted and was appended to the array, we could run 
        # out of memory space. A for loop also allows you to speed up the runtime of the program as ...
        # we can clear the previous extracted data from the memory.
        for eps in range(epoch_size):
            for filename in data:
                
                subtext = []
                target = []
                
                print("\nExtracting text from " + filename + "...\n")
                
                data_file = codecs.open("./Dataset/Converted/" + filename ,"r","utf-8")
                
                lines = ""
                # this variable is used in order to indicate that we at the line of the compressed data
                start_reading = 0
                
                for line in data_file:
                    if ("START READING" in line):
                        start_reading = 1
                    elif (start_reading==1):
                        lines = lines + line
                
                # we going to break the text into a substrings
                # the target character which the model is going to try to predict ...
                # would be the next character after the substring
                
                for i in range(0, len(lines) - length, 1):
                    subtext.append(lines[i: i + length])
                    target.append(lines[i + length])
                
                # LSTM cell requires a 3D matrix as an input shape
                x = np.zeros((len(subtext), length, len(chars)), dtype=np.bool)
                y = np.zeros((len(subtext), len(chars)), dtype=np.bool)
                for i, text in enumerate(subtext):
                    for t, char in enumerate(text):
                        if char in chars:
                            x[i, t, chars.index(char)] = 1
                    if target[i] in chars:
                        y[i, chars.index(target[i])] = 1
                
                # TensorBoard callback is used to visuals the process of our model training,
                # we can use this to better understand and debug our model
                tb_callback = TensorBoard(log_dir='logs/'+NAME[:len(NAME) - 3])
                
                # checkpoint call back is used for backup
                cp_callback = ModelCheckpoint(filepath='./Models/CP_'+NAME, monitor='loss',save_best_only=True,save_weights_only=False, mode='auto', save_freq='epoch')
                
                # for better optimization, its worth to consider stoping the model early if it's not improving at all
                es_callback = EarlyStopping(monitor='loss', min_delta=0, patience=3, verbose=0, mode='auto')
                
                self.model.fit(x,y,epochs=1,batch_size = batch_size, callbacks = [cp_callback,tb_callback,es_callback])
                save_model(self.model, './Models/' + NAME)
        
    def generate(self, size, diversity):
    
        print("\nGenerating music...\n")
        
        # this is a general text that will be added at the start of the text file
        # the trained model would generate a compressed text of the music data ...
        # but not the arbitrary information such as the title or music instrument type
        
        generated = "0, 0, Header, 1, 2, 480\n"
        generated = generated + "1, 0, Start_track\n"
        generated = generated + "1, 0, Title_t, Generated Music\n"
        generated = generated + "1, 0, Text_t, Sample for MIDIcsv Distribution\n"
        generated = generated + "1, 0, Copyright_t, This file is in the public domain\n"
        generated = generated + "1, 0, Time_signature, 4, 2, 24, 8\n"
        generated = generated + "1, 0, Tempo, 500000\n"
        generated = generated + "1, 0, Instrument_name_t, A-01\n"
        generated = generated + "1, 0, End_track\n"
        generated = generated + "2, 0, Start_track\n"
        generated = generated + "START READING\n"
        
        '''sentence = ''
        for i in range(length-1):
            sentence = sentence + " "
        sentence = sentence + random.choice(chars)'''
        
        # here we shuffling a data and picking a random text file as our starting point
        random.shuffle(data)
        filename = data[0]
        
        data_file = codecs.open("./Dataset/Converted/" + filename,"r","utf-8")
            
        lines = ""
        start_reading = 0
        
        for line in data_file:
            if ("START READING" in line):
                start_reading = 1
            elif (start_reading==1):
                lines = lines + line
        
        # we going to choose a random index from the text file as the starting point of a substring
        rnd_index = random.randint(0, len(lines) - length - 1)
        sentence = lines[rnd_index: rnd_index + length]
        generated += sentence
        
        for i in range(size):
                # creating a prediction matrix
                x_pred = np.zeros((1, length, len(chars)))
                
                # set up the prediction matrix based on the random substring that we got
                for t, char in enumerate(sentence):
                    x_pred[0, t, chars.index(char)] = 1
                
                # let the model predict a vector of unique characters
                preds = self.model.predict(x_pred, verbose=0)[0]
                
                # sample the next character
                next_index = sample(preds, diversity)
                next_char = chars[next_index]
                
                # add the predicted character to the string and shift the input substring by one ...
                # while including the next predicted character
                generated += next_char
                sentence = sentence[1:] + next_char
        
        file = codecs.open("./Generated/Text/generatedx" + str(size) + "x" + str(diversity) + ".txt","w","utf-8")
        file.write(generated)
        file.close()
        
        # we going to automatically generate a midi file using our decompressor program
        Convert.run().create_mid("./Generated/Text/generatedx" + str(size) + "x" + str(diversity)+ ".txt")
        
        print("\nGenerated midi file can be found at " + "/Generated/Midis/decomprssed_generatedx" + str(size) + "x" + str(diversity) + ".MID \n")
    
arguments = len(sys.argv)
setup = 0

for i in range(0,arguments):
    if sys.argv[i] == "-l":
        # the user is loading a model
        if i+1 <= arguments:
            if os.path.isfile(sys.argv[i+1]):
                # right here we set up the model training and input values
                # based on the name of the model
                values = sys.argv[i+1].split("x")
                length = int(values[1])
                batch_size = int(values[2])
                epoch_size = int(values[3][:len(values[3]) - 3])
                setup = RNN(sys.argv[i+1])
            else:
                raise Exception("LOADING ERROR: file not found!")
        else:
            raise Exception("LOADING ERROR: File location missing!")
    elif sys.argv[i] == "-g":
        # the user is generating a text
        if (i+1 <= arguments) & (sys.argv[i+1]).isdigit():
            size = int(sys.argv[i+1])
        else:
            raise Exception("GENERATE ERROR: Something is wrong with size argument")
        if (i+2 <= arguments):
            try:
                diversity = float(sys.argv[i+2])
            except ValueError:
                raise Exception("GENERATE ERROR: diversity argument is not a float value")
        else:
            raise Exception("GENERATE ERROR: Something is wrong with diversity argument")
        if setup == 0:
            raise Exception("GENERATE ERROR: Model is missing, please train a new model or load a saved one")
        else:
            setup.generate(size,diversity)
    elif sys.argv[i] == "-t":
        # the user is training a model if there is no loaded model ...
        # the program would use the default RNN-model
        if (i+1 <= arguments) & (sys.argv[i+1]).isdigit():
            length = int(sys.argv[i+1])
        else:
            raise Exception("TRAINING ERROR: Something is wrong with length argument")
        if (i+2 <= arguments) & (sys.argv[i+2]).isdigit():
            batch_size = int(sys.argv[i+2])
        else:
            raise Exception("TRAINING ERROR: Something is wrong with batch argument")
        if (i+3 <= arguments) & (sys.argv[i+3]).isdigit():
            epoch_size = int(sys.argv[i+3])
        else:
            raise Exception("TRAINING ERROR: Something is wrong with epoch argument")
        if setup == 0:
            setup = RNN()
        setup.train()
            