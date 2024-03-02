# Uma forma de conseguir os `.apk`

Este projeto é uma ferramenta de linha de comando desenvolvida para facilitar a extração de artefatos de pacotes instalados em dispositivos Android. Utilizando um wrapper do `adb`, permite aos usuários listar dispositivos disponíveis, especificar um pacote pelo nome para extrair seus artefatos e definir um diretório de saída para os artefatos extraídos além de instalar (tanto *split* apps quanto *packages* únicos) e desinstalar aplicativos.

## Instalação

Além das dependências para o próprio `adb`, você pode instalar diretamente deste repositório com o comando:

```bash
pip install git+ssh://git@github.com/zone016/android-extract.git
```

Atualizações também pode ser feitas dessa forma.

## Utilização

O CLI é muito simples, e seu README deve ser o suficiente para entender como utilizá-lo:

```plaintext
Usage: extract [OPTIONS] COMMAND [ARGS]...

  Extract installed Android packages artifacts from remotes

Options:
  --help  Show this message and exit.

Commands:
  install       Install split app or single package from the argument.
  list-devices  List available devices.
  pull          Pull artifacts from a package.
  uninstall     Uninstall an app.
```

Para procurar e desinstalar o aplicativo `br.com.bb.android`, podemos fazer algo como:

```bash
extract uninstall bb

suc: Package br.com.bb.android found!
inf: Uninstalling br.com.bb.android...
suc: Package uninstalled!
```

Ou instalar o aplicativo `com.picpay` como um *split* app:

```bash
ll

base.apk
split_config.x86_64.apk
split_config.xxhdpi.apk

extract install .

inf: Installing package to emulator-5554...
suc: The split package was installed!
```

O `extract` suporta qualquer sistema operacional, e deve funcionar em qualquer ambiente que tenha o `adb` (ou `adb.exe` no Windows) disponível no `$PATH`.
