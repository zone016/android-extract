#! /usr/bin/env python3
import sys
from pathlib import Path
from typing import Optional

import typer
from py_adb import Adb
from py_adb.exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable
from rich.console import Console
from rich.markup import escape
from rich.text import Text

console_stdout = Console()
console_stderr = Console(file=sys.stderr)

app = typer.Typer(
    help='Extract installed Android packages artifacts from remotes',
    name='extract',
)


def error_message(message: str):
    err_prefix = Text('err:', style='bold red')
    console_stderr.print(err_prefix, message)


def suc(message: str):
    suc_prefix = Text('suc:', style='bold green')
    console_stdout.print(suc_prefix, message, highlight=False)


def war(message: str):
    suc_prefix = Text('war:', style='bold yellow')
    console_stdout.print(suc_prefix, message, highlight=False)


def inf(message: str):
    suc_prefix = Text('inf:', style='bold blue')
    console_stdout.print(suc_prefix, message, highlight=False)


@app.command()
def main(
    list_devices: bool = typer.Option(
        False, '--list-devices', '-l', help='List available devices.'
    ),
    package_name: Optional[str] = typer.Argument(
        None, help='The package name from which to extract artifacts.'
    ),
    output_dir: Optional[str] = typer.Option(
        None, '--output', '-o', help='Where to save the extracted artifact(s).'
    ),
    device: Optional[str] = typer.Option(
        None, '--device', '-d', help='Specify the device to extract from.'
    ),
):
    if not list_devices and not package_name:
        error_message(
            'You must specify at least one option. '
            'Check [b]--help[/] for more information.'
        )
        exit(1)

    if list_devices and package_name:
        error_message(
            'You cannot list devices and pull artifacts at the same time.'
        )
        exit(1)

    adb: Adb
    try:
        adb = Adb()
    except AdbIsNotAvailable:
        error_message(
            'The Android Debug Bridge is not available in your [b]$PATH[/]. '
            'Make sure you have the Android SDK available with the correct '
            'tooling available.'
        )
        exit(1)
    except AdbHaveMultipleMatches:
        error_message(
            'You have multiple matches for Android Debug Bridge in '
            '[b]$PATH[/]. Make sure you have only one.'
        )
        exit(1)

    devices = adb.list_devices()
    if len(devices) == 0:
        error_message('No devices are detected.')
        exit(1)

    if list_devices and not package_name:
        inf('Available device(s):')
        for device in devices:
            console_stdout.print(f'- {device}', highlight=False)
        exit(0)

    if len(devices) > 1:
        error_message(
            'Multiple devices are detected. '
            'Specify the device to extract from using '
            '[b]--device[/b] or [b]-d[/] option.'
        )
        exit(1)

    android_device = devices[0] if len(devices) == 1 else None
    if not android_device:
        if device not in devices:
            error_message('Device does not exist in your host.')
            exit(1)
        android_device = devices[devices.index(device)]

    packages = adb.search_package(android_device, package_name)
    if len(packages) == 0:
        error_message('No packages found with the specified name.')
        exit(1)

    if len(packages) > 1:
        war('Multiple packages found with the specified name:')
        for package in packages:
            console_stdout.print(f'- [b]{escape(package)}[/b]')
        exit(1)

    package = packages[0]
    suc(f'Package [b]{escape(package)}[/b] found!')

    if not output_dir:
        output_dir = package
        inf(f'Using [b]{escape(package)}[/b] as the output directory.')

    if Path(output_dir).is_dir():
        error_message(
            f'Output directory [b]{escape(output_dir)}[/b] already exists.'
        )
        exit(1)

    artifacts = adb.get_application_artifacts(android_device, package)
    if not artifacts or len(artifacts) == 0:
        error_message('Package does not have any artifact.')
        exit(1)

    Path(output_dir).mkdir()
    inf(f'Found [b]#{len(artifacts)} artifact(s)[/b].')
    for artifact in artifacts:
        file_name = Path(artifact).name
        destination_path = Path(output_dir) / Path(file_name)
        inf(f'Extracting artifact [b]{escape(file_name)}[/b]...')
        adb.pull_file(android_device, artifact, str(destination_path))
        suc('Artifact extracted successfully!')

    inf(f'Artifacts extracted to [b]{escape(output_dir)}[/b]!')


if __name__ == '__main__':
    app()
