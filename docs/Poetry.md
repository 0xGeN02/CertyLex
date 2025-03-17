# CertyLex Project

## Overview

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging. Poetry simplifies the process of managing Python projects and ensures a consistent environment.

## Prerequisites

- Python 3.11 (for this repo)
- Poetry installed on your system. If not installed, follow the [Poetry installation guide](https://python-poetry.org/docs/#installation).

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Activate the virtual environment:

   ```bash
   poetry shell
   ```

## Main Commands

- **Run the application**:

  ```bash
  poetry run python <main_script>.py
  ```

  Replace `<main_script>` with the name of the main Python file.

- **Add a new dependency**:

  ```bash
  poetry add <package-name>
  ```

- **Run tests**:

  ```bash
  poetry run pytest
  ```

- **Check for outdated dependencies**:

  ```bash
  poetry show --outdated
  ```

## Documentation

For more details about Poetry, refer to the [official documentation](https://python-poetry.org/docs/).
