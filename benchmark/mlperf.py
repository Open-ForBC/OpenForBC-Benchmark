# File under construction


import subprocess
import os


def runInShell(command: str, loc: str):
    if loc == " ":
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, cwd=loc)
    output, error = process.communicate()
    return output, error


