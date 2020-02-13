from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
from datetime import datetime, timedelta
import os
import re
import pandas as pd
from pycparser import c_parser
import tempfile
import subprocess
import sys

def createDirectory():
    dslist = os.listdir("./datasets")

    highest = 0
    for ds in dslist:
        if (int(ds[-1]) > highest):
            highest = int(ds[-1])
    highest += 1

    direpath = "./datasets/dataset#{0}".format(highest) 
    os.mkdir(direpath)
    return direpath


def buildDataset(direpath):
    temp_dir = tempfile.TemporaryDirectory()
    dflist = []
    count = 0

    exdirlist = os.listdir("./codeflaws")

    for exdir in exdirlist:
        if not os.path.isdir("./codeflaws/{0}".format(exdir)):
            continue
        components = exdir.split('-')
        if len(components) != 5:
            continue
        contestId = components[0]
        problem = components[1]
        bugId = components[-2]
        accId = components[-1]

        bug_path = "./codeflaws/{0}/{1}-{2}-{3}.c".format(exdir, contestId,
                problem, bugId)
        acc_path = "./codeflaws/{0}/{1}-{2}-{3}.c".format(exdir, contestId,
                problem, bugId)

        # Preprocess the buggy submission.
        args = ["gcc", "-nostdinc", "-E", bug_path,
                "-Ipycparser/utils/fake_libc_include"]
        result = subprocess.run(args, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        
        if (result.returncode != 0):
            print(result.returncode)
            print("STDERR: {0}".format(result.stderr.decode("utf8")))
            continue


        # Create dataframe. Label of "1" means bug.
        dfbug = pd.DataFrame([[count, result.stdout.decode("utf8"), 1]],
            columns=["id", "code", "label"])
        count += 1

        # Preprocess the accepted submission.
        args = ["gcc", "-nostdinc", "-E", acc_path,
                "-Ipycparser/utils/fake_libc_include"]
        result = subprocess.run(args, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        
        if (result.returncode != 0):
            print(result.returncode)
            print("STDERR: {0}".format(result.stderr.decode("utf8")))
            continue

        # Create dataframe. Label of "0" means non-bug.
        dfacc = pd.DataFrame([[count, result.stdout.decode("utf8"), 0]],
            columns=["id", "code", "label"])
        count += 1

        # Verify code can be parsed.
        try:
            parseCode(dfbug)
            parseCode(dfacc)
        except:
            print("Failed to parse {0}".format(exdir))
            continue

        # Append dataframes to dflist.
        dflist.append(dfbug)
        dflist.append(dfacc)
    
    return pd.concat(dflist, ignore_index=True)

def readPickle(direpath):
    df = pd.read_pickle("{0}/examples.pkl".format(direpath))
    # print(df.iloc[0]["code"])
    print(df)
    return df

def writePickle(direpath, dataframe):
    dataframe.to_pickle("{0}/examples.pkl".format(direpath))

def parseCode(df):
    parser = c_parser.CParser()
    ast = parser.parse(df.iloc[0]["code"])

direpath = createDirectory()
# direpath = ""
# df = readPickle(direpath)
# df = readPickle("./datasets/dataset#4")

dataframe = buildDataset(direpath)
writePickle(direpath, dataframe)
dataframe = readPickle(direpath)
# parseCode(dataframe)

