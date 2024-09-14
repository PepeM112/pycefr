import express from 'express';
import path from 'path';
import { exec } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { formatDate } from "./public/js/utils.js";   

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

// Serve results
app.get('/results', (req, res) => {
  const resultsDir = path.join(__dirname, '..', 'results');

  fs.readdir(resultsDir, (err, files) => {
    if (err) {
      return res.status(500).send("There was an error trying to read results folder");
    }

    const jsonFiles = files.filter(file => file.endsWith('.json'));
    const repoInfoArray = []

    jsonFiles.forEach((file, index) => {
      const filePath = path.join(resultsDir, file);

      // Read JSON file
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const jsonData = JSON.parse(fileContent);

      // Get repoInfo
      if (jsonData.repoInfo) {
        repoInfoArray.push({ ...jsonData.repoInfo })
      } else if (jsonData.dirInfo) {
        repoInfoArray.push({ ...jsonData.dirInfo })
      }
    })

    res.json(repoInfoArray);
  })
})

// Routing
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'html', 'home.html'));
});

app.get('/:filename', (req, res, next) => {
  const { filename } = req.params;
  const htmlTemplatePath = path.join(__dirname, 'public', 'html', 'repo.html')

  fs.access(htmlTemplatePath, fs.constants.F_OK, (err) => {
    if (err) {
      return next();
    } 
    
    fs.readFile(htmlTemplatePath, 'utf8', (err, htmlContent) => {
      if (err) {
        return res.status(500).send('Error reading HTML template')
      }

      // Substitute placeholders
      const jsonResultsPath = path.join(__dirname, '..', 'results', `${filename}.json`);
      
      fs.access(jsonResultsPath, fs.constants.F_OK, (err) => {
        if (err) {
          return res.status(404).send("Couldn't find results file");
        }

        fs.readFile(jsonResultsPath, 'utf8', (err, jsonData) => {
          if (err) {
            return res.status(500).send('Error reading JSON results')
          }
          
          const parsedData = JSON.parse(jsonData)

          const isLocal = !!parsedData.dirInfo;

          const repoInfo = parsedData.repoInfo || parsedData.dirInfo;
          const replacedHTML = htmlContent
            .replace(/PH_IS_LOCAL/g, isLocal ? 'true' : 'false')
            .replace(/PH_REPO_NAME/g, repoInfo.data?.name || 'N/A')
            .replace(/PH_REPO_DATE/g, formatDate(repoInfo.data?.createdDate) || 'N/A')
            .replace(/PH_TOTAL_FILES/g, repoInfo.data?.totalFiles || 'N/A')
            .replace(/PH_TOTAL_COMMITS/g, repoInfo.commits?.total_commits || 'N/A')
            .replace(/PH_TOTAL_CHANGES/g, repoInfo.commits?.total_files_modified || 'N/A')
            .replace(/PH_TOTAL_HOURS/g, repoInfo.commits?.total_hours || 'N/A')
            .replace(/PH_TOTAL_LINES/g, repoInfo.commits?.total_loc || 'N/A');

          res.send(replacedHTML);
        })
      })
    })
  });
});


app.get('/results/:repoName', (req, res) => {
  const { repoName } = req.params;
  const filePath = path.join(__dirname, '..', 'results', `${repoName}.json`);

  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (!err) {
      res.sendFile(filePath);
    } else {
      res.status(404).send('File not found');
    }
  });
});

// Serve CSS
app.use('/css', express.static(path.join(__dirname, 'public', 'css')));

// Serve JS
app.use('/js', express.static(path.join(__dirname, 'public', 'js')));

// Run project
app.post('/run-python', (req, res) => {
  const configFilePath = path.join(__dirname, 'config', 'config.json');

  // Guardar el archivo de configuración recibido
  fs.writeFile(configFilePath, JSON.stringify(req.body), (err) => {
    if (err) {
      return res.status(500).send(err);
    }

    // Ejecutar el script de Python
    exec('python3 pycerfl.py', (error, stdout, stderr) => {
      if (error) {
        console.error(error.message);
        return res.status(500).send('Error al ejecutar el script de Python');
      }

      if (stderr) {
        console.error(stderr);
        return res.status(500).send('Error en el script de Python');
      }

      console.log(`Resultado del script de Python: ${stdout}`);
      
      res.send(stdout);
    });
  });
});

app.listen(port, () => {
  console.log(`Listening http://localhost:${port}`);
});
