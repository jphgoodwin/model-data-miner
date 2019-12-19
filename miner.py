from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
from datetime import datetime, timedelta
import os
import re
import pandas as pd
from pycparser import c_parser

def createDirectories():
    dslist = os.listdir("./datasets")

    highest = 0
    for ds in dslist:
        if (int(ds[-1]) > highest):
            highest = int(ds[-1])
    highest += 1

    os.makedirs("./datasets/dataset#{0}/bug".format(highest))
    os.mkdir("./datasets/dataset#{0}/not-bug".format(highest))

    return "./datasets/dataset#{0}".format(highest)


def mine(direpath):
    total = 0
    remaining = 0
    count = 0
    dflist = []
    for commit in RepositoryMining('https://github.com/curl/curl',
            since=(datetime.now() - timedelta(days=1095)),
            only_modifications_with_file_types=['.c']).traverse_commits():
        total += 1
        if (not re.search("[\s^][fF]ix|[\s^][bB]ug", commit.msg)):
            continue
        for mod in commit.modifications:
            if (mod.change_type == ModificationType.MODIFY and
                    mod.new_path[-2:] == ".c" and
                    mod.nloc <= 1000):
                remaining += 1
                print(commit.msg)
                print(mod.new_path)
                print("Number of LOC: {0}".format(mod.nloc), "\n",
                      "Token count: {0}".format(mod.token_count))

                fbug = open("{0}/bug/example#{1}.c".format(direpath, remaining),
                        "w")
                fbug.write(mod.source_code_before)
                fbug.close()

                dflist.append(pd.DataFrame([[count, mod.source_code_before, 0]],
                        columns=["id", "code", "label"]))
                count += 1

                ffix = open("{0}/not-bug/example#{1}.c".format(direpath, remaining),
                        "w")
                ffix.write(mod.source_code)
                ffix.close()
                dflist.append(pd.DataFrame([[count, mod.source_code, 1]],
                        columns=["id", "code", "label"]))
                count += 1
    
    pd.concat(dflist, ignore_index=True).to_pickle("{0}/examples.pkl".format(direpath))

    print("total: {0}, remaining: {1}".format(total, remaining))

def readPickle(direpath):
    df = pd.read_pickle("{0}/examples.pkl".format(direpath))
    print(df.iloc[0]["code"])
    # print(df)
    return df

def parseCode(df):
    parser = c_parser.CParser()
    ast = parser.parse(df.iloc[0]["code"])
    print(ast)

# direpath = createDirectories()
# mine(direpath)
# readPickle(direpath)
df = readPickle("./datasets/dataset#4")

parseCode(df)

