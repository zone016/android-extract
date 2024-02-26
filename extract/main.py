#! /usr/bin/env python3
from pathlib import Path
from typing import Optional

import typer
from printer.console import err, inf, sanitize, suc, war
from py_adb import Adb
from py_adb.exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable

app = typer.Typer(
    help='Extract installed Android packages artifacts from remotes',
    name='extract',
)


def install(adb: Adb, device: str, origin: str) -> None:
    if not Path(origin).exists():
        err(f'The origin {sanitize(origin)} does not exists.')
        exit(1)

    inf(f'Installing package to [b]{sanitize(device)}[/b]...')
    if Path(origin).is_file():
        is_installed = adb.install_app(device, origin)
        if is_installed:
            suc(
                f'The package [b]{Path(sanitize(origin)).name}[/b] '
                f'was installed!'
            )
            exit(0)
        else:
            err(
                f'Unable to install package '
                f'[b]{Path(sanitize(origin)).name}[/b].'
            )
            exit(1)
    else:
        packages = [
            str(file) for file in Path(origin).iterdir() if file.is_file()
        ]

        if len(packages) == 1:
            err(
                f'The package [b]{sanitize(Path(packages[0]).name)}[/b] '
                f'must be installed with it full path instead of the folder!'
            )
            exit(1)

        is_installed = adb.install_split_app(device, packages)
        if is_installed:
            suc('The split package was installed!')
            exit(0)
        else:
            err('Unable to install the slip package.')
            exit(1)


def uninstall(adb: Adb, device: str, package: str) -> None:
    inf(f'Uninstalling {package}...')
    is_uninstalled = adb.uninstall_app(device, package)

    if is_uninstalled:
        suc('Package uninstalled!')
        exit(0)
    else:
        err('Unable to uninstall package!')
        exit(1)


def dump_devices(adb: Adb) -> None:
    inf('Available device(s):')
    for device in adb.list_devices():
        print(f'- {device}')
    exit(0)


def pull_package(adb: Adb, device: str, package: str, output_dir: str) -> None:
    if not output_dir:
        output_dir = package
        inf(f'Using [b]{sanitize(package)}[/b] as the output directory.')

    if Path(output_dir).is_dir():
        err(f'Output directory [b]{sanitize(output_dir)}[/b] already exists.')
        exit(1)

    artifacts = adb.get_application_artifacts(device, package)
    if not artifacts or len(artifacts) == 0:
        err('Package does not have any artifact.')
        exit(1)

    Path(output_dir).mkdir()
    inf(f'Found [b]#{len(artifacts)} artifact(s)[/b].')
    for artifact in artifacts:
        file_name = Path(artifact).name
        destination_path = Path(output_dir) / Path(file_name)
        inf(f'Extracting artifact [b]{sanitize(file_name)}[/b]...')
        adb.pull_file(device, artifact, str(destination_path))
        suc('Artifact extracted successfully!')

    inf(f'Artifacts extracted to [b]{sanitize(output_dir)}[/b]!')


@app.command()
def main(
    package_name: Optional[str] = typer.Argument(
        None, help='The package name or path to an artifact to be installed.'
    ),
    list_devices: bool = typer.Option(
        False, '--list-devices', '-lD', help='List available devices.'
    ),
    output_dir: Optional[str] = typer.Option(
        None, '--output', '-o', help='Where to save the extracted artifact(s).'
    ),
    device: Optional[str] = typer.Option(
        None, '--device', '-d', help='Specify the device to extract from.'
    ),
    uninstall_app: bool = typer.Option(
        False, '--uninstall', '-u', help='If specified, uninstall.'
    ),
    install_app: bool = typer.Option(
        False,
        '--install',
        '-i',
        help='Install split app or single package from the argument.',
    ),
):
    if not list_devices and not package_name:
        err(
            'You must specify at least one option. '
            'Check [b]--help[/] for more information.'
        )
        exit(1)

    if list_devices and package_name:
        err('You cannot list devices and pull artifacts at the same time.')
        exit(1)

    adb: Adb
    try:
        adb = Adb()
    except AdbIsNotAvailable:
        err(
            'The Android Debug Bridge is not available in your [b]$PATH[/]. '
            'Make sure you have the Android SDK available with the correct '
            'tooling available.'
        )
        exit(1)
    except AdbHaveMultipleMatches:
        err(
            'You have multiple matches for Android Debug Bridge in '
            '[b]$PATH[/]. Make sure you have only one.'
        )
        exit(1)

    devices = adb.list_devices()
    if len(devices) == 0:
        err('No devices are detected.')
        exit(1)

    if list_devices and not package_name:
        dump_devices(adb)

    if len(devices) > 1:
        err(
            'Multiple devices are detected. '
            'Specify the device to extract from using '
            '[b]--device[/b] or [b]-d[/] option.'
        )
        exit(1)

    android_device = devices[0] if len(devices) == 1 else None
    if not android_device:
        if device not in devices:
            err('Device does not exist in your host.')
            exit(1)
        android_device = devices[devices.index(device)]

    if install_app and uninstall_app:
        err('You cannot specify both install and uninstall!')
        exit(1)

    if install_app:
        install(adb, android_device, package_name)

    packages = adb.search_package(android_device, package_name)
    if len(packages) == 0:
        err('No packages found with the specified name.')
        inf(
            'Maybe you are trying to install? '
            'Check [b]--help[/b] for more details.'
        )
        exit(1)

    if len(packages) > 1:
        war('Multiple packages found with the specified name:')
        for package in packages:
            print(f'- {sanitize(package)}')
        exit(1)

    package = packages[0]
    suc(f'Package [b]{sanitize(package)}[/b] found!')

    if uninstall_app:
        uninstall(adb, android_device, package)

    pull_package(adb, android_device, package, output_dir)


if __name__ == '__main__':
    app()
