from __future__ import print_function, unicode_literals
from PyInquirer import prompt, Separator
import os
from pathlib import Path
from examples import custom_style_2
import typer
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import (
    getBenchmarksToRun,
    getSettings,
    getSuitesToRun,
    EmptyBenchmarkList,
    setItUp,
)
from interface_skeleton import InterfaceSkeleton


app = typer.Typer()
home_dir = Path.cwd()


class InteractiveMenu:
    def __init__(self):
        self.selectBenchmark: dict = {}
        self.selectSettings: dict = {}
        self.home_dir = Path.cwd()
        self.runnerDict: dict = {}
        self.type = None
        self.runChoice = [
            {
                "type": "list",
                "name": "runchoice",
                "message": "Collective benchmark suite or individual run?",
                "choices": [
                    "Benchmark Suite",
                    "Stand Alone Benchmark",
                    Separator(),
                    "Make your own suite",
                    {
                        "name": "Suite builder",
                        "disabled": "function under construction",
                    },
                ],
            }
        ]

    def runner(self):
        self.benchmarkBanner()
        self.selectRunChoice = prompt(self.runChoice, style=custom_style_2)
        if self.selectRunChoice["runchoice"] == "Make your own suite":
            raise ValueError("This function hasn't been implemented yet")
        elif self.selectRunChoice["runchoice"] == "Benchmark Suite":
            self.type = "Suite"
            qtype = "list"
        else:
            self.type = "Benchmark"
            qtype = "checkbox"
        self.benchmarks = [
            {
                "type": qtype,
                "message": "Select Benchmark",
                "name": "benchmark",
                "qmark": "💻",
                "choices": getSuitesToRun()
                if self.type == "Suite"
                else getBenchmarksToRun(),
                "validate": lambda answer: ValueError("no input")
                if len(answer) == 0
                else True,
            }
        ]

        ## TODO: Print the benchmarks in a suite in an informative way.

        self.selectBenchmark = prompt(self.benchmarks, style=custom_style_2)
        if not self.selectBenchmark["benchmark"]:
            raise EmptyBenchmarkList

        if self.type == "Benchmark":
            for bmark in self.selectBenchmark["benchmark"]:
                benchmarkPath = os.path.join(Path.cwd(), "benchmarks", bmark)
                if "setup.py" or "setup.sh" in os.listdir(benchmarkPath):
                    setup = typer.prompt(
                        "We found setup file in your directory. Would you like to use it?(y/n)"
                    )
                if setup == "y" or "Y":
                    setItUp(benchmarkPath)
                self.pick_settings = [
                    {
                        "type": "list",
                        "message": f"Select Settings to use for {bmark}",
                        "name": "settings",
                        "qmark": "->",
                        "choices": getSettings(bmark, self.type),
                        "validate": lambda x: os.path.isfile(x),
                    }
                ]
                self.selectSettings = prompt(self.pick_settings)
            InterfaceSkeleton().startBenchmark(
                runType=self.type, bmark=bmark, settings=self.selectSettings["settings"]
            )
        elif self.type == "Suite":
            suite = self.selectBenchmark["benchmark"]
            suitePath = os.path.join(home_dir, "suites", suite)
            InterfaceSkeleton().startBenchmark(runType=self.type, suitePath=suitePath)

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
    interactive: bool = typer.Option(False, prompt="Run program in interactive mode?")
):
    """
    Ask user if they want interactive interface or not
    """
    if interactive:
        InteractiveMenu().runner()
    else:
        raise typer.Exit()


@app.command()
def run_benchmark(
    input: List[str],
    verbose: int = typer.Option(None, "--verbose", "-v", help="modify verbosity"),
):
    """
    Runs the given benchmarks
    """
    _availableBench = [x["name"] for x in getBenchmarksToRun()]
    for benchmark in input:
        if benchmark not in _availableBench:
            typer.echo(
                f"{benchmark} implementation doesn't exist. Please check available benchmarks using list-benchmarks command"
            )
            continue
        benchmarkPath = os.path.join(Path.cwd(), "benchmarks", benchmark)
        if "setup.py" or "setup.sh" in os.listdir(benchmarkPath):
            setup = typer.prompt(
                "We found setup file in your directory. Would you like to use it?(y/n)"
            )
        if setup == "y" or "Y":
            setItUp(benchmarkPath)
        benchSetting = typer.prompt(
            f"What settings would you like for {benchmark} <space> for default"
        )
        if benchSetting == " " or benchSetting not in getSettings(
            benchmark, "Benchmark"
        ):
            benchSetting = "settings1.json"
        else:
            benchSetting += ".json"
        InterfaceSkeleton().startBenchmark(
            bmark=benchmark, settings=benchSetting, verbosity=verbose
        )


@app.command()
def run_suite(suite: str):
    """
    Runs the given Suite
    """
    _availableSuites = [x["name"] for x in getSuitesToRun()]
    if suite not in _availableSuites:
        typer.echo(
            f"{suite} implementation doesn't exist. Please check available benchmarks using list-suites command"
        )
        typer.Exit()
    suitePath = os.path.join(home_dir, "suites", suite)
    InterfaceSkeleton().startBenchmark(runType="suite", suitePath=suitePath)


@app.command()
def list_suites():
    """
    Lists available suites
    """
    for suites in getSuitesToRun():
        print(suites["name"])


@app.command()
def list_benchmarks():
    """
    Lists available benchmarks
    """
    for bmark in getBenchmarksToRun():
        print(bmark["name"])


@app.command()
def get_settings(benchmark: str, command: List[str] = ["help"]):
    """
    Gets the settings for the benchmark
    """
    InterfaceSkeleton().getSettings(
        bmark=benchmark, command=command, settings="settings1.json"
    )


if __name__ == "__main__":
    app()
