import { readFileSync, writeFileSync } from "fs";
import { fileURLToPath } from "url";
import { resolve, dirname, join } from "path";

const dirPath = dirname(fileURLToPath(import.meta.url));
const basePath = resolve(dirPath, "../");

const TOTAL_DATA = JSON.parse(readFileSync(join(basePath, "DATA_JSON/total_data.json")));
const SUMMARY_DATA = JSON.parse(readFileSync(join(basePath, "DATA_JSON/summary_data.json")));

const REPOSITORY = Object.keys(TOTAL_DATA);


// region generate index.html
const BUTTON_HTML = REPOSITORY
                        .map(repo => 
                                `<button role='link' onclick="window.location='${repo}.html'">
                                    Repository ${repo}
                                </button>
                                <br/>
                                <br/>\n
                                `)
                        .join('');

const TOTAL_SUMMARY_HTML = (() => {
    let totalSummary = "";
    Object.keys(SUMMARY_DATA).forEach((key) => {
        totalSummary += `<h4>${key.toUpperCase()}:<h4>\n`;
        Object.keys(SUMMARY_DATA[key]).forEach((subKey) => {
            totalSummary += `<p>${key} ${subKey}: ${SUMMARY_DATA[key][subKey]}</p>\n`;
        });
    });
    return totalSummary;
})();

let indexHTML = readFileSync(join(dirPath, "main.html"), "utf-8");
indexHTML = indexHTML.replace("BUTTON", BUTTON_HTML);
indexHTML = indexHTML.replace("SUMMARY", TOTAL_SUMMARY_HTML);
writeFileSync(join(dirPath, "index.html"), indexHTML);

//endregion

// region generate directory HTML
REPOSITORY.forEach((dirName, dirIndex) => {
    let htmlContent = readFileSync(join(dirPath, "repo.html"), "utf-8");;
    let htmlTotal = "";

    Object.keys(TOTAL_DATA[dirName]).forEach((nameFile) => {
        htmlTotal += `<h3>NAME FILE : ${nameFile}<h3>`;
        const FILE_CONTENT = TOTAL_DATA[dirName][nameFile];
        htmlTotal += "<h4>LEVELS: <h4>\n";
        
        Object.keys(FILE_CONTENT["Levels"]).forEach((level) => {
            htmlTotal += `<p>Levels ${level}: ${FILE_CONTENT["Levels"][level]}</p>\n`;
        });

        htmlTotal += "<h4>CLASSES: <h4>\n";
        
        Object.keys(FILE_CONTENT["Class"]).forEach((cls) => {
            htmlTotal += `<p>Class ${cls}: ${FILE_CONTENT["Class"][cls]}</p>\n`;
        });
    });

    const SUMMARY_HTML = (() => {
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

    htmlContent = htmlContent.replace("REPO", `<h2> REPOSITORY: ${dirName}</h2>\n`).replace("TOTAL", htmlTotal).replace("SUMMARY", SUMMARY_HTML);
    writeFileSync(join(dirPath, `${dirName}.html`), htmlContent);
});

// endregion

console.log("Website created.");
