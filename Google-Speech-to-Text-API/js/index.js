const wer = require('./wer.js')

async function main() {
  let filePath = process.argv[2]
  let refPath = process.argv[3]
  let hypPath = process.argv[4]
  let resultsTablePath = process.argv[5]
  let resultsCSVPath = process.argv[6]
  let refIndex = Number(process.argv[7])

  // Results are processed here
  const transcribedFilename = filePath.replace(/^.*[\\\/]/, '')
  console.log('\n******RESULTS' + ' ~ ' + transcribedFilename + '******')

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
  console.log('\nTranscribed text:\n' + hyp)
  wer.calculate(ref, hyp, filePath, resultsTablePath, resultsCSVPath)

  console.log('\n*******************')
}

main().catch(console.error)
