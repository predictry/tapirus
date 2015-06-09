import os
import os.path
import errno
import tempfile
import shutil
import csv
import json
import time

import luigi
import luigi.file

if os.name == 'posix':
    tempfile.tempdir = "/tmp"
else:
    tempfile.tempdir = "out"


CSV_EXTENSION = "csv"
JSON_EXTENSION = "json"
VALUE_SEPARATOR = ";"

