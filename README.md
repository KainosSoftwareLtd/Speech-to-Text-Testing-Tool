# Speech to Text Testing Tool

This app transcribes and tests audio files with Microsoft, Amazon & Google's speech to text services, to help compare accuracy and performance.

## Getting started

Select your service by navigating to the appropriate folder

```
cd Amazon-Transcribe
```

```
cd Google-Speech-to-Text-API
```

```
cd Microsoft-Speech-SDK
```

Each service has its own README containing set up and usage instructions, found in their specific directory.

#### File structure

_Make sure the path to these files are correct in `settings.py` before running_

- In each service's directory, there is a `results` folder and contains the following files:
  - `ref.txt`: stores the original transcript of the audio file you want to transcribe. Enter the original transcript before running the app
  - `hyp.txt`: result of the transcription is stored here once the app is run and transcription is generated
  - `results.csv`: results are stored here once generated (transcripts, WER & word error count)
  - `table.txt`: WER and the word error count results are stored here
  - `alltranscriptions.txt`: all text that has been transcribed is stored here

#### Testing structure

This app measures the accuracy of transcriptions using [word error rate (WER)](https://martin-thoma.com/word-error-rate-calculation/).

> Word Error Rate (WER), is a method to measure the performance of automated speech recognition (ASR). It compares the original transcript (reference) with the transcribed text (hypothesis) from a speech-to-text service.

WER does have its [pros and cons](https://medium.com/descript/challenges-in-measuring-automatic-transcription-accuracy-f322bf5994f) but overall it provides a baseline accuracy metric for general use, in the form of a percentage.

## Usage

Each app supports single and batch processing. With batch, an average of results are automatically calculated

1. Select your service by navigating to the appropriate folder. You can find README's with specific information there
2. Make sure to have understood and completed the prerequisites
3. Gather audio samples. I recommend creating a `sounds` folder and placing audio files there
4. Install all required dependencies by executing

```sh
npm run setup
```

5. Run each app by executing

```sh
npm start
```

6. Analyse results (table.txt & results.csv)

> _Further info can be found in each app's README's_

## General Info

- To use each tool, you will require an account with your service of choice. Each of the services are paid but all offer a free trial period
- For each service, audio files are required to be in a specific format. Details of this can be found in each projects README
- Both the original transcript (ref.txt) and the transcribed text (hyp.txt) are 'cleaned' to have consistent stylistic formats before WER is calculated. For example, digits like 1, 64 and 3000 are converted to their corresponding words: one, sixty-four and three thousand, respectively. Punctuation and unnecessary whitespace is also removed
- You may have to change stylistic differences like "street" and "st" yourself to be consistent with transcription service

* Find out more about this project and our findings in our [blog](https://medium.com/kainos-applied-innovation)

## Acknowledgments

- **Applied Innovation** - [Kainos](https://www.kainos.com/)

## Disclaimer

This project was developed using:

- python 3.7.4, python modules version as described in `requirements.txt` 
- Node js v10.16.0, npm packages as described in `package.json`

Software versions are subject to change with new releases, to ensure the project runs smoothly without alteration the above versions should be used. This software was last ran on 09/2019
