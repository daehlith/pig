"""
pig - python import graph
> A utility to create the import graph of a given Python project

Some caveats to watch out for:
  - "lazy imports"         --> list as conditional dependencies
  - conditional imports    --> decide if this should be a warning or be listed as a conditional dependencies
  - __import__ / importlib --> warning if called with a non-constant expression
"""
import argparse
import ast
import logging
import sys


class ImportFinder(ast.NodeVisitor):
    def visit_Import(self, node):
        for name in node.names:
            logging.debug("Found Import for module: %s as %s", name.name, name.asname)

    def visit_ImportFrom(self, node):
        logging.debug("Visit ImportFrom: %s %s %s", node.level, node.module, node.names)
        for name in node.names:
            logging.debug("Found Import for module: %s.%s as %s", node.module, name.name, name.asname)


def main():
    parser = argparse.ArgumentParser(description="Create an import graph for the given Python code.")
    parser.add_argument("-v", "--verbose", help="Toggle verbose mode", action="store_true")
    parser.add_argument("script", type=argparse.FileType('r'), help="Script to generate the import graph for")
    options = parser.parse_args()

    log_level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(level=log_level, stream=sys.stdout)
    logging.info("Generating import graph for %s", options.script.name)

    try:
        node = ast.parse(options.script.read(), filename=options.script.name)
        logging.debug(ast.dump(node))
        walker = ImportFinder()
        walker.visit(node)
    finally:
        options.script.close()


if __name__ == "__main__":
    main()