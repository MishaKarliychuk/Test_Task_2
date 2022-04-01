import csv

def create_csv(filename, headers, data_rows):
    """Создает csv файл"""
    with open(filename, "w") as file:
        csv_writer = csv.writer(file)

        csv_writer.writerow(headers)
        csv_writer.writerows(data_rows)

def read_csv(filename):
    """Читает csv файл"""
    with open(filename, "r") as file:
        csv_reader = csv.reader(file)

        headers = next(csv_reader)
        data_rows = [row for row in csv_reader]
    return data_rows
