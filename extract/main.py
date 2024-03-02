#! /usr/bin/env python3
from pathlib import Path

import click
from printer.console import err, inf, sanitize, suc, war
from py_adb import Adb
from py_adb.exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable


def install_package(adb: Adb, device: str, origin: str) -> None:
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


def uninstall_package(adb: Adb, device: str, package: str) -> None:
    inf(f'Uninstalling {package}...')
    is_uninstalled = adb.uninstall_app(device, package)

    if is_uninstalled:
        suc('Package uninstalled!')
        exit(0)
    else:
        err('Unable to uninstall package!')
        exit(1)


def list_devices(adb: Adb) -> None:
    inf('Available device(s):')
    for device in adb.list_devices():
        print(f'- {device}')
    exit(0)


def pull_package(
    adb: Adb, device: str, package: str, output_dir: Path
) -> None:
    if output_dir.is_dir():
        err(
            f'Output directory [b]{sanitize(str(output_dir))}[/b] '
            f'already exists.'
        )
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

    inf(f'Artifacts extracted to [b]{sanitize(str(output_dir))}[/b]!')


def search_package(adb: Adb, device: str, package: str) -> str:
    packages = adb.search_package(device, package)
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

    return package


def get_adb_instance() -> Adb:
    try:
        adb = Adb()
    except AdbIsNotAvailable:
        err(
            'The Android Debug Bridge is not available in your $PATH. '
            'Make sure you have the Android SDK available with the '
            'correct tooling available.'
        )
        exit(1)
    except AdbHaveMultipleMatches:
        err(
            'You have multiple matches for Android Debug Bridge in $PATH. '
            'Make sure you have only one.'
        )
        exit(1)

    return adb


def device_exists(adb: Adb, device: str) -> bool:
    return device in adb.list_devices()


def get_device(adb: Adb) -> str:
    devices = adb.list_devices()
    if len(devices) == 0:
        err('No devices are visible for Android Debug Bridge.')
        exit(1)

    if len(devices) == 1:
        device = devices[0]
        return device

    if len(devices) > 1:
        err(
            'Multiple devices are visible for Android Debug Bridge. '
            'Please specify the device to extract from: '
        )
        for device in devices:
            print(f'- {device}')

        exit(1)

    return devices[0]


def ensure_get_device(adb: Adb, device: str) -> str:
    device = device if device else get_device(adb)
    if not device_exists(adb, device):
        err(
            f'Device [b]{sanitize(device)}[/b] does not exists '
            f'for Android Debug Bridge.'
        )
        exit(1)

    return device


@click.group(help='Extract installed Android packages artifacts from remotes')
def app():
    pass


@app.command(name='list-devices', help='List available devices.')
def list_devices_command():
    adb = get_adb_instance()

    inf('Available device(s):')
    for device in adb.list_devices():
        print(f'- {device}')

    exit(0)


@app.command(
    name='install',
    help='Install split app or single package from the argument.',
)
@click.argument('package', required=True)
@click.option(
    '--device',
    '-d',
    help='Specify the device to extract from.',
    required=False,
)
def install_command(package: str, device: str | None):
    adb = get_adb_instance()
    device = ensure_get_device(adb, device)

    install_package(adb, device, package)
    exit(0)


@app.command(name='uninstall', help='Uninstall an app.')
@click.argument('package', required=True)
@click.option(
    '--device',
    '-d',
    help='Specify the device to extract from.',
    required=False,
)
def uninstall_command(package: str, device: str):
    adb = get_adb_instance()
    device = ensure_get_device(adb, device)
    package = search_package(adb, device, package)

    uninstall_package(adb, device, package)
    exit(0)


@app.command(name='pull', help='Pull artifacts from a package.')
@click.argument('package', required=True)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Where to save the extracted artifact(s).',
    required=False,
)
@click.option(
    '--device',
    '-d',
    help='Specify the device to extract from.',
    required=False,
)
def pull_command(package: str, output: Path | None, device: str | None):
    adb = get_adb_instance()
    device = ensure_get_device(adb, device)

    package = search_package(adb, device, package)
    output = output if output else Path(package)

    pull_package(adb, device, package, output)
    exit(0)


if __name__ == '__main__':
    app()
