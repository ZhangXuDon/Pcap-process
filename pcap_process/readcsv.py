import csv
import pickle
import os

csv_files_path = "csvfile"

# with open("non-Tor.csv", mode='w', encoding='utf-8') as write_file:
with open("non-Tor.csv", 'w+', newline='') as csv_file:
    csvwriter = csv.writer(csv_file)
    for dirpath, dirnames, filenames in os.walk(csv_files_path):
        for filename in sorted(filenames):
            path = os.path.join(dirpath, filename)
            print(path)
            with open(path, 'r') as file:
                # line = file.readline()
                csvreader = csv.reader(file)
                for line in csvreader:
                    csvwriter.writerow(line)
                    # print(line)
                    # write_file.write(line)
