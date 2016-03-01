
import json
from pprint import pprint

import textmining


def genCSV(srcFile, destFile, mapFile):
    with open(srcFile) as dataFile:
        data = json.load(dataFile)

    size = len(data)
    print size
    mapWrite = open(mapFile, "w")

    tdm = textmining.TermDocumentMatrix()
    for index in range(size):
        tdm.add_doc(data[index]["newsContext"])
        record = "doc" + str(index + 1) + "\t\t" + data[index]["newsTitle"] + "\t\t" + data[index]["newsCategory"] + "\n"
        mapWrite.write(record.encode("utf-8"))

    tdm.write_csv(destFile, cutoff = 1)
    #for row in tdm.rows(cutoff=1):
        #print row
    dataFile.close()
    mapWrite.close()
    return True

if __name__ == "__main__":
    srcFile = "items.json"
    destFile = "matrix.csv"
    mapFile = "docNameMap.txt"
    genCSV(srcFile, destFile, mapFile)
