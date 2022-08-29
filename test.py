import os
import tarfile
import gzip


def foo(path):
    # file = tarfile.open(path)
    # file.extractall(os.path.dirname(path))
    # file.close()
    # os.remove(path)
    gzFilePath = str(path).replace('.tar', '.gz')
    csvFilePath = gzFilePath.replace('.gz', '')
    with gzip.open(gzFilePath) as gz:
        with open(csvFilePath, 'w+') as f:
            f.write(gz.read().decode('UTF-8'))
            f.close()
            gz.close()  


foo('/tmp/states_2020-06-01-04.csv.tar')
foo('/tmp/states_2020-05-25-05.csv.tar')
