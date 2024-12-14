# viewers-leaderboard-backend
A Twitch extension that shows a leaderboard of viewers

## How to setup the project
### Install Python (>= 3.11)
This project uses Python 3.11, so make sure you have it installed. You can download the necessary version from [Python's official website](https://www.python.org/downloads/) or install it using your preferred method.

### Install pdm
The project dependencies is managed using [PDM](https://pdm-project.org/en/latest/). To install it, just open the terminal and execute the following command:

```shell
pip install -U pdm
```

## Install dependencies
After installing PDM, the next step is install the project dependencies. You can either use the provided make (if you have it installed) or just execute PDM manually.

```shell
make setup
```
or
```shell
pdm install
```

### Run locally
After installing all dependencies, the project is ready to run. Again, you can use the provided make command or do it manually through PDM.

```shell
make dev
```
or
```shell
pdm run uvicorn src.viewers_leaderboard.main:app --reload
```

After this, the project can be accessed through [http://localhost:8000]([http://localhost:8000])

## Optional configuration and commands

### Defining project port
If you want to run the project on a specific port, you just need to specify the `--port` param when running manually, or just set the `PORT` environment variable when using the make command.

```shell
PORT=8080 make dev
```

```shell
pdm run uvicorn src.viewers_leaderboard.main:app --port 8080 --reload
```

### Formatting code
The project already has the [black](https://black.readthedocs.io/en/stable/index.html) formatter as a dev dependency. If you want to format the code (src, tests), just use the make command or use black manually.

```shell
make format
```

```
pdm run black ./src
pdm run black ./tests
```
