# viewers-leaderboard-backend
A Twitch extension that shows a leaderboard of viewers

## How to setup the project
### docker-compose option

If you want to just run the application together with the database, the project provides a `docker-compose.yml` file to allow running it with docker. To do this, make sure you have `docker` and `docker-compose` installed and just use the command:

```shell
docker-compose up
```

After this, the application should be available at [http://localhost:8000](http://localhost:8000).
However, if you want to install and run the application outside docker, just follow the next sections.


### Install Python (>= 3.11)
This project uses Python 3.11, so make sure you have it installed. You can download the necessary version from [Python's official website](https://www.python.org/downloads/) or install it using your preferred method.

### Install pdm
Project dependencies are managed using [PDM](https://pdm-project.org/en/latest/). To install it, just open the terminal and execute the following command:

```shell
pip install -U pdm
```

## Install dependencies
After installing PDM, the next step is to install the project dependencies. You can either use the provided make command (if you have it installed) or just execute PDM manually.

```shell
make setup
```
or
```shell
pdm install
```

### Set environment variables
Some environment variables need to be set before running the application. You can create your own `.env` file or create a copy of `.env.example` and make the necessary changes.

```
# .env

env="dev"
app_name="Viewers Leaderboard Backend"
twitch_signature_validation=true
app_client_id="client_id"
app_client_secret="cl13nt_s3cr3t"
app_access_token="access_token"
webhook_secret="w3bh00k_s3cr3t"
mongo_conn_str="mongodb+srv://username:password@url.com/"
mongo_db_name="viewers_leaderboard"
```

### Run locally
After installing all dependencies, the project is ready to run. Again, you can use the provided make command or do it manually with PDM.

```shell
make dev
```
or
```shell
pdm run uvicorn src.viewers_leaderboard.main:app --reload
```

After this, the application can be accessed at [http://localhost:8000](http://localhost:8000).

### Application Swagger UI

The project includes a swagger page that can be accessed through the [/docs](http://localhost:8000/docs) path. There you can find information about the endpoints and can also test requests.

## Other configuration and commands

### Running tests

The project uses [pytest](https://docs.pytest.org/en/stable/) to run the tests. You can do so using the make command or manually using `pytest`:

```
make test
```
or
```
pdm run pytest
```

### Disabling Twitch webhook signature validation (for testing purposes)

By default, the application validates requests from Twitch using the `twitch-eventsub-message-signature` header. If you to do local testing without connecting directly to Twitch, you can do so using a enviroment variable:

```shell
export TWITCH_SIGNATURE_VALIDATION=false
```

> [!CAUTION]
> Disabling this validation can create a security issue for the application.

### Overriding the active livestream check
By default, after receiving a request from Twitch, the application check if there's a active livestream for that given broadcaster and uses its start timestamp to create specific validations (preventing multiple points before time gap, duplicated points for joining stream, etc). To bypass this check, you can use special headers in the request:

```
# Stream broadcaster id
active-stream-broadcaster-id-override

# Stream start timestamp
active-stream-started-at-override
```

The information about those header can also be found in the [/docs](http://localhost:8080) page when running the project.

> [!NOTE]
> This only works for `dev` environment. For other environments, this override is disabled.

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
