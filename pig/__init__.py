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


from graphviz import Digraph


class ImportFinder(ast.NodeVisitor):
    def __init__(self, name):
        super(ImportFinder, self).__init__()
        self._graph = Digraph(name=name)
        self._graph.node(name, label=name)
        self._root = name

    @property
    def graph(self):
        logging.debug(self._graph.source)
        return self._graph

    def visit_alias(self, node):
        for field, value in ast.iter_fields(node):
            logging.debug("\t%s=%s", field, value)

    def visit_Import(self, node):
        for name in node.names:
            self._graph.edge(self._root, name.name)
        # for field, value in ast.iter_fields(node):
        #     if isinstance(value, ast.AST):
        #         logging.debug("\t%s", field)
        #         self.visit(value)
        #     elif isinstance(value, list):
        #         logging.debug("\t%s=[", field)
        #         for item in value:
        #             if isinstance(item, ast.AST):
        #                 self.visit(item)
        #             else:
        #                 logging.debug("\t\t%s,", item)
        #         logging.debug("\t]")
        #     else:
        #         logging.debug("\t%s=%s", field, value)

    def visit_ImportFrom(self, node):
        self._graph.edge(self._root, node.module)
        # for field, value in ast.iter_fields(node):
        #     if isinstance(value, ast.AST):
        #         logging.debug("\t%s", field)
        #         self.visit(value)
        #     elif isinstance(value, list):
        #         logging.debug("\t%s[", field)
        #         for item in value:
        #             if isinstance(item, ast.AST):
        #                 self.visit(item)
        #             else:
        #                 logging.debug("\t\t%s", item)
        #         logging.debug("\t]")
        #     else:
        #         logging.debug("\t%s=%s", field, value)


def generate_import_graph(code, filename):
    """
    """
    node = ast.parse(code, filename=filename)
    logging.debug(ast.dump(node))
    walker = ImportFinder(filename)
    walker.visit(node)
    return walker.graph


def main():
    parser = argparse.ArgumentParser(description="Create an import graph for the given Python code.")
    parser.add_argument("-v", "--verbose", help="Toggle verbose mode", action="store_true")
    parser.add_argument("script", type=argparse.FileType('r'), help="Script to generate the import graph for")
    options = parser.parse_args()

    log_level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(level=log_level, stream=sys.stdout)
    logging.info("Generating import graph for %s", options.script.name)

    try:
        generate_import_graph(options.script.read(), filename=options.script.name)
    finally:
        if options.script not in (sys.stdin, sys.stdout, sys.stderr):
            options.script.close()


if __name__ == "__main__":
    main()
