#accessing python from terminal: C:/Users/Wayne/AppData/Local/Programs/Python/Python37/python.exe

#saving image info in text files

#purpose is to import negative images names into a text file

#for positive image txt file, its a bit different, not only image name is needed, it needs the # of object, and rectangular coordinates
#use opencv annotation.exe for that. to access the exe file:  C:\Users\Wayne\.vscode\Runescape\opencv\opencv\build\x64\vc15\bin\opencv_annotation.exe --annotations=pos.txt --images=positive/
#make sure it can find the image files, best to run above code in bash in the directory where the image folder lies

#for positive folders, once the data collection is done. go to the dir where pos.txt is, and type this in powershell: C:\Users\Wayne\.vscode\Runescape\opencv\opencv\build\x64\vc15\bin\opencv_createsamples.exe -info pos.txt -w 24 -h 24 -num 1000 -vec pos.vec   
#the width and height values = 24 is set to detect only images >= 24
#larger w h values will improve detection but training takes longer
#"num 1000" - number of vectors, this needs to just be some number larger than total # of rectangles i drew, so it will include all the rectangles
#-vec pos.vec -> this is where to save output, the file is call pos.vec (binary file), itll just be in the same folder as a pos.txt since the directory is already there.

import os

#run this in terminal. because it wont run by itself when click run due to being a function
def generate_negative_description_file():
    with open('neg.txt', 'w') as f: #with block ensures file will be closed after execution
        for filename in os.listdir('negative'):
            f.write('negative/' + filename + '\n')


#training the model
#in the folder where we want to save the training data (prefer same location as the vector file), type C:\Users\Wayne\.vscode\Runescape\opencv\opencv\build\x64\vc15\bin\opencv_traincascade.exe -data cascade/ -vec pos.vec -bg neg.txt -w 24 -h 24 -precalcValBufSize 3000 -precalcIdxBufSize 3000 -numPos 500 -numNeg 250 -numStages 20 -maxFalseAlarmRate 0.3 -minHitRate 0.999
#"cascade" is the folder for creation. -vec is argument for positive vector, -bg is background, argument for negative text file
#numPos needs to be less than the num of rectangles in pos txt file or else there will ben an error. Can play around
#numNeg doesnt matter, generally half the numPos or 2x. can play around
#numStages - training stages, 10 is a good starting number for 200 samples
#bufSize - for example, 5000 = 5g of ram dedicated to training model. its a value that can slow or speed up training
#false alarm rate - keep adding layers N until the false alarm rate is below the set value
#hit rate - keep adding layer until hit rate is above the set value

#in the model: HR = hit rate, FA = false alarm, N = layer, higher the N, higher the detail. we want the highest N to have the lowest FA 
# HR and FA stand for hit rate and false alarm. Conceptually: hitRate = % of positive samples that are classified correctly as such. falseAlarm = % of negative samples incorrectly classified as positive.

#running python file in python terminal - C:/Users/Wayne/AppData/Local/Programs/Python/Python37/python.exe

#keep track of your parameters
#if training stop for whatever reason, can continue by entering same parameter. 
#can also enter fewer/more numStages to test how each stages improve. it will override the cascade xml file  
#C:\Users\Wayne\.vscode\Runescape\opencv\opencv\build\x64\vc15\bin\opencv_traincascade.exe -data cascade/ -vec pos.vec -bg neg.txt -w 24 -h 24 -numPos 700 -numNeg 700 -numStages 23 -maxFalseAlarmRate 0.15 -minHitRate 0.995


'''
dir = os.path.dirname(os.path.abspath(__file__))
negative_path = os.path.join(dir, 'negative')

negative_text_file = os.path.join(dir, "negative.txt")

f = open(negative_text_file, "a")
for negative_files in os.listdir(negative_path):
    f.write(negative_files)
f.close()
'''