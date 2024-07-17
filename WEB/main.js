//-- PROGRAM TO CREATE A WEB PAGE

//-- Import external modules
const fs = require("fs");
const path = require("path");

//-- Define the base path as the root of the project directory
const basePath = path.resolve(__dirname, "../");

//-- Read html file
const REPO = fs.readFileSync(path.join(__dirname, "repo.html"), "utf-8");

//-- Read index.html
let INDEX = fs.readFileSync(path.join(__dirname, "main.html"), "utf-8");

//-- Define the path to the JSON files
const jsonDir = path.join(basePath, "DATA_JSON");

//-- Name of the Json files to read
const JSON_FILE = fs.readFileSync(
  path.join(jsonDir, "total_data.json"),
  "utf-8"
);
const JSON_FILESUM = fs.readFileSync(
  path.join(jsonDir, "summary_data.json"),
  "utf-8"
);
const JSON_FILEREPO = fs.readFileSync(
  path.join(jsonDir, "repo_data.json"),
  "utf-8"
);

//-- Create the store structure from the contents of the file
//-- Return us the json structure
var data_total = JSON.parse(JSON_FILE);
var data_summary = JSON.parse(JSON_FILESUM);
var data_repo = JSON.parse(JSON_FILEREPO);

//-- Variable that is going to have all the buttons available
let button = "";

//-- Get information
//-- Get Repository name
const repository = Object.keys(data_total);

//-- Create a button for each repository
for (let i = 0; i < repository.length; i++) {
  button +=
    "<button role='link' onclick=window.location='" +
    repository[i] +
    ".html'>Repository " +
    repository[i] +
    "</button><br><br>" +
    "\n";
}
INDEX = INDEX.replace("BUTTON", button);

//-- Write total in new html file
fs.writeFileSync(path.join(__dirname, "index.html"), INDEX);

//-- Obtain information from each repository
for (let repo = 0; repo < repository.length; repo++) {
  //-- Assign the value of REPO
  let content = REPO;
  //-- Variable total
  let total = "";
  let name_repo = "<h2> REPOSITORY: " + repository[repo] + "</h2>" + "\n";
  //-- Get total content
  let content_total = data_total[repository[repo]];

  //-- Get Files names
  let files = Object.keys(content_total);

  for (let file = 0; file < files.length; file++) {
    //-- Get name
    let name_file = files[file];
    total += "<h3>NAME FILE : " + name_file + "<h3>";
    let content_file = content_total[name_file];

    //-- Get levels
    let levels = content_file["Levels"];
    total += "<h4>LEVELS: <h4>" + "\n";
    for (let i = 0; i < Object.keys(levels).length; i++) {
      let keys = Object.keys(levels);
      let values = Object.values(levels);
      total += "<p>Levels " + keys[i] + ": " + values[i] + "</p>" + "\n";
    }
    //-- Get classes
    let clase = content_file["Class"];
    total += "<h4>CLASSES: <h4> " + "\n";
    for (let i = 0; i < Object.keys(clase).length; i++) {
      let keys = Object.keys(clase);
      let values = Object.values(clase);
      total += "<p>Class " + keys[i] + ": " + values[i] + "</p>" + "\n";
    }
  }
  let total_repo = repo_summary(repo);
  content = content.replace("REPO", name_repo);
  content = content.replace("TOTAL", total);
  content = content.replace("SUMMARY", total_repo);

  let name_html = path.join(__dirname, repository[repo] + ".html");

  //-- Write total in new html file
  fs.writeFileSync(name_html, content);
}

//-- Obtain repository summary information
function repo_summary(repo) {
  //-- Variable with the summary of each repository
  let total_repo = "<h3>Summary of file analysis: <h3>" + "\n";
  let repos = Object.keys(data_repo);
  //-- Get repository name
  let repo_name = repos[repo];
  //-- Get content of each repository
  let content = data_repo[repo_name];
  for (let elem = 0; elem < Object.keys(content).length; elem++) {
    let keys = Object.keys(content);
    let values = Object.values(content);
    if (elem === 0) {
      total_repo += "<h4>LEVELS: <h4>" + "\n";
    } else {
      total_repo += "<h4>CLASSES: <h4>" + "\n";
    }
    for (let value = 0; value < Object.keys(values[elem]).length; value++) {
      let key = Object.keys(values[elem])[value];
      let val = Object.values(values[elem])[value];
      total_repo += "<p>" + keys[elem] + " " + key + ": " + val + "</p>" + "\n";
    }
  }
  return total_repo;
}

//-- Obtain summary information
let total_summary = "";
let type = Object.keys(data_summary);
for (let i = 0; i < type.length; i++) {
  let key = type[i]; //-- Levels or Class
  total_summary += "<h4>" + key.toUpperCase() + ":<h4> " + "\n";
  let content = data_summary[key];
  for (let elem = 0; elem < Object.keys(content).length; elem++) {
    let keys = Object.keys(content);
    let values = Object.values(content);
    total_summary +=
      "<p>" + key + " " + keys[elem] + ": " + values[elem] + "</p>" + "\n";
  }
}
INDEX = INDEX.replace("SUMMARY", total_summary);
//-- Write total in new html file
fs.writeFileSync(path.join(__dirname, "index.html"), INDEX);

console.log("Website created.");
