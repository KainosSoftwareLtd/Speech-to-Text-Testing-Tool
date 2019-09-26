from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator
from Naked.toolshed.shell import execute_js, muterun_js

import settings
import speech

from collections import OrderedDict
import platform

import os
import sys
import time
from datetime import datetime

Qstyle = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

def main():    
    transcription_type = getTranscriptionType()
    if transcription_type == 'batch' :
        runBatchTranscription()
        calcAverage()
        printResultsTable()
    elif transcription_type == 'single':
        file_path = getFilepath()
        if startTranscriptionJob(file_path) != False:
            calcResult(file_path, 0)
    else:
        print('Error: Invalid transcription type')
        sys.exit(0)
    
def getTranscriptionType():
    questions = [
        {
            'type': 'list',
            'name': 'transcription_type',
            'message': 'Select transcription type',
            'choices': ['Single', 'Batch'],
            'filter': lambda val: val.lower()
        },
    ]

    answers = prompt(questions, style=Qstyle)
    if len(answers) == 0:
        print('Error: Use arrow keys and preess enter to confirm')
        sys.exit(0)
    
    return answers['transcription_type']

def getFolderPath():
    question = [
        {
            'type': 'input',
            'name': 'folder_path',
            'message': 'Enter path to folder:',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    if len(answers) == 0:
        print('Error: Please enter path to audio files folder')
        sys.exit(0)
        
    folder_path = answers['folder_path']
    
    if (not(os.path.isdir(folder_path))):
        print("Error: Cannot find folder")
        sys.exit(0)
        
    if folder_path == '':
        print('Error: Please enter path to folder containing audio files')
        sys.exit(0)
    
    if (folder_path[0] == '/' or folder_path[0] == '.'):    
        folder_path = folder_path[1:]
        if (folder_path[0] == '/'):    
            folder_path = folder_path[1:]
    if (folder_path[len(folder_path)-1] != '/'):    
        folder_path = folder_path + '/'
    
    return folder_path

def getFilepath():
    question = [
        {
            'type': 'input',
            'name': 'file_path',
            'message': 'Enter path to audio file:',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    if len(answers) == 0:
        print('Error: Please enter path to audio file')
        sys.exit(0)
    
    file_path = answers['file_path']    
    
    if (not(os.path.isfile(file_path))):
        print("Error: Cannot find file")
        sys.exit(0)
        
    if file_path == '':
        print('Error: Please enter path to audio file')
        sys.exit(0)
    
    return file_path

def isWavFile(filename):
    return filename.lower().endswith(('.wav'))
    
def runBatchTranscription():
    try:
        folderpath = getFolderPath()
        path, dirs, files = next(os.walk(folderpath))
        files = sorted(files)
        ref_index = 0
        for aFile in files:
            if(aFile[0] != '.'):
                filepath = folderpath + aFile
                if startTranscriptionJob(filepath) != False:
                    calcResult(filepath, ref_index)
                ref_index = ref_index + 1
    except Exception as e:
        print('Error running sample: {}'.format(e))
    
def startTranscriptionJob(file_path):
    if isWavFile(file_path) == False:
        filename, file_extension = os.path.splitext(file_path)
        print('\nError: ' + file_path + ' is an invalid file format ' + '(' + file_extension + ')' + '. Please use .wav\n')
        return False
        
    print("\nTranscribing job:", file_path)
    start = time.time()
    
    transcription = speech.speech_recognize_continuous_from_file(file_path)
    
    end = time.time()
    elapsed_time = end - start
    print("\nOperation time: %.2f" % elapsed_time, 'seconds')
    transcribed_filename = os.path.basename(file_path)
    writeTranscription(transcribed_filename, transcription)
    
def writeTranscription(transcribed_filename, transcript):
    with open(settings.HYP_PATH, 'w') as out:
        out.write(transcript)
        
    with open(settings.ALL_TRANCRIPTIONS_PATH, 'a') as out:
        out.write(transcribed_filename + ' (' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ')' + ':\n' + transcript + '\n\n')

def calcResult(file_path, ref_index):
    transcribed_filename = os.path.basename(file_path)
    cliArgs = (transcribed_filename, settings.REF_PATH, settings.HYP_PATH, settings.RESULTS_TABLE_PATH, settings.RESULTS_CSV_PATH, str(ref_index))
    args = ' '.join(cliArgs)
    runjs = muterun_js('js/index.js', arguments=args)

    if runjs.exitcode == 0:
      response = str(runjs.stdout)
      responseByLine = response[2:len(response)-1].split('\\n')
      for s in responseByLine:
        print(s)
    else:
      sys.stderr.write(str(runjs.stderr))
      
def calcAverage():
    cliArgs = (settings.RESULTS_CSV_PATH, settings.RESULTS_TABLE_PATH)
    args = ' '.join(cliArgs)
    runjs = muterun_js('js/avg.js', arguments=args)
    
    if runjs.exitcode == 0:
      response = str(runjs.stdout)
      responseByLine = response[2:len(response)-1].split('\\n')
      for s in responseByLine:
        print(s)
    else:
      sys.stderr.write(str(runjs.stderr))
      
def printResultsTable():
    with open(settings.RESULTS_TABLE_PATH) as out:
        print(out.read() + '\n\n')

if __name__ == "__main__":
    main()