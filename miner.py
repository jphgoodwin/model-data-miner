from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
from datetime import datetime, timedelta
import os
import re

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
    for commit in RepositoryMining('https://github.com/curl/curl',
            since=(datetime.now() - timedelta(days=30)),
            only_modifications_with_file_types=['.c']).traverse_commits():
        total += 1
        if (not re.search("[\s^][fF]ix", commit.msg) and
                not re.search("[\s^][bB]ug", commit.msg)):
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

                ffix = open("{0}/not-bug/example#{1}.c".format(direpath, remaining),
                        "w")
                ffix.write(mod.source_code)
                ffix.close()


    print("total: {0}, remaining: {1}".format(total, remaining))

direpath = createDirectories()
mine(direpath)
