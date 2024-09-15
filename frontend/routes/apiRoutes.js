import express from 'express';
import fs from 'fs';
import path from 'path';
import { formatDate } from "./../public/js/utils.js";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const router = express.Router();

// Serve results
router.get('/results', (req, res) => {
  const resultsDir = path.join(__dirname, '..', '..', 'results');

  fs.readdir(resultsDir, (err, files) => {
    if (err) {
      return res.status(500).send("There was an error trying to read results folder");
    }

    const jsonFiles = files.filter(file => file.endsWith('.json'));
    const repoInfoArray = [];

    jsonFiles.forEach((file, index) => {
      const filePath = path.join(resultsDir, file);

      // Read JSON file
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const jsonData = JSON.parse(fileContent);

      repoInfoArray.push({ ...jsonData.repoInfo });
    });

    res.json(repoInfoArray);
  });
});

// Serve specific results file
router.get('/results/:repoName', (req, res) => {
  const { repoName } = req.params;
  const filePath = path.join(__dirname, '..', '..', 'results', `${repoName}.json`);

  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (!err) {
      res.sendFile(filePath);
    } else {
      res.status(404).send('File not found');
    }
  });
});

export default router;
