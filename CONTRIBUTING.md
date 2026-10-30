# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Bug Reports

When [reporting a bug][0] please include:

*   Your operating system name and version.
*   Any details about your local setup that might be helpful in
    troubleshooting.
*   Detailed steps to reproduce the bug.

## Documentation Improvements

scratchrelaxtv could always use more documentation, whether as part of the official
scratchrelaxtv docs, in docstrings, or even on the web in blog posts, articles, and
such. The official documentation is maintained within this project in
docstrings and the README. Contributions are
welcome, and are made the same way as any other code.

## Feature Requests and Feedback

The best way to send feedback is to [file an issue][0] on GitHub.

If you are proposing a feature:

*   Explain in detail how it would work.
*   Keep the scope as narrow as possible, to make it easier to implement.
*   Remember that this is a community-driven, open-source project, and that
    code contributions are welcome. :)

## Development Guide

To set up scratchrelaxtv for local development:

1.  Fork [scratchrelaxtv](https://github.com/YakDriver/scratchrelaxtv) (look for the
    "Fork" button).

2.  Clone your fork locally:

    ```shell
    git clone https://github.com/your_name_here/scratchrelaxtv.git && cd scratchrelaxtv
    ```

3.  Create a branch for local development:

    ```shell
    git checkout -b name-of-your-bugfix-or-feature
    ```

4.  Now you can make your changes locally.

5.  Install in a virtual environment with development tools, then run the
    linters, type checker, and tests:

    ```shell
    python -m venv .venv && . .venv/bin/activate
    python -m pip install -e ".[dev]"
    ruff check . && ruff format --check . && mypy scratchrelaxtv && pytest
    ```

6.  Commit your changes and push your branch to GitHub:

    ```shell
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

7.  Submit a pull request through the GitHub website.

## Pull Request Guidelines

If you need some code review or feedback while you are developing the code just
open the pull request.

For pull request acceptance, you should:

1.  Make sure GitHub Actions CI passes (Linux, macOS, and Windows).
2.  Update documentation whenever making changes to the API or functionality.
3.  Add a note to `CHANGELOG.md` about the changes. Include a link to the
    pull request.

[0]: https://github.com/YakDriver/scratchrelaxtv/issues
