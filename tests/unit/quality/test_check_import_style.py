from quality.check_import_style import import_style_errors


def test_single_line_from_import_ok():
    source = "from foo.bar import baz, qux\n"
    assert import_style_errors(source, "ok.py") == []


def test_parenthesized_import_fails():
    source = "from foo import (bar, baz)\n"
    errors = import_style_errors(source, "bad.py")
    assert errors
    assert "parentheses" in errors[0]


def test_multiline_import_fails():
    source = "from foo import (\n    bar,\n    baz,\n)\n"
    errors = import_style_errors(source, "wrap.py")
    assert errors
    assert "single line" in errors[0]
