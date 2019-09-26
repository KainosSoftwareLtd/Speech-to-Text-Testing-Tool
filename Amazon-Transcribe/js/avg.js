const fs = require('fs')
const csv = require('csvtojson')
const csvWriter = require('csv-write-stream')

let totalWER = 0
let totalWordErrors = 0
let lineCount = 1

if (!fs.existsSync(process.argv[2])) {
  console.log('Error: Can not find path to results table')
  process.exit(0)
}

const csvPath = process.argv[2]
const tablePath = process.argv[3]

csv()
  .fromFile(csvPath)
  .then(jsonObj => {
    jsonObj.map(obj => {
      if (Number(obj['WER']) && Number(obj['Total_word_errors'])) {
        totalWER += Number(obj['WER'])
        totalWordErrors += Number(obj['Total_word_errors'])
        lineCount++
      }
    })
  })
  .then(() => {
    const avgWER = calcAvgWER(totalWER)
    const avgWordErrorRate = calcAvgWordErrors(totalWordErrors).toFixed(2)

    if (isNaN(avgWER))
      console.log('Error: cannot calculate average word error rate')

    if (isNaN(avgWordErrorRate))
      console.log('Error: cannot calculate average word rate')

    if (!isNaN(avgWER) || !isNaN(avgWordErrorRate))
      addAverageToResults(avgWER, avgWordErrorRate, tablePath)

    let writer = csvWriter({ sendHeaders: false })
    writer.pipe(fs.createWriteStream(csvPath, { flags: 'a' }))
    writer.write({
      File: 'Average',
      Original_transcript: '',
      Transcribed_text: '',
      WER: avgWER,
      Total_word_errors: avgWordErrorRate
    })
    writer.end()
  })

function calcAvgWER(totalWER) {
  return totalWER / lineCount
}

function calcAvgWordErrors(totalWordErrors) {
  return totalWordErrors / lineCount
}

function addAverageToResults(avgWER, avgWordErrorRate, tablePath) {
  const whitespace1 = new Array(44).join(' ')
  const whitespace2 = new Array(24 - avgWER.toString().length).join(' ')
  const whitespace3 = new Array(7 - avgWordErrorRate.toString().length).join(
    ' '
  )
  const newResult =
    '\n| ' +
    'Overall average' +
    whitespace1 +
    ' |  ' +
    avgWER +
    whitespace2 +
    ' |      ' +
    avgWordErrorRate +
    whitespace3 +
    ' |\n+------------------------------------------------------------+--------------------------+-------------+'
  fs.appendFileSync(tablePath, newResult)
}
