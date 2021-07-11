from __future__ import print_function, unicode_literals
from PyInquirer import prompt,Separator
import os
from pathlib import Path
from examples import custom_style_2
import typer
import sys
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import getBenchmarksToRun, getSettings, getSuitesToRun, EmptyBenchmarkList
from interface_skeleton import InterfaceSkeleton

app = typer.Typer()


class InteractiveMenu:
    def __init__(self):
        self.selectBenchmark: dict = {}
        self.selectSettings: dict = {}
        self.home_dir = Path.cwd()
        self.runnerDict: dict = {}
        self.type = None
        self.runChoice = [
            {
                'type':'list',
                'name': 'runchoice',
                'message': 'Collective benchmark suite or individual run?',
                'choices':[
                    'Benchmark Suite',
                    'Stand Alone Benchmark',
                   Separator(),
                    'Make your own suite',
                    {
                        'name': 'Suite builder',
                        'disabled': 'function under construction'
                    }
                ] 
            }
        ]

    def runner(self):
        self.benchmarkBanner()
        self.selectRunChoice = prompt(self.runChoice,style=custom_style_2)
        if self.selectRunChoice['runchoice'] == 'Make your own suite':
            raise ValueError('This function hasn\'t been implemented yet')
        if self.selectRunChoice['runchoice'] == 'Benchmark Suite':
            self.type = 'Suite'
        else:
            self.type = 'Benchmark'
        self.benchmarks = [
            {
                "type": "checkbox",
                "message": "Select Benchmark",
                "name": "benchmark",
                "qmark": "💻",
                "choices": getSuitesToRun() if self.type =='Suite' else getBenchmarksToRun(),
                "validate": lambda answer: ValueError("no input")
                if len(answer) == 0
                else True,
            }
        ]

        ## TODO: Print the benchmarks in a suite in an informative way.


        self.selectBenchmark = prompt(self.benchmarks, style=custom_style_2)
        if not self.selectBenchmark["benchmark"]:
            raise EmptyBenchmarkList
        for bmark in self.selectBenchmark["benchmark"]:
            self.pick_settings = [
                {
                    "type": "list",
                    "message": f"Select Settings to use for {bmark}",
                    "name": "settings",
                    "qmark": "->",
                    "choices": getSettings(bmark,self.type),
                    "validate": lambda x: os.path.isfile(x),
                }
            ]
            self.selectSettings = prompt(self.pick_settings)
            print(f"send command to run {bmark} with { self.selectSettings['settings'] } settings.")
            if self.type == 'Benchmark':
                InterfaceSkeleton().startBenchmark(bmark,self.selectSettings['settings'])
            elif self.type == 'Suite':
                pass
                #TODO: Fingure out suites settings


    def benchmarkBanner(self):
        print("   ___                   _____          ____   ____ ")
        print("  / _ \ _ __   ___ _ __ |  ___|__  _ __| __ ) / ___|")
        print(" | | | | '_ \ / _ \ '_ \| |_ / _ \| '__|  _ \| |    ")
        print(" | |_| | |_) |  __/ | | |  _| (_) | |  | |_) | |___ ")
        print("  \___/| .__/ \___|_| |_|_|  \___/|_|  |____/ \____|")
        print("       |_|                                          ")
        print(" ====Welcome to the OpenForBC Benchmarking Tool==== ")


@app.command()
def interactive(
    interactive:bool = typer.Option(False,prompt ="Run program in interactive mode?")
    ):
    '''
        Ask user if they want interactive interface or not
    '''
    if interactive:
        InteractiveMenu().runner()
    else:
        raise typer.Exit()
    

@app.command()
def run_benchmark(
    input:List[str]
    ):
    '''
    Runs the given benchmarks
    '''
    _availableBench = [x["name"] for x in getBenchmarksToRun()]
    for benchmark in input:
        if benchmark not in _availableBench:
            typer.echo(f'{benchmark} implementation doesn\'t exist. Please check available benchmarks using list-benchmarks command')
            continue
        benchSet = typer.prompt(f"What settings would you like for {benchmark} <space> for default")
        if benchSet == ' ' or benchSet not in getSettings(benchmark,'Benchmark'):
            benchSet = 'settings1.json'
        else:
            benchSet+='.json'
        InterfaceSkeleton().startBenchmark(benchmark,benchSet)


# @app.command()
# def run_suite(
#     input:List[str]
#     ):


@app.command()
def list_suites():
    '''
        Lists available suites
    '''
    for suites in getSuitesToRun():
        print(suites['name'])

@app.command()
def list_benchmarks():
    '''
        Lists available benchmarks
    '''
    for bmark in getBenchmarksToRun():
        print(bmark['name'])

@app.command()
def get_settings(
    benchmark:str,
    command:List[str]):
    '''
        Gets the settings for the benchmark
    '''
    InterfaceSkeleton().getSettings(bmark = benchmark,command = command,settings ='settings1.json')



if __name__ == "__main__":
    app()

