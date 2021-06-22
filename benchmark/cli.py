import typer
import time 
from tasks import run
import subprocess
import time
from celery import uuid


app = typer.Typer()
benchmark_ran:bool = 0

def runInShell(command: str, loc: str):
    if loc == " ":
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, cwd=loc)
    output, error = process.communicate()
    return output, error


def getConfig():
    with typer.progressbar(range(100)) as progress:
        for value in progress:
            time.sleep(0.01)
    benchmarkRunner()

def checkForCompletion(res):
    while res.ready()!='TRUE':
        time.sleep(0.01)
    raise typer.Exit()


def benchmarkRunner():
    task_id = uuid()
    result = run.apply_async(task_id = task_id)
    runInShell("celery -A tasks worker --loglevel=INFO"," ")
    # checkForCompletion(result)   TODO:use a worker to check for completion

@app.command()
def showMenu():
    userChoice = 0
    while(userChoice!='q'):
        typer.secho(f"-----------------[ OPENFORBC-BENCHMARK ]-----------------", fg=typer.colors.GREEN)
        typer.echo("1.Start Benchmark")
        typer.echo("2.Stop Benchmark")
        typer.echo("3.Show Status")
        userChoice = str(typer.prompt("What'd you like to run?"))
        if userChoice == '1':
            typer.echo("Benchmark Started")
            typer.echo("Fetching configuration files...")
            getConfig()
        elif userChoice == '2':
            stopBenchmark()


def stopBenchmark():
    stop = typer.confirm("Are you sure you want to stop it?")
    if stop:
        raise typer.Exit()
    else:
        typer.echo("Not stopped")


if __name__ == "__main__":
    app()