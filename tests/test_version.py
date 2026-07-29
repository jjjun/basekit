import re

import basekit


def test_version_is_non_empty_pep_440_style_string():
    assert isinstance(basekit.__version__, str)
    assert re.fullmatch(
        r"\d+\.\d+\.\d+"
        r"(?:(?:a|b|rc)\d+)?"
        r"(?:\.post\d+)?"
        r"(?:\.dev\d+)?"
        r"(?:\+[a-z0-9]+(?:[.-][a-z0-9]+)*)?",
        basekit.__version__,
    )
