import pytest

import pig


MULTIPLE_IMPORTS = """digraph unittest {
\tunittest [label=unittest]
\ttestdata -> indirectdep
\tunittest -> sys [color=blue style=solid]
\tunittest -> testdata [color=blue style=solid]
\tunittest -> indirectdep [style=dotted]
}"""

MULTIPLE_IMPORT_FROMS = """digraph unittest {
\tunittest [label=unittest]
\ttestdata -> indirectdep
\tunittest -> sys [color=blue style=solid]
\tunittest -> testdata [color=blue style=solid]
\tunittest -> indirectdep [style=dotted]
}"""

MIXED_IMPORTS = """digraph unittest {
\tunittest [label=unittest]
\ttestdata -> indirectdep
\tunittest -> sys [color=blue style=solid]
\tunittest -> testdata [color=blue style=solid]
\tunittest -> indirectdep [style=dotted]
}"""


@pytest.mark.parametrize(
    "test_input,expected", [
        pytest.param(
            "", "digraph unittest {\n\tunittest [label=unittest]\n}", id="no imports"
        ),
        pytest.param(
            "import sys",
            "digraph unittest {\n\tunittest [label=unittest]\n\tunittest -> sys [color=blue style=solid]\n}",
            id="simple import"
        ),
        pytest.param(
            "from sys import argv",
            "digraph unittest {\n\tunittest [label=unittest]\n\tunittest -> sys [color=blue style=solid]\n}",
            id="simple import from"
        ),
        pytest.param(
            "import testdata; import sys",
            MULTIPLE_IMPORTS,
            id="multiple imports"
        ),
        pytest.param(
            "from sys import version; from testdata import noop",
            MULTIPLE_IMPORT_FROMS,
            id="multiple import froms"
        ),
        pytest.param(
            "from sys import argv; import testdata",
            MIXED_IMPORTS,
            id="mixed imports"
        ),
    ]
)
def test_import_graph_generation(test_input, expected):
    x = pig.generate_import_graph(test_input, "unittest")
    assert x.source == expected
