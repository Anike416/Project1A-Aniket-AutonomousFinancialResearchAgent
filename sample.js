const fs = require('fs');
const pdf = require('pdf-parse');

let dataBuffer = fs.readFileSync('463548A_Agentic-AI_Autonomous_Financial_Research_Agent.docx.pdf');

pdf(dataBuffer).then(function(data) {
    fs.writeFileSync("output.txt", data.text);
});