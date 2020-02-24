import pytest

import pig


MULTIPLE_IMPORTS = """digraph unittest {
\tunittest [label=unittest]
\tunittest -> os
\tunittest -> sys
\tunittest -> tempfile
}"""

MULTIPLE_IMPORT_FROMS = """digraph unittest {
\tunittest [label=unittest]
\tunittest -> os
\tunittest -> sys
\tunittest -> tempfile
}"""

MIXED_IMPORTS = """digraph unittest {
\tunittest [label=unittest]
\tunittest -> logging
\tunittest -> os
\tunittest -> sys
\tunittest -> tempfile
}"""


@pytest.mark.parametrize(
    "test_input,expected", [
        pytest.param(
            "", "digraph unittest {\n\tunittest [label=unittest]\n}", id="no imports"
        ),
        pytest.param(
            "import sys",
            "digraph unittest {\n\tunittest [label=unittest]\n\tunittest -> sys\n}",
            id="simple import"
        ),
        pytest.param(
            "from sys import argv",
            "digraph unittest {\n\tunittest [label=unittest]\n\tunittest -> sys\n}",
            id="simple import from"
        ),
        pytest.param(
            "import os; import sys; import tempfile",
            MULTIPLE_IMPORTS,
            id="multiple imports"
        ),
        pytest.param(
            "from os import path; from sys import version; from tempfile import mkstemp",
            MULTIPLE_IMPORT_FROMS,
            id="multiple import froms"
        ),
        pytest.param(
            "import logging; from os import path; import sys; from tempfile import mkstemp",
            MIXED_IMPORTS,
            id="mixed imports"
        ),
    ]
)
def test_import_graph_generation(test_input, expected):
    x = pig.generate_import_graph(test_input, "unittest")
    assert x.source == expected
