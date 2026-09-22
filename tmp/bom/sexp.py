"""Minimal S-expression reader for KiCad files (British English identifiers)."""


def parse(text):
    """Return the nested list representation of a KiCad S-expression file."""
    pos = 0
    length = len(text)
    stack = []
    current = []
    while pos < length:
        char = text[pos]
        if char == "(":
            stack.append(current)
            current = []
            pos += 1
        elif char == ")":
            finished = current
            current = stack.pop()
            current.append(finished)
            pos += 1
        elif char == '"':
            pos += 1
            chunks = []
            while text[pos] != '"':
                if text[pos] == "\\":
                    chunks.append(text[pos + 1])
                    pos += 2
                else:
                    chunks.append(text[pos])
                    pos += 1
            current.append("".join(chunks))
            pos += 1
        elif char.isspace():
            pos += 1
        else:
            start = pos
            while pos < length and not text[pos].isspace() and text[pos] not in '()"':
                pos += 1
            current.append(Symbol(text[start:pos]))
    return current[0] if len(current) == 1 else current


class Symbol(str):
    """Bare atom, distinguishable from a quoted string."""

    __slots__ = ()


def walk(node, tag):
    """Yield every sub-list whose head atom equals `tag`, at any depth."""
    if isinstance(node, list):
        if node and isinstance(node[0], Symbol) and node[0] == tag:
            yield node
        for child in node:
            yield from walk(child, tag)


def children(node, tag):
    """Yield direct child lists whose head atom equals `tag`."""
    for child in node:
        if isinstance(child, list) and child and isinstance(child[0], Symbol) and child[0] == tag:
            yield child
