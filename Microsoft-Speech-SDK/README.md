# Speech to text testing tool - Microsoft Speech SDK

This app uses Microsofts Speech SDK for Python to transcribe audio files to text and then calculate the word error rate of the transcription.

## Prerequisites

- A Microsoft Azure account
- A subscription key for the Speech services. See [Try the speech service for free](https://docs.microsoft.com/azure/cognitive-services/speech-service/get-started).
- A [Node.js](https://nodejs.org) compatible device.
- Python 3.5 or later needs to be installed. Downloads are available [here](https://www.python.org/downloads/).

## Set up

- Update the following variables, in `settings.py`:

  - `SPEECH_SUBSCRIPTION_KEY`: replace with your subscription key.
  - `SERVICE_REGION`: replace with the [region](https://aka.ms/csspeech/region) your subscription is associated with.
    For example, `westus` or `northeurope`.
  - `REF_PATH`: path to ref.txt file. Enter original transcript here
  - `HYP_PATH`: path to hyp.txt file. Transcribed text is generated and placed here
  - `RESULTS_TABLE_PATH`: path to table.txt file. Transcription results generated and placed here.

- Place audio samples in local directory. I recommend creating a `sounds` folder. Audio files are required in .wav (16000 Hz, Mono) format. You can convert your audio formats [here](https://audio.online-convert.com/)
- Add the original transcript of the audio file you are transcribing to `ref.txt` file in the results folder

- Install required dependencies including Azure speech SDK, execute the command

  ```sh
  npm run setup
  ```

  in a terminal.

## Run

To run the app, navigate to this projects directory.
Start the app with the command

```sh
npm start
```

The app displays a menu. Choose a transcription type. Then enter either filepath or folderpath, depending on which transcription type you selected.

# General errors

- _If no text is transcribed from audio, there may be a problem with the subscription key and/or service region given in `settings.py`_
- Audio file may have the incorrect sample rate or bits per sample if the error `Floating point exception: 8` is displayed

## Further info

- [Word error rate (WER) explained](https://martin-thoma.com/word-error-rate-calculation/)

## References

- [Quickstart article on the SDK documentation site](https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python)
- [Speech SDK API reference for Python](https://aka.ms/csspeech/pythonref)
- [Cognitive services speech SDK for python](https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/samples/python/console)
