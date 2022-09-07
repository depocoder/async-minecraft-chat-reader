# async-minecraft-chat-reader

Chat client for minecraft server

![async-minecraft-chat-reader functional](https://s7.gifyu.com/images/Peek-2022-03-10-11-01.gif)

## Features
- Registraition
  - save token after registraition
- Auth by token
- Send message
- Read and store messages


## How to start(Linux)

Install dependency for tkinter (Ubuntu/Debian)
```shell
sudo apt-get install python3-tk
```

Install dependency for tkinter Arch/Monjaro)
```shell
sudo pacman -S tk
```


Clone the project
```shell
pip install git+https://github.com/depocoder/async-minecraft-chat-reader.git
```

Run chat
```bash
minecraft_chat
```

## For developer

Install dependencies
```shell
pip install poetry
poetry install
```

Commit hook [read more](https://pre-commit.com/)
```shell
pre-commit install
```

```shell
poetry run python3 main.py
```
