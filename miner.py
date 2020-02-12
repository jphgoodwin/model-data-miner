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

                # Preprocess file post-commit.
                args = ["gcc", "-nostdinc", "-E", file_path, "-Ipycparser/utils/fake_libc_include"]

                for root, dirs, files in os.walk(root_path):
                    for dirname in dirs:
                        args.append("-I{0}".format(os.path.join(root, dirname)))

                result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if (result.returncode != 0):
                    print(result.returncode)
                    print("STDERR: {0}".format(result.stderr))
                    break

                ffix = open("{0}/not-bug/example#{1}.c".format(direpath, numMods),
                        "bw")
                ffix.write(result.stdout)
                ffix.close()
                dflist.append(pd.DataFrame([[count, result.stdout.decode("ascii"), 1]],
                        columns=["id", "code", "label"]))
                count += 1

                # Open in write mode and write pre-commit text to file.
                f = open(file_path, "w")
                f.write(mod.source_code_before)
                f.close()

                # Preprocess file pre-commit.
                result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if (result.returncode != 0):
                    print(result.returncode)
                    print("STDERR: {0}".format(result.stderr))
                    break

                fbug = open("{0}/bug/example#{1}.c".format(direpath, numMods),
                        "bw")
                fbug.write(result.stdout)
                fbug.close()
                dflist.append(pd.DataFrame([[count, result.stdout.decode("ascii"), 0]],
                        columns=["id", "code", "label"]))
                count += 1

        if (not first):
            break

        # print(os.listdir(os.path.join(temp_dir.name,
        #     RepositoryMining._get_repo_name_from_url(url))))
    
    pd.concat(dflist, ignore_index=True).to_pickle("{0}/examples.pkl".format(direpath))

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

direpath = createDirectories()
# direpath = ""
mine(direpath)
df = readPickle(direpath)
# df = readPickle("./datasets/dataset#4")

parseCode(df)

