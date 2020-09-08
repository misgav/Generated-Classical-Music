1. DESCRIPTION

This is the first version of the project, the main objective is to learn to generate music based on midi files. In order to run this project you need to have installed the following:

1. Python 3.x		https://www.python.org/downloads/
2. Tensorflow 2.0	https://www.tensorflow.org/install
3. midicvs 1.1		https://www.fourmilab.ch/webtools/midicsv/


*** Its a requirment to have midicsv installed on your computer for this project to work. For simplicity, download midicsv into
this repository directory. If you want to train a new model based on new midi files, you can download them into ./Dataset/Midis
and rename all of them numerically (you can just select all of them and rename one of them). If you are in windows you can navigate the midicsv directory and use the following code in the command line to generate the necessary CSVs files:

FOR /l %G in (1,1,<number of files>) DO midicsv ../Dataset/Midis/<filename> (%G).MID ../Dataset/CSVs/<file name> (%G).txt

*** its importent to emphesis that the generated CSVs file should be .txt file and not .csv


2. DIRECTORY DESCRIPTION 

./Dataset - contains all the data which models would be trained on
./Dataset/Midis - this directory is used to store all the midis you want the model to learn from
./Dataset/CSVs - this directory should be used when using midicsv as the output location
./Dataset/Compressed - in this directory Convert.py would generate the compressed files from CSVs folder

./Generated - this directory is used to hold all the generated music from your trained model
./Generated/Decompressed - in this directory Convert.py would generate the decompressed files from the Text folder

./Models - this is a directory to hold all your trained models


3. MANUAL

NAME

Convert.py

SYNOPSIS

Convert.py [-c -d]
Convert.py -m [compressed file location]

DESCRIPTION

this program is used to compress midicsv generated text file so the model can learn from

OPTIONS

-c	the program would compress all the text files in ./Dataset/CSVs and upload them to ./Dataset/Compressed

-d	the program would decompress all the text files from ./Dataset/Compressed and upload them to ./Generated/Decompressed

-m	would generate a midi file into ./Generated/Midis/


NAME

RNN.py

SYNOPSIS

RNN.py -l [h5 model file location]
RNN.py -g [string length][diversity]
RNN.py -t [substring length][batch size][epochs size]

DESCRIPTION

This program is responsible for training new neural-networks models and generating new music

OPTIONS

-t	The program would train a new RNN model, unless a model was loaded beforehand then it would continue to train that model.
	The model would be loaded into ./Models/ as well as its backup checkpoint starting with "CP_"
	Training any model would generate a log directory found at ./logs/, you can use TensorBoard to view the model progress.

-g	The program would generate a midi file based on string length and diversity, the file would be found at ./Generated/Midis
	It is a requirement that you either trained or loaded a model previously

-l	Would load a previouslytrained model


4. KNOWN BUGS

Sometimes when using midicsv to generate the text file, the text would contain (usually in the title name) a
character that cannot be decoded by UTF-8. Simply remove the character so Covert.py can be run without errors

5. CREDITS

The following is the websites which I download the necessary midi files to train Model_1:

https://www.free-scores.com/
https://yamahaden.com/midi-files/category/claude_debussy
https://www.8notes.com/

The following is a website which I download the necessary midi files to train Model_2:

http://www.jsbach.net/midi/