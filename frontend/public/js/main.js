import { readFileSync, writeFileSync } from "fs";
import { fileURLToPath } from "url";
import { resolve, dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const basePath = resolve(__dirname, "../");

const totalData = JSON.parse(readFileSync(join(basePath, "DATA_JSON/total_data.json")));
const summaryData = JSON.parse(readFileSync(join(basePath, "DATA_JSON/summary_data.json")));

const REPOSITORY = Object.keys(totalData);


// region generate index.html
const buttonHtml = REPOSITORY
                        .map(repo => 
                                `<button role='link' onclick="window.location='${repo}.html'">
                                    Repository ${repo}
                                </button>
                                <br/>
                                <br/>\n
                                `)
                        .join('');

const totalSummaryHtml = (() => {
    let totalSummary = "";
    Object.keys(summaryData).forEach((key) => {
        totalSummary += `<h4>${key.toUpperCase()}:<h4>\n`;
        Object.keys(summaryData[key]).forEach((subKey) => {
            totalSummary += `<p>${key} ${subKey}: ${summaryData[key][subKey]}</p>\n`;
        });
    });
    return totalSummary;
})();

let indexHTML = readFileSync(join(__dirname, "main.html"), "utf-8");
indexHTML = indexHTML.replace("BUTTON", buttonHtml);
indexHTML = indexHTML.replace("SUMMARY", totalSummaryHtml);
writeFileSync(join(__dirname, "index.html"), indexHTML);

//endregion

// region generate directory HTML
REPOSITORY.forEach((dirName, dirIndex) => {
    let htmlContent = readFileSync(join(__dirname, "repo.html"), "utf-8");;
    let htmlTotal = "";

    Object.keys(totalData[dirName]).forEach((nameFile) => {
        htmlTotal += `<h3>NAME FILE : ${nameFile}<h3>`;
        const FILE_CONTENT = totalData[dirName][nameFile];
        htmlTotal += "<h4>LEVELS: <h4>\n";
        
        Object.keys(FILE_CONTENT["Levels"]).forEach((level) => {
            htmlTotal += `<p>Levels ${level}: ${FILE_CONTENT["Levels"][level]}</p>\n`;
        });

        htmlTotal += "<h4>CLASSES: <h4>\n";
        
        Object.keys(FILE_CONTENT["Class"]).forEach((cls) => {
            htmlTotal += `<p>Class ${cls}: ${FILE_CONTENT["Class"][cls]}</p>\n`;
        });
    });

    const summaryHtml = (() => {
        const REPO_DATA = JSON.parse(readFileSync(join(basePath, "DATA_JSON/repo_data.json")));

        let summaryHTML = "<h3>Summary of file analysis: <h3>\n";
        const REPO_NAME = Object.keys(REPO_DATA)[dirIndex];

        Object.keys(REPO_DATA[REPO_NAME]).forEach((key, elem) => {
            summaryHTML += `<h4>${elem === 0 ? "LEVELS" : "CLASSES"}: <h4>\n`;

            Object.keys(REPO_DATA[REPO_NAME][key]).forEach((subKey) => {
                summaryHTML += `<p>${key} ${subKey}: ${REPO_DATA[REPO_NAME][key][subKey]}</p>\n`;
            });
        });

        return summaryHTML;
    })();

    htmlContent = htmlContent.replace("REPO", `<h2> REPOSITORY: ${dirName}</h2>\n`).replace("TOTAL", htmlTotal).replace("SUMMARY", summaryHtml);
    writeFileSync(join(__dirname, `${dirName}.html`), htmlContent);
});

// endregion

console.log("Website created.");
