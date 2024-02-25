# Uma forma de conseguir os `.apk`

Este projeto é uma ferramenta de linha de comando desenvolvida para facilitar a extração de artefatos de pacotes instalados em dispositivos Android. Utilizando um wrapper do `adb`, permite aos usuários listar dispositivos disponíveis, especificar um pacote pelo nome para extrair seus artefatos e definir um diretório de saída para os artefatos extraídos.

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

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────╮
│   package_name      [PACKAGE_NAME]  The package name from which to extract artifacts.               │
│                                     [default: None]                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --list-devices        -l            List available devices.                                         │
│ --output              -o      TEXT  Where to save the extracted artifact(s). [default: None]        │
│ --device              -d      TEXT  Specify the device to extract from. [default: None]             │
│ --install-completion                Install completion for the current shell.                       │
│ --show-completion                   Show completion for the current shell, to copy it or customize  │
│                                     the installation.                                               │
│ --help                              Show this message and exit.                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
