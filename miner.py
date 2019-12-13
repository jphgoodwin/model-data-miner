from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
from datetime import datetime, timedelta
import os

def createDirectories():
    dslist = os.listdir("./datasets")

print(dslist)

def mine():
    for commit in RepositoryMining('https://github.com/curl/curl',
            since=(datetime.now() - timedelta(days=30)),
            only_modifications_with_file_types=['.c']).traverse_commits():
        if (commit.msg.find("fix") == -1 and commit.msg.find("bug") == -1):
            continue
        for mod in commit.modifications:
            if (mod.change_type == ModificationType.MODIFY and
                    mod.new_path[-2:] == ".c" and
                    mod.nloc <= 1000):
                print(mod.new_path)
                print("Number of LOC: {0}".format(mod.nloc), "\n",
                      "Token count: {0}".format(mod.token_count))



