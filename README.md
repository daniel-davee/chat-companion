# CLI Companion

CLI Companion is a command line tool that you can use to ask questions and get responses back from a virtual companion. You can also review previous questions and responses.

## Installation

You can install CLI Companion using [PyInstaller](https://www.pyinstaller.org/).

To install using PyInstaller, first clone this repository. Then, in the repository directory, run the following command:

```
pyinstaller -D companion.py
```

This will create a standalone executable in the `dist` directory.

## Usage

### Talk

To ask a question, use the `talk` subcommand. For example:

```
companion talk "What is your name?"
```

### Review

To review previous questions and responses, use the `review` subcommand. This will bring up a list of previous questions. You can then select a question to view the response.