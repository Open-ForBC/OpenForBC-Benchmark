from __future__ import print_function, unicode_literals
from PyInquirer import prompt,Separator
import os
from pathlib import Path
from utils import getBenchmarksToRun, getSettings, setSettings, getSuitesToRun, EmptyBenchmarkList
import typer
from typing import Optional
from typing import Tuple
from examples import custom_style_2

# app = typer.Typer()


def interactive(
    interactive:bool = typer.Option(default = False,help="interactive interface (T/F).")
):
    if interactive:
        InteractiveMenu().runner()
    else:
        pass


# def getBenchmarks(
#     benchs: str = typer.Option(
#         default=None, help="Enter the benchmarks with a space distance"
#     )
# ):
#     typer.echo(f"{benchs.split(' ')}")
#     # benchNames = benchs.split(" ")
#     # print(benchNames)


# def runPreference(
#     pref: str = typer.Option(
#         default=None, help="Would you like to run benchmark as suite or seperately."
#     )
# ):
#     if pref == "suite":
#         pass  # Todo:print suites
#     elif pref == "individual":
#         pass  # Print individual benchmarks
#     else:
#         typer.echo("invalid input")


# @app.command()
# def getSettings(
#     settings: Optional[Path] = typer.Option(default = 'settings1',help="Which settings to use.")
# ):
#     settings_path = Path.cwd().joinpath('benchmarks','dummy_regressor','settings')
#     return os.listdir(settings_path)


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
        _setter = []
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
                _setter.append(
                    dict({"name": bmark, "settings": self.selectSettings["settings"]})
                )
                self.runnerDict = {"benchmarks": _setter}
                setSettings(self.runnerDict)
        
            elif self.type == 'Suite':
                pass
                #TODO: Fingure out suites settings
                # _setter.append(
                #     dict({"name": bmark, "settings": self.selectSettings["settings"]})
                # )
                # self.runnerDict = {"benchmarks": _setter}
                # setSettings(self.runnerDict)



def benchmarkBanner():
    print("   ___                   _____          ____   ____ ")
    print("  / _ \ _ __   ___ _ __ |  ___|__  _ __| __ ) / ___|")
    print(" | | | | '_ \ / _ \ '_ \| |_ / _ \| '__|  _ \| |    ")
    print(" | |_| | |_) |  __/ | | |  _| (_) | |  | |_) | |___ ")
    print("  \___/| .__/ \___|_| |_|_|  \___/|_|  |____/ \____|")
    print("       |_|                                          ")
    print(" ====Welcome to the OpenForBC Benchmarking Tool====")


if __name__ == "__main__":
    typer.run(interactive)
