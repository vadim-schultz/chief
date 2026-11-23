"""README and docs checks: required sections, ASD-STE100 prose and CLI coverage."""

import re
from pathlib import Path

from typer.main import get_group

from chief.cli.app import app

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
DOCS = tuple(sorted((REPO_ROOT / "docs").glob("*.md")))

REQUIRED_HEADINGS = (
    "## Installation",
    "## Supported IDEs",
    "## Usage",
    "## Normal workflow",
    "## Security",
    "## Contributing",
)
PLACEHOLDERS = ("A few more paragraphs", "TODO")
_FENCE = re.compile(r"^```.*?^```[^\n]*$", re.M | re.S)
_HEADING = re.compile(r"^## .+$", re.M)
_NUMBERED_ITEM = re.compile(r"^\s*\d+\.\s+")
_LIST_MARKER = re.compile(r"^\s*(?:\d+\.|[-*])\s+")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
MAX_PROCEDURE_WORDS = 20
IMPERATIVE_VERBS = frozenset(
    "add check choose confirm convert copy create delete export give install keep open "
    "print read remove restart review run select set show start stop update use wait write".split(),
)


def _read(path: Path) -> str:
    """Return the text of ``path``."""
    return path.read_text(encoding="utf-8")


def _outside_code(text: str) -> str:
    """Return ``text`` with every fenced code block blanked, so that its lines are prose or headings."""
    return _FENCE.sub("", text)


def _section_pattern(heading: str) -> re.Pattern[str]:
    """Return the pattern of the ``##`` section named ``heading``, up to the next ``## `` heading."""
    return re.compile(rf"^{re.escape(heading)}\n.*?(?=^## |\Z)", re.M | re.S)


def _without_security(text: str) -> str:
    """Return ``text`` with the ``## Security`` section removed, because its TBD items stay by decision O3."""
    return _section_pattern("## Security").sub("", _outside_code(text))


def test_readme_has_the_required_sections() -> None:
    """The README holds every heading that the docs pages and the workflow need."""
    headings = set(_HEADING.findall(_outside_code(_read(README))))
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in headings]
    assert not missing, f"README lacks headings: {missing}"


def test_readme_has_no_placeholder_text() -> None:
    """The README keeps template text out of every section except ``## Security``."""
    text = _without_security(_read(README))
    found = [marker for marker in PLACEHOLDERS if marker in text]
    assert not found, f"README still holds placeholder text: {found}"


def _pages() -> tuple[Path, ...]:
    """Return the README and every docs page, the prose that ASD-STE100 governs."""
    return (README, *DOCS)


def _prose_lines(text: str) -> list[str]:
    """Return the lines of ``text`` outside code blocks that are neither headings nor table rows."""
    return [line for line in _outside_code(text).splitlines() if not line.lstrip().startswith(("#", "|"))]


def _starts_with_imperative(sentence: str) -> bool:
    """Return whether the first word of ``sentence`` is an imperative verb of the procedure vocabulary."""
    words = sentence.split()
    return bool(words) and words[0].lower().strip("*_`[]()\"'") in IMPERATIVE_VERBS


def _line_procedure_sentences(line: str) -> list[str]:
    """Return the procedure sentences of ``line``: all sentences of a numbered step, or those opening with a verb."""
    numbered = _NUMBERED_ITEM.match(line) is not None
    body = _LIST_MARKER.sub("", line)
    return [sentence for sentence in _SENTENCE_END.split(body) if numbered or _starts_with_imperative(sentence)]


def _procedure_sentences(text: str) -> list[str]:
    """Return the procedure sentences of every prose line of ``text``."""
    return [sentence for line in _prose_lines(text) for sentence in _line_procedure_sentences(line)]


def test_procedure_steps_are_at_most_twenty_words() -> None:
    """Every procedure sentence in the README and the docs pages has 20 words or fewer."""
    too_long = [
        sentence
        for path in _pages()
        for sentence in _procedure_sentences(_read(path))
        if len(sentence.split()) > MAX_PROCEDURE_WORDS
    ]
    assert not too_long, f"procedure sentences over {MAX_PROCEDURE_WORDS} words: {too_long}"


def test_prose_has_no_semicolons() -> None:
    """No sentence outside a code block of the README or the docs pages contains a semicolon."""
    with_semicolon = [path.name for path in _pages() if ";" in _outside_code(_read(path))]
    assert not with_semicolon, f"semicolons outside code blocks in: {with_semicolon}"


def _raw_section(text: str, heading: str) -> str:
    """Return the ``##`` section named ``heading`` with its code blocks, or an empty string when it is absent."""
    match = _section_pattern(heading).search(text)
    return match.group(0) if match else ""


def _section(text: str, heading: str) -> str:
    """Return the ``##`` section named ``heading``, heading included, or an empty string when it is absent."""
    return _raw_section(_outside_code(text), heading)


def _cli_option_names() -> set[str]:
    """Return every option of the group and of each command, read from the registered Typer app."""
    root = get_group(app)
    commands = [root, *root.commands.values()]
    return {opt for command in commands for param in command.params for opt in param.opts}


def test_readme_names_every_cli_command() -> None:
    """The README names each registered command and option, and the ``--target all`` form."""
    text = _read(README)
    missing_commands = [name for name in get_group(app).commands if f"chief {name}" not in text]
    missing_options = [
        opt for opt in sorted(_cli_option_names()) if not re.search(rf"(?<![\w-]){re.escape(opt)}(?![\w-])", text)
    ]
    assert not missing_commands, f"README does not name commands: {missing_commands}"
    assert not missing_options, f"README does not name options: {missing_options}"
    assert "--target all" in text, "README does not name --target all"


def test_readme_states_index_requirement() -> None:
    """The install section names ``UV_DEFAULT_INDEX``, because ``uv tool install`` does not read the project index."""
    installation = _section(_read(README), "## Installation")
    assert "UV_DEFAULT_INDEX" in installation, "install section does not name UV_DEFAULT_INDEX"


INSTALL_COMMAND = re.compile(r"uv tool install git\+https://github\.com/vadim-schultz/chief@v\d+\.\d+\.\d+")
REMOVED_TERMS = ("mcp-snippet", "package index")
MCP_TERM = re.compile(r"\bmcp\b", re.IGNORECASE)


def test_readme_names_git_url_install() -> None:
    """The install section installs the command from the tagged git URL of the repository."""
    installation = _raw_section(_read(README), "## Installation")
    assert INSTALL_COMMAND.search(installation), "install section does not install from the tagged git URL"


def test_readme_has_no_mcp_or_package_index() -> None:
    """The README names no removed command, no package index and no MCP term."""
    text = _read(README)
    found = [term for term in REMOVED_TERMS if term in text.lower()]
    assert not found, f"README names removed terms: {found}"
    assert not MCP_TERM.search(text), "README names an MCP term"
