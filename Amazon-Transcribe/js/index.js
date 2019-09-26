const wer = require('./wer.js')

async function main() {
  let jobName = process.argv[2]
  let isError = checkIfError()

  // Results are processed here
  if (!isError) {
    console.log('\n******RESULTS' + ' ~ ' + jobName + '******')

    let refPath = process.argv[3]
    let hypPath = process.argv[4]
    let resultsTablePath = process.argv[5]
    let resultsCSVPath = process.argv[6]
    let refIndex = Number(process.argv[7])

    let ref = wer.readRef(refPath)
    const splitRef = ref.split('\n')
    let lineCount = 0
    let cleanRef = []
    for (let i = 0; i < splitRef.length; i++) {
      if (splitRef[i] !== '') {
        cleanRef[lineCount] = splitRef[i]
        lineCount++
      }
    }
    ref = cleanRef[refIndex]

    const hyp = wer.readHyp(hypPath)
    console.log('\nOriginal:\n', ref)
    console.log('\nTranscribed text:\n', hyp)

    wer.calculate(ref, hyp, jobName, resultsTablePath, resultsCSVPath)
    console.log('\n*******************')
  } else {
    let resultsTablePath = process.argv[4]
    let resultsCSVPath = process.argv[5]
    wer.calculateError('Error: ' + jobName, resultsTablePath, resultsCSVPath)
  }
}

function checkIfError() {
  if (process.argv[3] === 'err') return true
  else return false
}

main().catch(console.error)
