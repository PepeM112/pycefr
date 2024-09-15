import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import apiRoutes from './routes/apiRoutes.js';
import htmlRoutes from './routes/htmlRoutes.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

// Use routes
app.use('/api', apiRoutes);
app.use('/', htmlRoutes);

// Serve CSS
app.use('/css', express.static(path.join(__dirname, 'public', 'css')));

// Serve JS
app.use('/js', express.static(path.join(__dirname, 'public', 'js')));

app.listen(port, () => {
  console.log(`Listening http://localhost:${port}`);
});
