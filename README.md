# Uma forma de conseguir os `.apk`

Este projeto é uma ferramenta de linha de comando desenvolvida para facilitar a extração de artefatos de pacotes instalados em dispositivos Android. Utilizando um wrapper do `adb`, permite aos usuários listar dispositivos disponíveis, especificar um pacote pelo nome para extrair seus artefatos e definir um diretório de saída para os artefatos extraídos além de instalar (tanto *split* apps quanto *packages* únicos) e desinstalar aplicativos.

## Instalação

Além das dependências para o próprio `adb`, você pode instalar diretamente deste repositório com o comando:

```bash
pip install git+ssh://git@github.com/zone016/pull-android-artifacts.git
```

Atualizações também pode ser feitas dessa forma.

## Utilização

O CLI é muito simples, e seu README deve ser o suficiente para entender como utilizá-lo:

```plaintext
extract --help

 Usage: extract [OPTIONS] [PACKAGE_NAME]

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   package_name      [PACKAGE_NAME]  The package name or path to an artifact to be installed. [default: None]             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --list-devices        -lD            List available devices.                                                             │
│ --output              -o       TEXT  Where to save the extracted artifact(s). [default: None]                            │
│ --device              -d       TEXT  Specify the device to extract from. [default: None]                                 │
│ --uninstall           -u             If specified, uninstall.                                                            │
│ --install             -i             Install split app or single package from the argument.                              │
│ --install-completion                 Install completion for the current shell.                                           │
│ --show-completion                    Show completion for the current shell, to copy it or customize the installation.    │
│ --help                               Show this message and exit.                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Para procurar e desinstalar o aplicativo `com.whatsapp`, podemos fazer algo como:

```bash
extract -u whats

suc: Package com.whatsapp found!
inf: Uninstalling com.whatsapp...
suc: Package uninstalled!
```

Ou instalar o aplicativo `com.vanuatu.aiqfome` como um *split* app:

```bash
ll

base.apk
split_config.en.apk
split_config.x86_64.apk
split_config.xxhdpi.apk

extract -i .

inf: Installing package to emulator-5554...
suc: The split package was installed!
```
