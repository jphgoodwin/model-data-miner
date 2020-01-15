from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
from datetime import datetime, timedelta
import os
import re
import pandas as pd
from pycparser import c_parser
import tempfile
import subprocess

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
    totalCommits = 0
    remainingCommits = 0
    numMods = 0
    count = 0
    dflist = []
    temp_dir = tempfile.TemporaryDirectory()
    url = 'https://github.com/curl/curl'
    for commit in RepositoryMining(url,
            since=(datetime.now() - timedelta(days=10)),
            only_modifications_with_file_types=['.c'],
            clone_repo_to=temp_dir.name).traverse_commits():
        totalCommits += 1
        if (not re.search("[\s^][fF]ix|[\s^][bB]ug", commit.msg)):
            continue
        first = True
        for mod in commit.modifications:
            if (mod.change_type == ModificationType.MODIFY and
                    mod.new_path[-2:] == ".c" and
                    mod.nloc <= 1000):
                numMods += 1
                if (first):
                    remainingCommits += 1
                    first = False
                # print(commit.msg)
                # print(mod.new_path)
                # print("Number of LOC: {0}".format(mod.nloc), "\n",
                #       "Token count: {0}".format(mod.token_count))
                root_path = os.path.join(temp_dir.name, RepositoryMining._get_repo_name_from_url(url))
                file_path = os.path.join(root_path, mod.new_path)
                # print(os.path.isfile(file_path))

                args = ["gcc", "-E", file_path]

                for root, dirs, files in os.walk(root_path):
                    for dirname in dirs:
                        args.append("-I{0}".format(os.path.join(root, dirname)))

                print(args)
                result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print(result.stdout)
                print(result.returncode)

                # fbug = open("{0}/bug/example#{1}.c".format(direpath, numMods),
                #         "w")
                # fbug.write(mod.source_code_before)
                # fbug.close()

                # dflist.append(pd.DataFrame([[count, mod.source_code_before, 0]],
                #         columns=["id", "code", "label"]))
                count += 1

                # ffix = open("{0}/not-bug/example#{1}.c".format(direpath, numMods),
                #         "w")
                # ffix.write(mod.source_code)
                # ffix.close()
                # dflist.append(pd.DataFrame([[count, mod.source_code, 1]],
                #         columns=["id", "code", "label"]))
                count += 1

        break

        # print(os.listdir(os.path.join(temp_dir.name,
        #     RepositoryMining._get_repo_name_from_url(url))))
    
    # pd.concat(dflist, ignore_index=True).to_pickle("{0}/examples.pkl".format(direpath))

    print("total: {0}, remaining: {1}".format(totalCommits, remainingCommits))

def readPickle(direpath):
    df = pd.read_pickle("{0}/examples.pkl".format(direpath))
    # print(df.iloc[0]["code"])
    print(df)
    return df

def parseCode(df):
    parser = c_parser.CParser()
    ast = parser.parse(df.iloc[0]["code"])
    print(ast)

# direpath = createDirectories()
direpath = ""
mine(direpath)
# readPickle(direpath)
# df = readPickle("./datasets/dataset#4")

# subprocess.run("gcc -E {0}".format(df.iloc[0]["code"]))

# parseCode(df)

