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

// Middleware para parsear JSON en las solicitudes
app.use(express.json());

// Middleware para servir archivos estáticos desde la carpeta "public"
app.use(express.static(path.join(__dirname, 'public')));

// Middleware para redirigir solicitudes sin la extensión ".html" a los archivos HTML correspondientes
app.get('/:filename', (req, res, next) => {
  const { filename } = req.params;
  const filePath = path.join(__dirname, 'public', 'html', `${filename}.html`);

  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (!err) {
      res.sendFile(filePath);
    } else {
      next(); // Si el archivo no existe, pasa al siguiente middleware
    }
  });
});

// Middleware para servir archivos CSS y otros archivos estáticos
app.use('/css', express.static(path.join(__dirname, 'public', 'css')));

// Endpoint para manejar la edición y ejecución del archivo de configuración
app.post('/run-python', (req, res) => {
  const configFilePath = path.join(__dirname, 'config', 'config.json');

  // Guardar el archivo de configuración recibido
  fs.writeFile(configFilePath, JSON.stringify(req.body), (err) => {
    if (err) {
      return res.status(500).send('Error al guardar el archivo de configuración');
    }

    // Ejecutar el script de Python
    exec('python3 backend/pycerfl.py', (error, stdout, stderr) => {
      if (error) {
        console.error(`Error al ejecutar el script de Python: ${error.message}`);
        return res.status(500).send('Error al ejecutar el script de Python');
      }

      if (stderr) {
        console.error(`Error en el script de Python: ${stderr}`);
        return res.status(500).send('Error en el script de Python');
      }

      console.log(`Resultado del script de Python: ${stdout}`);
      
      // Enviar la respuesta al cliente
      res.send(stdout);
    });
  });
});

// Servir el archivo HTML principal
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'html', 'summary.html'));
});

app.listen(port, () => {
  console.log(`Listening http://localhost:${port}`);
});
