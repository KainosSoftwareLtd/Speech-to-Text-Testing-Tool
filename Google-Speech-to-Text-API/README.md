# Speech to text testing tool - Google Cloud Speech API using the REST API

This app uses Googles Speech to Text API for Python to transcribe audio files to text and calculate the word error rate of the transcription.

## Prerequisites

- A Google Cloud Platform account, with `Cloud Speech to Text API` enabled
- A service account key. See [Setting up authentication](https://cloud.google.com/docs/authentication/getting-started)
- Download service key account JSON and place it in this projects directory
- A [Node.js](https://nodejs.org) compatible device.
- Python 3 or later needs to be installed. Downloads are available [here](https://www.python.org/downloads/).

## Set up

- Update the following strings in the `settings.py` file with your configuration:

  - `PATH_TO_GOOGLE_CREDENTIALS_JSON`: path to service key account JSON
  - `HYP_PATH`: path to hyp.txt file. Transcribed text is generated and placed here
  - `REF_PATH`: path to ref.txt file. Enter original transcript here
  - `RESULTS_TABLE_PATH`: path to table.txt file. Transcription results generated and placed here
  - `ALL_TRANCRIPTIONS_PATH`: path to file that stores all transcriptions
  - `AUDIO_FORMAT`: format of audio file being transcribed
  - `HERTZ_RATE`: sample rate of audio file being transcribed
  - `LANGUAGE`: default language of audio file being transcribed

- For short audio samples (less than ~1 minute) place files in projects directory. I recommend creating a `sounds` folder and storing audio files there
- For longer audio samlpes (longer than 1 minute) upload files to a bucket on [Google Cloud Storage](https://console.cloud.google.com/home)
- See compatible audio formats [here](https://cloud.google.com/speech-to-text/docs/encoding). You can convert your audio formats [here](https://audio.online-convert.com/)
- Add the original transcript of the audio file you are transcribing to `ref.txt` file in the results folder. If you are using batch and transcribing multiple files, enter each transcript on a new line

- Install required dependencies including AWS CLI, execute the command

  ```sh
  npm run setup
  ```

  in a terminal.

## Run the app

To run the app, navigate to this projects main directory and execute

```sh
npm start
```

in a terminal

## Using the app

The app displays a menu. Choose a transcription type (single or batch). `Single` transcribes a single audio file. `Batch` transcribes multiple audio files in a folder and calculates averages of results.

- Single transcription

  - Enter path to where the audio file you want to transcribe is stored. Either local path or Google Cloud URI

- Batch transcription

  - Enter path to local folder that contains sound files you want to transcribe

## Further info

- [Word error rate (WER) explained](https://martin-thoma.com/word-error-rate-calculation/)

## References

- [Google Speech-to-Text how-to guide](https://cloud.google.com/speech-to-text/docs/how-to)
- For more information about WER. [See here](https://martin-thoma.com/word-error-rate-calculation/)
- [Google Cloud Speech API Python Samples](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/speech/cloud-client)
- [Cloud Speech-to-Text Client Libraries](https://cloud.google.com/speech-to-text/docs/reference/libraries#client-libraries-usage-python)
