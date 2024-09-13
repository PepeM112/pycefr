# **pycefr**

## [OUTDATED]

## *Identifying Python3 Code Level Using the CERFL Framework as Inspiration*

### What is this project about?
The goal of pycefrl is to create a tool capable of obtaining an evaluation inspired by the [''Common European Framework of Reference for Languages''](https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages) for code written in the Python programming language, version 3.

With this tool it is possible to analyze the level of GitHub repositories (and their developers) or code snippets in Python3.

### How to use it?

There are 3 ways of running it:


#### 1. Analyze a GitHub repository
  ```bash
  python3 pycerfl.py [-r | --repo] <repo_url> 
  ```

Performs full analysis on a valid GitHub repository and fetches relevant related to the repository.

#### 2. Analyze a GitHub user
  ```bash
  python3 pycerfl.py [-u | --user] <user_name> 
  ```

Retrieves information about a valid GitHub user, asking which of the public projects of such user you would like to perform the analysis on. Once chosen, performs full analysis on a valid GitHub repository and fetches relevant related to the repository.

#### 3. Analyze a local directory
  ```bash
  python3 pycerfl.py [-d | --directory] <dir_path> 
  ```

Performs full analysis on a directory. If it is detected that the directory is a GitHub project the user is asked if he would like to analyse the origin repository instead of the local files. If yes it analyses the repository as in (1), else it perform analysis on the local files. 

### After analysis

Once the analysis is done, a json file will be generated in a folder named results/. You can visualize here the results.

However, you can also visualize all your results using Node.js.

To install dependencies position yourself inside frontend folder and execute:

```bash
npm install
```

After that, you can run the local server:

```bash
node server.js
```

### Options

There is a settings.json in place in order to setup some configurations:

|Settings | Description |
|:--------|:-------------:|
|**ignoreFolders**| Folders whose names appear here will be excluded from the analysis. No absolute nor relative paths, just folder name |
|**API-KEY**|GitHub api key in order to be avoid the limit on calls to GitHub api.|
|**addLocalSuffix**|Allows to perform a local analysis without overwritting the results of a repository with the same name as the directory being analysed, by adding (if set to True) a suffix to the results file|

An example of a settings.json could be:
```json
{
    "ignoreFolders": [
        "node_modules/",
        "myenv/",
        ".git/",
        "__pycache__/"
    ],
    "API-KEY": "",
    "addLocalSuffix": true
}
```