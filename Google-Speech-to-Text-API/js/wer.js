const speechScorer = require('word-error-rate')
const fs = require('fs')
const removePunctuation = require('remove-punctuation')
const numWords = require('num-words')
const contractions = require('contractions')
const csvWriter = require('csv-write-stream')

function convertNumbersToText(formatStr) {
  const nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
  for (let i = 0; i < formatStr.length; i++) {
    if (nums.includes(formatStr.charAt(i))) {
      let currentNum = ''
      if (formatStr.charAt(i) === '0') {
        currentNum += formatStr.charAt(i)
        formatStr = formatStr.slice(0, i) + formatStr.slice(i + 1)
      } else {
        while (nums.includes(formatStr.charAt(i))) {
          currentNum += formatStr.charAt(i)
          formatStr = formatStr.slice(0, i) + formatStr.slice(i + 1)
        }
      }
      const wordStart = formatStr.slice(0, i)
      const wordEnd = formatStr.slice(i)

      if (currentNum === '0') formatStr = wordStart + 'zero ' + wordEnd
      else formatStr = wordStart + numWords(currentNum) + wordEnd
    }
  }
  return formatStr
}

module.exports = {
  readRef: function readRef(path) {
    return fs.readFileSync(path, 'utf-8')
  },
  readHyp: function readHyp(path) {
    return fs.readFileSync(path, 'utf-8')
  },
  cleanTranscript: function cleanTranscript(transcript) {
    let formatStr = contractions.expand(transcript)
    formatStr = removePunctuation(formatStr)
    formatStr = formatStr.toLowerCase()
    formatStr = formatStr.replace(/\s+/g, ' ').trim()
    formatStr = convertNumbersToText(formatStr)
    return formatStr
  },
  writeTranscription: function writeTranscription(transcription, fileName) {
    fs.appendFileSync(`./results/${fileName}.txt`, transcription, err => {
      if (err) {
        console.log(err.message)
        return
      }
    })
  },
  addToResultsTable: function addToResultsTable(
    wer,
    wordErrorRate,
    filename,
    resultsTablePath
  ) {
    const whitespace1 = new Array(59 - filename.toString().length).join(' ')
    const whitespace2 = new Array(24 - wer.toString().length).join(' ')
    const whitespace3 = new Array(7 - wordErrorRate.toString().length).join(' ')
    const newResult =
      '\n| ' +
      filename +
      whitespace1 +
      ' |  ' +
      wer +
      whitespace2 +
      ' |      ' +
      wordErrorRate +
      whitespace3 +
      ' |\n+------------------------------------------------------------+--------------------------+-------------+'
    fs.appendFileSync(resultsTablePath, newResult)
  },
  addToResultsCSV: function addToResultsCSV(
    filename,
    ref,
    hyp,
    wer,
    wordsWithErrors,
    resultsCSVPath
  ) {
    let writer = csvWriter()
    if (!fs.existsSync(resultsCSVPath))
      writer = csvWriter({
        headers: [
          'File',
          'Original_transcript',
          'Transcribed_text',
          'WER',
          'Total_word_errors'
        ]
      })
    else writer = csvWriter({ sendHeaders: false })

    writer.pipe(fs.createWriteStream(resultsCSVPath, { flags: 'a' }))
    writer.write({
      File: filename,
      Original_transcript: ref,
      Transcribed_text: hyp,
      WER: wer,
      Total_word_errors: wordsWithErrors
    })
    writer.end()
  },
  calculate: function calculate(
    ref,
    hyp,
    filename,
    resultsTablePath,
    resultsCSVPath
  ) {
    const formattedRef = module.exports.cleanTranscript(ref)
    const formattedHyp = module.exports.cleanTranscript(hyp)
    const wer = speechScorer.wordErrorRate(formattedRef, formattedHyp)
    console.log('\nWord Error Rate =', wer)
    const wordsWithErrors = speechScorer.calculateEditDistance(
      formattedRef,
      formattedHyp
    )
    console.log('Number of word errors =', wordsWithErrors)
    module.exports.addToResultsTable(
      wer,
      wordsWithErrors,
      filename,
      resultsTablePath
    )
    module.exports.addToResultsCSV(
      filename,
      ref,
      hyp,
      wer,
      wordsWithErrors,
      resultsCSVPath
    )
  },
  calculateError: function calculateError(filename) {
    console.log('Error was detected so results were not calculated')
    module.exports.addToResultsTable('-', '-', filename)
  }
}
