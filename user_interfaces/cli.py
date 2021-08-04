from PyInquirer import prompt
import os
from pathlib import Path
from examples import custom_style_2
import typer
import json
import sys
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces.utils import (
    getBenchmarksToRun,
    getSettings,
    getSuitesToRun,
    setItUp,
    suiteMaker,
    logIT
)
from user_interfaces.interface_skeleton import InterfaceSkeleton



app = typer.Typer()
home_dir = Path.cwd()


class InteractiveMenu:                     
    def __init__(self):
        self.selectBenchmark: dict = {}
        self.selectSettings: dict = {}
        self.home_dir = Path.cwd()
        self.runnerDict: dict = {}
        self.type = None

    def runner(self):
        self.benchmarkBanner()
        self.runChoice = [
            {
                "type": "list",
                "name": "runchoice",
                "qmark": "💻",
                "message": "Collective benchmark suite or individual run?",
                "choices": [
                    "Benchmark Suite",
                    "Stand Alone Benchmark",
                    "Make your own suite",
                ],
            }
        ]
        self.selectRunChoice = prompt(self.runChoice, style=custom_style_2)
        if self.selectRunChoice["runchoice"] == "Make your own suite":
            suiteBuilder = [
                {
                    "type": "input",
                    "name": "SuiteName",
                    "message": "What would you like to call your suite?",
                },
                {
                    "type": "input",
                    "name": "SuiteDescription",
                    "message": "Add description for your suite",
                },
                {
                    "type": "checkbox",
                    "message": "Select Benchmark(s) to add to the suite",
                    "name": "benchInSuite",
                    "choices": getBenchmarksToRun(),
                },
                {
                    "type": "input",
                    "name": "FileName",
                    "message": "Filename for your created suite",   
                },
            ]
            suiteBuild = prompt(suiteBuilder, style=custom_style_2)
            _suiteList = []
            for bmark in suiteBuild["benchInSuite"]:
                suite_settings = {
                    "type": "list",
                    "message": f"Select Settings to use for {bmark}",
                    "name": "settings",
                    "qmark": "->",
                    "choices": getSettings(bmark, self.type),
                    # "validate": lambda x: os.path.isfile(x),
                }
                suiteSettings = prompt(suite_settings, style=custom_style_2)
                _suiteList.append(
                    dict({"name": bmark, "settings": suiteSettings["settings"]})
                )
            suiteMaker(suiteBuild=suiteBuild,suiteList=_suiteList)
            exit()
        elif self.selectRunChoice["runchoice"] == "Benchmark Suite":
            self.type = "Suite"
        else:
            self.type = "Benchmark"
        self.benchmarks = [
            {
                "type": "list",
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

        self.selectBenchmark = prompt(self.benchmarks, style=custom_style_2)
        if not self.selectBenchmark["benchmark"]:
            raise Exception("There are no benchmarks to run.")

        if self.type == "Benchmark":
            bmark = self.selectBenchmark["benchmark"]
            benchmarkPath = os.path.join(Path.cwd(), "benchmarks", bmark)
            if (
                Path(os.path.join(benchmarkPath, "setup.py")).exists()
                or Path(os.path.join(benchmarkPath, "setup.sh")).exists()
            ):
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
            out = InterfaceSkeleton().startBenchmark(
                runType=self.type, bmark=bmark, settings=self.selectSettings["settings"]
            )
            if not isinstance(out,type(None)):
                logIT(benchmark = bmark,settings = self.selectSettings["settings"],logs = out["output"])
        elif self.type == "Suite":
            suite = self.selectBenchmark["benchmark"]
            suitePath = os.path.join(home_dir, "suites", suite)
            out = InterfaceSkeleton().startBenchmark(runType=self.type, suitePath=suitePath)
            logIT(benchmark = suite[:-5],logs = out)

    def benchmarkBanner(self):
        print("   ___                   _____          ____   ____ ")
        print("  / _ \ _ __   ___ _ __ |  ___|__  _ __| __ ) / ___|")
        print(" | | | | '_ \ / _ \ '_ \| |_ / _ \| '__|  _ \| |    ")
        print(" | |_| | |_) |  __/ | | |  _| (_) | |  | |_) | |___ ")
        print("  \___/| .__/ \___|_| |_|_|  \___/|_|  |____/ \____|")
        print("       |_|                                          ")
        print(" ====Welcome to the OpenForBC Benchmarking Tool==== ")



# Non interactive menu =>

@app.command()
def interactive(
    interactive: bool = typer.Argument(True)
):
    """
    Interactive/Non interactive router.
    """
    if interactive:
        InteractiveMenu().runner()
    else:
        raise typer.Exit(code = 5)


@app.command()
def run_benchmark(
    input: List[str] = typer.Option(...,'-b','--benchmark',help ="benchmark name"),
    settings: str = typer.Option(None,'-s','--settings',help = "benchmark settings"),
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
        if (
            Path(os.path.join(benchmarkPath, "setup.py")).exists()
            or Path(os.path.join(benchmarkPath, "setup.sh")).exists()
        ):
            setItUp(benchmarkPath)
        print(settings)
        if settings == None:
            with open(os.path.join(benchmarkPath, "benchmark_info.json")) as info:
                settings = json.load(info)["default_settings"]
        elif settings not in os.listdir(os.path.join(benchmarkPath,"settings")):
            raise Exception("Setting not found.")
        out = InterfaceSkeleton().startBenchmark(
            bmark=benchmark, settings=settings, verbosity=verbose
        )
        logIT(benchmark = benchmark,settings = benchSetting,logs = out["output"])

@app.command()
def run_suite(
    suite: str = typer.Argument(...,help = "Suite name")
    ):
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
    benchmarkOutput = InterfaceSkeleton().startBenchmark(runType="suite", suitePath=suitePath)
    logIT(benchmark = suite[:-5],logs = benchmarkOutput)

@app.command()
def make_suite(
    suite_name: str = typer.Option(..., "--name", help="Suite name"),
    benchmarks:List[str] = typer.Option(...,'-b',help ="Benchmarks in the suite"),
    settings:List[str] = typer.Option(...,'-s',help = "Settings for corresponding benchmarks"),
    filename:str = typer.Option(...,'-f',help="filename"),
    description:str = typer.Option("No description",'-d',help="description")
    ):
    """
    Makes a suite out of given benchmarks
    """
    #TODO: Make a check to ensure settings and benchmarks exist.
    if len(settings) != len(benchmarks):
        typer.echo("Unequal number of settings for benchmarks")
        raise typer.Exit()
    _suiteList = []
    for i in range(len(benchmarks)):
        _suiteList.append(
            dict({"name": benchmarks[i], "settings": settings[i]})
            )
    suiteBuild = {
        "SuiteName":suite_name,
        "SuiteDescription":description,
        "FileName":filename
    }
    suiteMaker(suiteBuild=suiteBuild,suiteList=_suiteList)


@app.command()
def list_suites():
    """
    Lists available suites
    """
    for suites in getSuitesToRun():
        typer.echo(suites["name"])


@app.command()
def list_benchmarks():
    """
    Lists available benchmarks
    """
    for bmark in getBenchmarksToRun():
        typer.echo(bmark["name"])


@app.command()
def get_settings(
    benchmark: str = typer.Option(...,'-b','--benchmark',help ="benchmark name"),
    settings:str = typer.Option(None,'-s','--settings',help="settings file")
    ):
    """
    Gets the settings for the benchmark
    """
    if settings != None:
        try:
            with open(os.path.join(home_dir,'benchmarks',benchmark,'settings',settings),'r') as settingsFile:
                output = json.load(settingsFile)
                typer.echo(json.dumps(output,indent=4))
        except FileNotFoundError as e:
            typer.echo(f"{e}: Settings doesn't exist")
    else:
        settings_list = []
        try:
            settings_list =  os.listdir(os.path.join(home_dir,'benchmarks',benchmark, "settings"))
        except FileNotFoundError as e:
            typer.echo(f"No settings folder in {benchmark} directory.")
        assert len(settings_list) > 0 and not isinstance(settings_list,type(None))
        for setting in settings_list:
            typer.echo(setting)


if __name__ == "__main__":
    app()

