import express, { json } from 'express';
import fs from 'fs';
import path from 'path';
import { formatDate } from './../public/js/utils.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const router = express.Router();

router.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'html', 'home.html'));
});

router.get('/:filename', (req, res, next) => {
  const { filename } = req.params;
  const htmlTemplatePath = path.join(__dirname, '..', 'public', 'html', 'repo.html');

  fs.access(htmlTemplatePath, fs.constants.F_OK, (err) => {
    if (err) {
      return next();
    }

    fs.readFile(htmlTemplatePath, 'utf8', (err, htmlContent) => {
      if (err) {
        return res.status(500).send('Error reading HTML template');
      }

      // Substitute placeholders
      const jsonResultsPath = path.join(__dirname, '..', '..', 'results', `${filename}.json`);

      fs.access(jsonResultsPath, fs.constants.F_OK, (err) => {
        if (err) {
          return res.status(404).send(`Couldn't find results file: ${ jsonResultsPath }"`);
        }

        fs.readFile(jsonResultsPath, 'utf8', (err, jsonData) => {
          if (err) {
            return res.status(500).send('Error reading JSON results');
          }

          const parsedData = JSON.parse(jsonData);
          const repoInfo = parsedData.repoInfo;
          const isLocal = !repoInfo.commits;

          let total_values = {};

          if (!isLocal) {
            total_values = repoInfo.commits.reduce((acc, commit) => {
              acc.total_commits += commit.commits;
              acc.total_hours += commit.total_hours;
              acc.total_files_modified += commit.total_files_modified;
              acc.total_loc += commit.loc;
              return acc;
            }, {
              total_commits: 0,
              total_hours: 0,
              total_files_modified: 0,
              total_loc: 0
            });
          }

          const replacedHTML = htmlContent
            .replace(/PH_IS_LOCAL/g, isLocal ? 'true' : 'false')
            .replace(/PH_REPO_NAME/g, repoInfo.data.name || 'N/A')
            .replace(/PH_REPO_DATE/g, formatDate(repoInfo.data.createdDate) || 'N/A')
            .replace(/PH_TOTAL_FILES/g, total_values.totalFiles || 'N/A')
            .replace(/PH_TOTAL_COMMITS/g, total_values.total_commits || 'N/A')
            .replace(/PH_TOTAL_CHANGES/g, total_values.total_files_modified || 'N/A')
            .replace(/PH_TOTAL_HOURS/g, total_values.total_hours || 'N/A')
            .replace(/PH_TOTAL_LINES/g, total_values.total_loc || 'N/A');

          res.send(replacedHTML);
        });
      });
    });
  });
});

export default router;
