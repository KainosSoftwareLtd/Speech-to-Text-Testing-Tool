from __future__ import print_function

import boto3
from botocore.client import ClientError
import botocore.errorfactory
import urllib.request

from PyInquirer import style_from_dict, Token, prompt, Separator
from Naked.toolshed.shell import execute_js, muterun_js

import settings

import os
import sys
import time
from datetime import datetime
import json
import uuid

transcribe = boto3.client('transcribe')
s3bucket = boto3.resource('s3')
s3 = boto3.client('s3')

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
        audio_location = getAudioFileLocation()
        runSingleTranscription(audio_location)
    else:
        print('Error: Invalid transcription type')
        sys.exit(0)
        
def runSingleTranscription(audio_location):
    if audio_location == 'local':
        job_path, job_name, job_file = getLocalJobDetails(audio_location)
        s3_bucket_name = getS3BucketName()
        uploadFilesToS3Bucket(job_path, s3_bucket_name, job_path)
        s3_name = getS3FilePath(s3_bucket_name, job_path)
    elif audio_location == 's3 bucket':
        s3_name, job_name = getS3JobDetails(audio_location)
        
    if startTranscriptionJob(job_name, s3_name) != False:
        calcResult(s3_name, 0)

def runBatchTranscription():
    folderpath = getFolderPath()
    s3name = getS3BucketName()
    path, dirs, files = next(os.walk(folderpath))
    files = sorted(files)
    ref_index = 0
    for aFile in files:
        if(aFile[0] != '.'):
            filepath = folderpath + aFile
            uploadFilesToS3Bucket(filepath, s3name, filepath)
            if (filepath[0] != '/'):    
                filepath = '/' + filepath
            s3path = 's3://' + s3name + filepath
            if startTranscriptionJob(aFile, s3path) != False:
                calcResult(s3path, ref_index)
            ref_index = ref_index + 1
        
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

def getAudioFileLocation():
    questions = [
        {
            'type': 'list',
            'name': 'audio_file_location',
            'message': 'Select audio file location',
            'choices': ['Local', 'S3 bucket'],
            'filter': lambda val: val.lower()
        },
    ]

    answers = prompt(questions, style=Qstyle)
    if len(answers) == 0:
        print('Error: Use arrow keys and preess enter to confirm')
        sys.exit(0)
        
    return answers['audio_file_location']

def getLocalJobDetails(audio_location):
    if audio_location == 'local':
        file_path = getFilepath()
        return file_path, getJobName(), getJobFile(file_path)
    else:
        print('Error: Invalid transcription type has been chosen')
        sys.exit(0)
        
def getS3JobDetails(audio_location):
    if audio_location == 's3 bucket':
        return getS3BucketFilePath(), getJobName()
    else:
        print('Error: Invalid transcription type has been chosen')
        sys.exit(0)

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

def getJobName():
    question = [
        {
            'type': 'input',
            'name': 'job_name',
            'message': 'Enter transcription job name (optional):',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    job_name = answers['job_name']  
    
    if job_name == '':
        job_name = str(uuid.uuid4())[0:10]  
    
    return job_name

def getJobFile(file_path):
    return os.path.basename(file_path)

def uploadFilesToS3Bucket(filepath, s3name, job_file):
    s3.upload_file(filepath, s3name, job_file)
    s3_path = 's3://' + s3name
    print('\n' + job_file + ' was successfully uploaded to ' + s3_path)

def getFolderPath():
    question = [
        {
            'type': 'input',
            'name': 'folder_path',
            'message': 'Enter path to local folder:',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    if len(answers) == 0:
        print('Error: Please enter path to local folder')
        sys.exit(0)
    
    folder_path = answers['folder_path']  
    
    if (not(os.path.isdir(folder_path))):
        print("Error: Cannot find folder")
        sys.exit(0)
    if (folder_path[0] == '/' or folder_path[0] == '.'):    
        folder_path = folder_path[1:]
        if (folder_path[0] == '/'):    
            folder_path = folder_path[1:]
    if (folder_path[len(folder_path)-1] != '/'):    
        folder_path = folder_path + '/'  
        
    if folder_path == '':
        print('Error: Please enter path to local folder')
        sys.exit(0)
    
    return folder_path

def getS3BucketName():
    question = [
        {
            'type': 'input',
            'name': 's3_bucket_path',
            'message': 'Enter S3 bucket name:',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    if len(answers) == 0:
        print('Error: Please enter path to S3 bucket')
        sys.exit(0)
    
    s3_bucket_path = answers['s3_bucket_path']    
        
    if s3_bucket_path == '':
        print('Error: Please enter path to S3 bucket')
        sys.exit(0)
        
    checkS3BucketExists(s3_bucket_path)
        
    return s3_bucket_path

def getS3BucketFilePath():
    question = [
        {
            'type': 'input',
            'name': 's3_bucket_file_path',
            'message': 'Enter path to S3 bucket file:',
            'default': ''
        },
    ]

    answers = prompt(question, style=Qstyle)
    
    if len(answers) == 0:
        print('Error: Please enter path to S3 bucket file')
        sys.exit(0)
    
    s3_bucket_file_path = answers['s3_bucket_file_path']    
        
    if s3_bucket_file_path == '':
        print('Error: Please enter path to S3 bucket file')
        sys.exit(0)
        
    return s3_bucket_file_path

def getS3FilePath(s3_bucket_path, job_file):
    if (job_file[0] != '/'):    
        job_file = '/' + job_file
    return 's3://' + s3_bucket_path + job_file
    
def checkS3BucketExists(s3_bucket_path):
    try:
        s3bucket.meta.client.head_bucket(Bucket=s3_bucket_path)
    except (ClientError) as e:
        print('\n' + e)
        sys.exit(0)
        
def checkVaildFileFormat(job_file):
    job_file = getJobFile(job_file)
    return job_file.lower().endswith(('.wav', '.mp3', '.mp4', '.flac'))

def checkAudioFormatMatches(job_file):
    job_file = getJobFile(job_file)
    return job_file.lower().endswith(('.wav', '.mp3', '.mp4', '.flac'))

def startTranscriptionJob(job_name, s3_name):
    if checkVaildFileFormat(s3_name) == False:
        filename, file_extension = os.path.splitext(s3_name)
        print('\nError: ' + filename + ' is an invalid file format ' + '(' + file_extension + ')' + '. Please use .wav, .mp3, mp4 or .flac\n')
        return False
    if checkAudioFormatMatches(s3_name) == False:
        print('\nError: ' + s3_name + ' file format does not match format specified in settings ' + '(' + settings.AUDIO_FORMAT + ')\n')
        return False
        
    print("\nTranscribing job:", job_name, "from", s3_name)
    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_name},
            MediaFormat=settings.AUDIO_FORMAT,
            LanguageCode=settings.LANGUAGE
        )
    except (transcribe.exceptions.ConflictException, transcribe.exceptions.BadRequestException) as e:
        print('\n',e)
        writeTranscriptionError(job_name, str(e))
        calcErrorResults(s3_name)
        return False
        
    processTranscriptionJob(job_name)


def processTranscriptionJob(job_name):
    start = time.time()
    s = '.'
    sys.stdout.write('transcribing')
    loading_len = 0
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break

        loading_len = loading_len + 1
        if loading_len % 4 != 0:
            sys.stdout.write( s )
            sys.stdout.flush()
            time.sleep(0.5)
        else:
            sys.stdout.write("\b" * 3 + " " * 3 + "\b" * 3)

    end = time.time()
    elapsed_time = end - start
    print("\nOperation time: %.2f" % elapsed_time, 'seconds')
    readTranscriptionResponse(status)

def readTranscriptionResponse(status):
    transcriptFileUri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']

    response = urllib.request.urlopen(transcriptFileUri)
    bJSON = response.read()
    resultsJSON = bJSON.decode('UTF-8')
    results = json.loads(resultsJSON)

    print("Status:", results['status'])

    transcript = results['results']['transcripts'][0]['transcript']
    writeTranscription(results['jobName'], transcript)

def writeTranscription(jobName, transcript):
    with open(settings.HYP_PATH, 'w') as out:
        out.write(transcript)
        
    with open(settings.ALL_TRANCRIPTIONS_PATH, 'a') as out:
        out.write(jobName + ' (' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ')' + ':\n' + transcript + '\n\n')

def writeTranscriptionError(jobName, errordescription):
    with open(settings.HYP_PATH, 'w') as out:
        out.write(errordescription)
        
    with open(settings.ALL_TRANCRIPTIONS_PATH, 'a') as out:
        out.write(jobName + ' (' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ')' + ':\n' + errordescription + '\n\n')

def calcResult(job_uri, ref_index):
    transcribed_filename = os.path.basename(job_uri)
    cliArgs = (transcribed_filename, settings.REF_PATH, settings.HYP_PATH, settings.RESULTS_TABLE_PATH, settings.RESULTS_CSV_PATH, str(ref_index))
    args = ' '.join(cliArgs)
    runjs = muterun_js('js/index.js', arguments=args)

    if runjs.exitcode == 0:
      response = str(runjs.stdout)
      responseByLine = response[2:len(response)-1].split('\\n')
      for s in responseByLine:
        print(s)
    else:
      sys.stderr.write(runjs.stderr)

def calcErrorResults(job_uri):
    transcribed_filename = os.path.basename(job_uri)
    cliArgs = (transcribed_filename, 'err', settings.RESULTS_TABLE_PATH, settings.RESULTS_CSV_PATH)
    args = ' '.join(cliArgs)
    runjs = muterun_js('js/index.js', arguments=args)
    
    if runjs.exitcode == 0:
      response = str(runjs.stdout)
      responseByLine = response[2:len(response)-1].split('\\n')
      for s in responseByLine:
        print(s)
    else:
      sys.stderr.write(runjs.stderr)
    
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