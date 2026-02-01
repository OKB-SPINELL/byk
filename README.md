# byk (Book)

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/Junzki/byk?utm_source=oss&utm_medium=github&utm_campaign=Junzki%2Fbyk&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FJunzki%2Fbyk.svg?type=small)](https://app.fossa.com/projects/git%2Bgithub.com%2FJunzki%2Fbyk?ref=badge_small)

A simple book manager.

## Usage

### Run API Server

**Please make sure to run API server in async mode.**  
The dev server (`django manage.py runserver`) is already integrated with async support with Daphne.  

For production environment, you can use any kind of ASGI server, e.g., Daphne, Uvicorn, Hypercorn, etc.  
For example, using Hypercorn:
```bash
hypercorn byk.asgi:application --bind 0.0.0.0:8000
```

You are strongly recommended to use `byk.settings_env` for production, or you can create your own settings module based
on it.  
Please make sure to configure database and run migrations prior to exposing the service to public.
```bash
export DJANGO_SETTINGS_MODULE=byk.settings_env  # or your custom settings module
python byk-server/manage.py migrate
```


### Run Task Worker

```bash
faststream run byk.task_broker.app:faststream_app
```

## Requirements
- Python 3.12+
- PostgreSQL 14+
- Redis 7+

Please see [requirements](requirements.txt) for detail.

If you are using Windows, please run this project with Docker/Podman or WSL, as some dependencies may not support 
Windows natively.  
Please refer to [docker-compose.yml](docker-compose.yml) for an example of setting up the environment with Docker.


## License
This project is licensed under the **GNU General Public License v3 (GPLv3)**.

### Third-party Component Notices
The module [`byk/nlc_isbn`](byk-server/nlc_isbn/README.md) contains code derived from [DoiiarX/NLCISBNPlugin](https://github.com/DoiiarX/NLCISBNPlugin) 
(Apache License 2.0). 
In accordance with the Apache 2.0 license, all original copyright notices are preserved, 
and modifications are documented. 
As a derivative work, this module is distributed under the GPLv3 license.