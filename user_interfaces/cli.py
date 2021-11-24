#!/usr/bin/env python3

from __future__ import annotations
from PyInquirer import prompt
import os
from pathlib import Path
import typer
import json
import sys
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from PyInquirer import style_from_dict, Token

custom_style_2 = style_from_dict(
    {
        Token.Separator: "#6C6C6C",
        Token.QuestionMark: "#FF9D00 bold",
        # Token.Selected: '',  # default
        Token.Selected: "#5F819D",
        Token.Pointer: "#FF9D00 bold",
        Token.Instruction: "",  # default
        Token.Answer: "#5F819D bold",
        Token.Question: "",
    }
)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces.interface_skeleton import InterfaceSkeleton  # noqa: E402
from user_interfaces.utils import (  # noqa: E402
    getBenchmarksToRun,
    getSettings,
    getSuitesToRun,
    setItUp,
    suiteMaker,
    logIT,
    tablify,
)
from common.phoronix_parser import phoronix_init, phoronix_install  # noqa: E402

home_dir = Path.cwd()


# This CLI interface makes use of Typer (https://typer.tiangolo.com/)
# which has an extensible functionality.


app = typer.Typer()


class InteractiveMenu:
    def __init__(self) -> None:
        self.selectBenchmark: dict = {}
        self.selectSettings: dict = {}
        self.home_dir = Path.cwd()
        self.runnerDict: dict = {}
        self.type = None

    def runner(self) -> None:
        """
        Run interactive prompts.

        Questions are put as a list of dictionary which are shown to user as prompts.
        """
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
                    "Quit",
                ],
            }
        ]

        self.selectRunChoice = prompt(self.runChoice, style=custom_style_2)

        # If user chooses to quit the cli
        if self.selectRunChoice["runchoice"] == "Quit":
            exit()

        # If user chooses to make their own suite =>
        if self.selectRunChoice["runchoice"] == "Make your own suite":
            self.buildSuite()

        # Else if user chooses to execute a benchmark/suite =>
        else:
            runChoices = {
                "Benchmark Suite": "Suite",
                "Stand Alone Benchmark": "Benchmark",
            }

            self.type = runChoices.get(self.selectRunChoice["runchoice"])
            if self.type == "Suite":
                choices = getSuitesToRun()
            elif self.type == "Benchmark":
                choices = getBenchmarksToRun()
            choices.append({"name": "Quit"})
            self.benchmarks = [
                {
                    "type": "list",
                    "message": "Select Benchmark",
                    "name": "benchmark",
                    "qmark": "💻",
                    "choices": choices,
                    "validate": lambda answer: ValueError("no input")
                    if len(answer) == 0
                    else True,
                }
            ]
        self.selectBenchmark = prompt(self.benchmarks, style=custom_style_2)

        # If user quit
        if self.selectBenchmark["benchmark"] == "Quit":
            exit()

        # Check that user selected a benchmark atleast
        if not self.selectBenchmark["benchmark"]:
            raise Exception("There are no benchmarks to run.")

        # Benchmark driver=>
        if self.type == "Benchmark":
            self.runBenchmark()

        # Suite driver=>
        elif self.type == "Suite":
            self.runSuite()

    def runBenchmark(self) -> None:
        """Run benchmark."""
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
        if not isinstance(out, type(None)):
            logIT(
                benchmark=bmark,
                settings=self.selectSettings["settings"],
                logs=out["output"],
            )
        else:
            logIT(
                benchmark=bmark,
                settings=self.selectSettings["settings"],
                logs="The Benchmark doesn't return any log",
            )

    def runSuite(self) -> None:
        """Run the suite."""
        suite = self.selectBenchmark["benchmark"]
        suitePath = os.path.join(home_dir, "suites", suite)
        out = InterfaceSkeleton().startBenchmark(runType=self.type, suitePath=suitePath)
        logIT(benchmark=suite[:-5], logs=out)

    def buildSuite(self) -> None:
        """Take in attributes of suite and build a suite for the specifications."""
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
        if len(suiteBuild["benchInSuite"]) <= 0:
            raise Exception("Can't make a suite with no benchmarks.")
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
        suiteMaker(suiteBuild=suiteBuild, suiteList=_suiteList)
        exit()

    def benchmarkBanner(self) -> None:
        print(
            r"   ___                   _____          ____   ____ "
            r"  / _ \ _ __   ___ _ __ |  ___|__  _ __| __ ) / ___|"
            r" | | | | '_ \ / _ \ '_ \| |_ / _ \| '__|  _ \| |    "
            r" | |_| | |_) |  __/ | | |  _| (_) | |  | |_) | |___ "
            r"  \___/| .__/ \___|_| |_|_|  \___/|_|  |____/ \____|"
            r"       |_|                                          "
            r" ====Welcome to the OpenForBC Benchmarking Tool==== "
        )


# Non interactive menu =>


@app.command()
def interactive(interactive: bool = typer.Argument(True)) -> None:
    """Interactive/Non interactive router."""
    if interactive:
        InteractiveMenu().runner()
    else:
        raise typer.Exit(code=5)


# Run benchmark with python user_interfaces/cli.py run-benchmark
@app.command()
def run_benchmark(  # noqa: C901
    input: List[str] = typer.Option(..., "-b", "--benchmark", help="benchmark name"),
    settings: str = typer.Option(None, "-s", "--settings", help="benchmark settings"),
    verbose: int = typer.Option(None, "--verbose", "-v", help="modify verbosity"),
) -> None:
    """Run the given benchmarks."""
    _availableBench = [
        x["name"] for x in getBenchmarksToRun()
    ]  # List of all available benchmarks
    for benchmark in input:
        if benchmark not in _availableBench:
            typer.echo(
                f"{benchmark} implementation doesn't exist. To list available benchmarks"
                " use list-benchmarks command"
            )
            continue
        benchmarkPath = os.path.join(Path.cwd(), "benchmarks", benchmark)

        # Check if setup file present in benchmark directory
        if (
            Path(os.path.join(benchmarkPath, "setup.py")).exists()
            or Path(os.path.join(benchmarkPath, "setup.sh")).exists()
        ):
            setItUp(benchmarkPath)

        # Use default settings if settings option None
        if settings is None:
            with open(os.path.join(benchmarkPath, "benchmark_info.json")) as info:
                settings = json.load(info)["default_settings"]
        elif settings not in os.listdir(os.path.join(benchmarkPath, "settings")):
            raise Exception("Setting not found.")
        try:
            out = InterfaceSkeleton().startBenchmark(
                bmark=benchmark, settings=settings, verbosity=verbose
            )
        except Exception as e:
            raise Exception(f"{e}The benchmark run failed")

        if not isinstance(out, type(None)):
            try:
                logIT(benchmark=benchmark, settings=settings, logs=out["output"])
            except TypeError as e:
                print(f"{e} Encountered while logging")
        else:
            logIT(
                benchmark=benchmark,
                settings=settings,
                logs="The Benchmark doesn't return any log",
            )


# Run suite with python user_interfaces/cli.py run-suite
@app.command()
def run_suite(suite: str = typer.Argument(..., help="Suite name")) -> None:
    """Run the given Suite."""
    _availableSuites = [x["name"] for x in getSuitesToRun()]
    if suite not in _availableSuites:
        typer.echo(
            f"{suite} implementation doesn't exist. Please check available "
            "benchmarks using list-suites command"
        )
        typer.Exit()
    suitePath = os.path.join(home_dir, "suites", suite)
    try:
        benchmarkOutput = InterfaceSkeleton().startBenchmark(
            runType="suite", suitePath=suitePath
        )
    except Exception as e:
        raise Exception(f"{e}The benchmark run failed")
    logIT(benchmark=suite[:-5], logs=benchmarkOutput)


# Make a suite with python user_interfaces/cli.py make-suite
@app.command()
def make_suite(
    suite_name: str = typer.Option(..., "--name", help="Suite name"),
    benchmarks: List[str] = typer.Option(..., "-b", help="Benchmarks in the suite"),
    settings: List[str] = typer.Option(
        ..., "-s", help="Settings for corresponding benchmarks"
    ),
    filename: str = typer.Option(..., "-f", help="filename"),
    description: str = typer.Option("No description", "-d", help="description"),
) -> None:
    """Make a suite out of given benchmarks."""
    # TODO: Make a check to ensure settings and benchmarks exist.
    if len(settings) != len(benchmarks):
        typer.echo("Unequal number of settings for benchmarks")
        raise typer.Exit()
    _suiteList = []
    for i in range(len(benchmarks)):
        _suiteList.append(dict({"name": benchmarks[i], "settings": settings[i]}))
    # Define suitebuilding dictionary for the suite.
    suiteBuild = {
        "SuiteName": suite_name,
        "SuiteDescription": description,
        "FileName": filename,
    }
    suiteMaker(suiteBuild=suiteBuild, suiteList=_suiteList)


# List all suites with python user_interfaces/cli.py list-suites
@app.command()
def list_suites(csv: bool = typer.Option(False, "--csv", help="show as csv")) -> None:
    """List available suites."""
    suites_list = [list(i.values()) for i in getSuitesToRun()]
    if not csv:
        table = tablify(legend=["suites"], data=suites_list)
        typer.echo(table)
    else:
        typer.echo(suites_list)


# List all benchmarks with python user_interfaces/cli.py list-benchmarks
@app.command()
def list_benchmarks(
    csv: bool = typer.Option(False, "--csv", help="show as csv")
) -> None:
    """List available benchmarks."""
    benchmark_list = [list(i.values()) for i in getBenchmarksToRun()]
    if not csv:
        table = tablify(legend=["benchmarks"], data=benchmark_list)
        typer.echo(table)
    else:
        typer.echo(benchmark_list)


# Get available settings with python user_interfaces/cli.py get-settings
@app.command()
def get_settings(
    benchmark: str = typer.Option(..., "-b", "--benchmark", help="benchmark name"),
    settings: str = typer.Option(None, "-s", "--settings", help="settings file"),
    csv: bool = typer.Option(False, "--csv", help="show as csv"),
) -> None:
    """Get the settings for the benchmark."""
    # If user wants to read the contents of a setting in a benchmark
    if settings is not None:
        try:
            with open(
                os.path.join(home_dir, "benchmarks", benchmark, "settings", settings),
                "r",
            ) as settingsFile:
                output = json.load(settingsFile)
                typer.echo(
                    json.dumps(output, indent=4)
                )  # Print the contents of the settingsFile
        except FileNotFoundError as e:
            typer.echo(f"{e}: Settings doesn't exist")

    # If user wants to see what all settings are present for a benchmark
    else:
        settings_list = []
        try:
            settings_list = [
                [file]
                for file in os.listdir(
                    os.path.join(home_dir, "benchmarks", benchmark, "settings")
                )
            ]
        except FileNotFoundError as e:
            typer.echo(f"{e}:No settings folder in {benchmark} directory.")
        assert len(settings_list) > 0 and not isinstance(
            settings_list, type(None)
        )  # Check to make sure settings list is not empty
        if not csv:
            table = tablify(
                legend=["settings"], data=settings_list, sorting=True, col=0
            )
            typer.echo(table)
        else:
            typer.echo(settings_list)


# List all logs with python user_interfaces/cli.py list-logs
@app.command()
def list_logs(csv: bool = typer.Option(False, "--csv", help="show as csv")) -> None:
    """List all previous logs."""
    logPath = os.path.join(home_dir, "logs")
    index = 0
    tableOutput = []
    for root, _, files in os.walk(logPath):
        if "output.log" in files:
            root = root.split(os.path.sep)
            for pathChunk in root:
                res = re.match(
                    r"(19|20)\d\d(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])", pathChunk
                )  # Regex pattern to match yyyymmdd

                # If pattern matches:
                if res is not None:
                    date = pathChunk.split("_")[0]  # Extract date
                    formatted_date = (
                        date[:4] + "-" + date[4:6] + "-" + date[6:]
                    )  # Format it to add hypens for printing
                    for i in range(len(root)):
                        if root[i] == "logs":
                            bmark = root[i + 1]  # root[i+1] is the benchmark name
                            settings = root[i + 2]  # root[i+2] is the settings name
                            index += 1
                            break
                    # Check settings != date (ie. not a suite) and benchmark name doesn't
                    # have 'suite' in it
                    # TODO: make a stronger check
                    if not settings.find(date) and bmark.find("suite"):
                        settings = "-"
                    tableOutput.append([index, formatted_date, bmark, settings])
    if not csv:
        table = tablify(
            legend=["Index", "Date", "Benchmark", "settings"], data=tableOutput
        )
        typer.echo(table)
    else:
        typer.echo(tableOutput)


@app.command()
def install_phoronix(
    benchmark: str = typer.Option(..., "-b", "--benchmark", help="benchmark name"),
    version: str = typer.Option(None, "-v", "--version", help="benchmark version"),
) -> None:
    """Install a benchmark from Phoronix repository."""
    phoronix_init()
    phoronix_install(benchmark_name=benchmark, benchmark_v=version)


if __name__ == "__main__":
    app()
