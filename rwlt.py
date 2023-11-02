#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Rewrite selected LaTeX environments.

Only supports longtable for now."""

import sys
import typing
from typing import Callable

import regex

import pylatexenc
import pylatexenc.latexwalker
from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexWalker,
    LatexNode,
)


def find_nodes(
    node_list: list[LatexNode], name_callback: Callable[[str], bool]
) -> list[LatexNode]:
    """Find all nodes in the given node list that match the given name callback."""
    longtable_nodes: list[pylatexenc.latexwalker.LatexNode] = []
    for node in node_list:
        if isinstance(node, LatexEnvironmentNode) and name_callback(node.envname):
            longtable_nodes.append(node)
        elif isinstance(node, LatexMacroNode) and name_callback(node.macroname):
            longtable_nodes.extend([node])
        elif isinstance(node, LatexGroupNode):
            longtable_nodes.extend(find_nodes(node.nodelist, name_callback))
        elif isinstance(node, LatexEnvironmentNode):
            longtable_nodes.extend(find_nodes(node.nodelist, name_callback))
        elif hasattr(node, "nodelist"):
            node_list = getattr(node, "nodelist")
            longtable_nodes.extend(find_nodes(node_list, name_callback))
    return longtable_nodes


def reload_latex(walker: LatexWalker, name_callback):
    """Reload the latex document."""
    (nodes, _, _) = walker.get_latex_nodes(pos=0)
    nodes: typing.List[pylatexenc.latexwalker.LatexNode] = nodes
    matched = find_nodes(nodes, name_callback)
    return (nodes, matched)


def rewrite_latex(nodelist_, output):
    """Rewrite the latex document."""
    newbashman = pylatexenc.latexwalker.nodelist_to_latex(nodelist_)
    with open(output, "w+", encoding="utf8") as latex:
        return latex.write(newbashman)


def rewrite_longtables(longtables_) -> list[str]:
    """Rewrite the longtables.
    Side effect: Changes the node list in place.

    Changes each longtable such that the last column is 5 inches wide.
    """
    changed = []
    for node in longtables_:
        if isinstance(node, LatexEnvironmentNode):
            chars = regex.sub(
                "(?<one>.*)l", r"\g<one>p{5in}", node.nodelist[1].nodelist[2].chars
            )
            node.nodelist[1].nodelist[2].chars = chars
            changed.append(chars)
    return changed


rewrite_funcs = {"longtable": rewrite_longtables}


def main():
    """Main function."""
    assert len(sys.argv) == 4, (
        "Usage: python rwlt.py <filename> <output> <name>"
        + "Example: python rwlt.py test.tex test2.tex longtable"
    )
    # pylint: disable=unbalanced-tuple-unpacking
    (_, filename, output, name) = sys.argv

    def name_cb(name_) -> Callable[[str], bool]:
        return name_ == name

    with open(filename, "r", encoding="utf8") as input_file:
        latex = input_file.read()
    walker = LatexWalker(latex)
    (nodelist, filtered) = reload_latex(walker, name_cb)
    if not name in rewrite_funcs:
        raise ValueError("Unknown name: " + name)
    rewrite_funcs[name](filtered)
    rewrite_latex(nodelist, output)


if __name__ == "__main__":
    main()
