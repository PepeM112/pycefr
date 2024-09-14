import os
import json
from tabulate import tabulate


# Método para leer el archivo JSON
def read_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


# Método para mostrar los totales generales
def display_totals(data):
    print("Total commits:", data["commits"]["total_commits"])
    print("Total files:", data["commits"]["total_files_modified"])
    print("Total hours:", data["commits"]["total_hours"])
    print("Total loc:", data["commits"]["total_loc"])


# Método para mostrar los datos de los autores en formato de tabla
def display_author_info(data):
    authors = data["contributors"]

    table = []
    for author in authors:
        table.append(
            [
                author["name"],
                author["commits"],
            ]
        )

    headers = ["Author", "coms"]
    print(tabulate(table, headers, tablefmt="pipe", numalign="right"))


# Método principal que coordina la lectura y la visualización
def main(file_path):
    data = read_data(file_path)['repoInfo']
    print("Processing data...\n")
    display_totals(data)
    print("\nAuthor information:\n")
    display_author_info(data)


if __name__ == "__main__":
    filePath = os.path.abspath('results/pycefr.json')
    main(filePath)

