import express from 'express';
import path from 'path';
import { exec } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

// Routing
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'html', 'summary.html'));
});

app.get('/:filename', (req, res, next) => {
  const { filename } = req.params;
  const filePath = path.join(__dirname, 'public', 'html', `${filename}.html`);

  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (!err) {
      res.sendFile(filePath);
    } else {
      next();
    }
  });
});

// Load CSS
app.use('/css', express.static(path.join(__dirname, 'public', 'css')));

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
