# Speech to text testing tool - Amazon Transcribe

This app uses [Amazon Transcribe with AWS SDK for Python (Boto)](https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-python.html) to transcribe audio files to text and calculate the word error rate of the transcription.

## Prerequisites

- AWS account
- An AWS access key and AWS secret access key. See [Creating Your First IAM Admin User and Group](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html) for more info.

- To upload local files to S3 bucket, in your S3 bucket permissions you must allow

  - `Block public access to buckets and objects granted through new access control lists (ACLs)`
  - `Block public access to buckets and objects granted through any access control lists (ACLs)`.

- Homebrew installed
- A [Node.js](https://nodejs.org) compatible device.
- Python 3 or later needs to be installed. Downloads are available [here](https://www.python.org/downloads/).

## Set up

- Install required dependencies including AWS CLI, execute the command

  ```sh
  npm run setup
  ```

  in a terminal.

- Run `aws configure` in your shell, to set up AWS CLI. See [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). Default region should be the same as your S3 bucket and default output format should be JSON.

- Update the following strings in the `settings.py` file with your configuration:

  - `REF_PATH`: path to ref.txt file. Enter original transcript here
  - `HYP_PATH`: path to hyp.txt file. Transcribed text is generated and placed here
  - `RESULTS_TABLE_PATH`: path to table.txt file. Transcription results generated and placed here.

- Place audio samples in local directory. I recommend creating a `sounds` folder. Amazon Transcribe supports both 16 kHz and 8kHz audio streams, and multiple audio encodings, including WAV, MP3, MP4 and FLAC. See compatible audio formats [here](https://aws.amazon.com/transcribe/faqs/). You can convert your audio formats [here](https://audio.online-convert.com/)
- Add the original transcript of the audio file you are transcribing to `ref.txt` file in the results folder

## Run the app

To run the app, navigate to this projects main directory and execute

```sh
npm start
```

## Using the app

The app displays a menu. Choose a transcription type (single or batch). `Single` transcribes a single audio file. `Batch` transcribes multiple audio files in a folder.

- Single transcription

  - Select either `Local` or `S3 Bucket` depending on location of audio file
  - If `Local` selected, enter name of S3 bucket you want the file to be uploaded to, then enter path to local audio file
  - If `S3 Bucket` selected, enter path to a file in an S3 bucket
  - You can give your transcription a name to display on Amazon Transcribe. If left empty a unique ID will be generated as a name

- Batch transcription

  - Enter path to local folder that contains sound files you want to transcribe
  - Enter the name of the S3 bucket you want to upload audio files too (Amazon only transcribes files which are S3 buckets)

## Further info

- [Word error rate (WER) explained](https://martin-thoma.com/word-error-rate-calculation/)

## References

- [Amazon transcribe FAQ](https://aws.amazon.com/transcribe/faqs/)
- [Getting Started (AWS SDK for Python (Boto))](https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-python.html)
