from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator
from Naked.toolshed.shell import execute_js, muterun_js

from google.cloud import speech, storage
from google.cloud.speech import enums, types
from google.auth.exceptions import DefaultCredentialsError
from google.api_core.exceptions import NotFound, InvalidArgument

import os
import sys
import time
from datetime import datetime
import io
import argparse

import settings
import setENV

try:
    client = speech.SpeechClient()
except DefaultCredentialsError as e:
    print('Error: ' + str(e) + '\n\nIn settings.py, set PATH_TO_GOOGLE_CREDENTIALS_JSON variable to the path to the local json file that holds your Google credentials. Then execute python3 setENV.py\n')
    sys.exit(0)

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
        if startTranscription(file_path) != False:
            calcResult(file_path, 0)
    else:
        print('Error: Invalid transcription type')
        sys.exit(0)
        
def getTranscriptionType():
    questions = [
        {
            'type': 'list',
            'name': 'transcription_type',
            'message': 'Select transcription type:',
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
            'message': 'Enter path to audio file (local or Google cloud URI):',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    if len(answers) == 0:
        print('Error: Please enter path to audio file')
        sys.exit(0)
    
    file_path = answers['file_path']   
    
    if not file_path.startswith('gs://'):
        if (not(os.path.isfile(file_path))):
            print("Error: Cannot find file")
            sys.exit(0) 
    
    if file_path == '':
        print('Error: Please enter path to audio file')
        sys.exit(0)
    
    return file_path
    
def runBatchTranscription():
    try:
        folderpath = getFolderPath()
        path, dirs, files = next(os.walk(folderpath))
        files = sorted(files)
        refIndex = 0
        for aFile in files:
            if(aFile[0] != '.'):
                filepath = folderpath + aFile
                if startTranscription(filepath) != False:
                    calcResult(filepath, refIndex)
                refIndex = refIndex + 1
    except Exception as e:
        print('Error running sample: {}'.format(e))
        
def startTranscription(file_path):
    if checkVaildFileFormat(file_path) == False:
        filename, file_extension = os.path.splitext(file_path)
        print('\nError: ' + file_path + ' is an invalid file format ' + '(' + file_extension + ')\n')
        return False
        
    print("\nTranscribing job:", file_path)
    start = time.time()
    
    if file_path.startswith('gs://'):
        try:
            transcription = transcribe_gcs(file_path)
        except (NotFound) as e:
            print('\nError: ' + str(e) + '\n')
            sys.exit(0)
        except (InvalidArgument) as e:
            print('\nError: ' + str(e) + '\n')
            sys.exit(0)
    else:
        try:
            transcription = transcribe_file(file_path)
        except Exception as e:
            print('\nError: ' + str(e) + '\n')
            sys.exit(0)
    
    end = time.time()
    elapsed_time = end - start
    print("\nOperation time: %.2f" % elapsed_time, 'seconds')
    
    transcribed_filename = getAudioFilenameFromPath(file_path)
    writeTranscription(transcribed_filename, transcription)

def checkVaildFileFormat(filename):
    filename = getAudioFilenameFromPath(filename)
    return filename.lower().endswith(('.mp3', '.wav', '.flac', '.LINEAR16', '.MULAW', 'AMR', 'AMR_WB', 'OGG_OPUS', 'SPEEX_WITH_HEADER_BYTE'))

def getAudioFilenameFromPath(file_path):
    return os.path.basename(file_path)

def setUpConfig(encoding1, sample_rate_hertz1, language_code1):
    ## Uncomment to use enhanced model (phone_call, video)
    # model_type = "video"
    # use_enhanced = True
    config = types.RecognitionConfig(
        encoding=encoding1,
        sample_rate_hertz=sample_rate_hertz1,
        language_code=language_code1,
        # model=model_type,
        # use_enhanced=use_enhanced
        )
    return config

def transcribe_file(file_path):
    with io.open(file_path, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = setUpConfig(settings.AUDIO_FORMAT, settings.HERTZ_RATE, settings.LANGUAGE)

    response = client.recognize(config, audio)
    transcript = ''
    for result in response.results:
        transcript = result.alternatives[0].transcript
        
    return transcript

def transcribe_gcs(gcs_uri):
    audio = types.RecognitionAudio(uri=gcs_uri)
    config = setUpConfig(settings.AUDIO_FORMAT, settings.HERTZ_RATE, settings.LANGUAGE)

    try:
        # response = client.recognize(config, audio)
        operation = client.long_running_recognize(config, audio)
        response = operation.result(timeout=10000)
    except Exception as e:
        print('Error:', str(e))
        sys.exit(0)

    transcript = ''
    for result in response.results:
        transcript = result.alternatives[0].transcript
        
    return transcript

def writeTranscription(transcribed_filename, transcript):
    with open(settings.HYP_PATH, 'w') as out:
        out.write(transcript)
        
    with open(settings.ALL_TRANCRIPTIONS_PATH, 'a') as out:
        out.write(transcribed_filename + ' (' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ')' + ':\n' + transcript + '\n\n')

def calcResult(file_path, refIndex):
    transcribed_filename = getAudioFilenameFromPath(file_path)
    cliArgs = (transcribed_filename, settings.REF_PATH, settings.HYP_PATH, settings.RESULTS_TABLE_PATH, settings.RESULTS_CSV_PATH, str(refIndex))
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

if __name__ == '__main__':
    main()