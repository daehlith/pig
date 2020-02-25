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
import imp
import logging
import os
import sys


from graphviz import Digraph


class ImportTracer(ast.NodeVisitor):
    def __init__(self, name):
        super(ImportTracer, self).__init__()
        self._graph = Digraph(name=name)
        self._graph.node(name, label=name)
        self._root = name
        self._current = self._root
        self._visited_modules = {name}
        self._direct_dependencies = set()
        self._indirect_dependencies = set()
        self._cached = False
        self._edges = set()

    @property
    def graph(self):
        if not self._cached:
            for dep in sorted(self._direct_dependencies):
                self._graph.edge(self._root, dep, style="solid", color="blue")
            for dep in sorted(self._indirect_dependencies):
                self._graph.edge(self._root, dep, style="dotted")
            self._cached = True
        logging.debug(self._graph.source)
        return self._graph

    def visit_alias(self, node):
        self._log_debug(node)

    def _insert_edge(self, from_node, to_node):
        if (from_node, to_node) in self._edges:
            return
        self._cached = False
        if from_node != self._root:
            if to_node not in self._direct_dependencies:
                self._indirect_dependencies.add(to_node)
            self._graph.edge(from_node, to_node)
        else:
            self._indirect_dependencies.discard(to_node)
            self._direct_dependencies.add(to_node)

    def visit_Import(self, node):
        self._log_debug(node)
        for name in node.names:
            self._insert_edge(self._current, name.name)
            self._recurse_imports(name.name)

    def _recurse_imports(self, name):
        if name in self._visited_modules:
            return
        else:
            _previous = self._current
            self._current = name
            self._visited_modules.add(name)
            fp = None
            try:
                fp, pathname, description = imp.find_module(name)
                logging.debug("imp.find_module(%s) returned: %s %s", name, pathname, description)
                if description[2] in (imp.C_BUILTIN, imp.C_EXTENSION, imp.PY_FROZEN):
                    return
                elif description[2] == imp.PKG_DIRECTORY:
                    fp = open(os.path.join(pathname, "__init__.py"), "r")
                code = fp.read()
                imported_node = ast.parse(code, name)
                logging.debug(ast.dump(imported_node))
                self.visit(imported_node)
            except ImportError:
                logging.warn("Failed importing %s, analysis may be incomplete", name)
            except Exception:
                logging.exception("Unhandled exception while visiting module %s", name)
            finally:
                if fp is not None:
                    fp.close()
                self._current = _previous

    def _log_debug(self, node):
        if logging.getLogger().level != logging.DEBUG:
            return
        self._indent_level = getattr(self, "_indent_level", 0) + 1
        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                logging.debug("%s%s", "\t" * self._indent_level, field)
                self.visit(value)
            elif isinstance(value, list):
                logging.debug("%s%s=[", "\t" * self._indent_level, field)
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
                    else:
                        logging.debug("%s%s", "\t" * (1+self._indent_level), item)
                logging.debug("%s]", "\t" * self._indent_level)
            else:
                logging.debug("%s%s=%s", "\t" * self._indent_level, field, value)
        self._indent_level = self._indent_level - 1

    def visit_ImportFrom(self, node):
        self._log_debug(node)
        if node.module is None:
            logging.warn("Empty node.module for %s", self._current)
            return
        self._insert_edge(self._current, node.module)
        self._recurse_imports(node.module)


def generate_import_graph(code, filename):
    """
    """
    node = ast.parse(code, filename=filename)
    logging.debug(ast.dump(node))
    walker = ImportTracer(filename)
    walker.visit(node)
    return walker.graph


def main():
    parser = argparse.ArgumentParser(description="Create an import graph for the given Python code.")
    parser.add_argument("-v", "--verbose", help="Toggle verbose mode", action="store_true")
    parser.add_argument(
        "-o", "--outfile", help="Where to write the dotfile to", default="out.dot", type=argparse.FileType('w')
    )
    parser.add_argument("script", type=argparse.FileType('r'), help="Script to generate the import graph for")
    options = parser.parse_args()

    log_level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(level=log_level, stream=sys.stdout)
    logging.info("Generating import graph for %s", options.script.name)

    try:
        graph = generate_import_graph(options.script.read(), filename=options.script.name)
        options.outfile.write(graph.source)
    finally:
        for fp in (options.script, options.outfile):
            if fp not in (sys.stdin, sys.stdout, sys.stderr):
                try:
                    fp.close()
                except Exception:
                    logging.exception("Failed closing %s", fp)



if __name__ == "__main__":
    main()
