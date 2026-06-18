#!/usr/bin/env python3
import json
import re
import sys

filepath = "/var/folders/8t/kvx58rxs2zjdq84nffdt6st40000gp/T/claude-hostloop-plugins/45b3545f2d81b8cc/projects/-Users-RickyLiu-Library-Application-Support-Claude-local-agent-mode-sessions-0309329f-4e53-4f66-adc5-3378e20f2322-69fd3102-bf77-4c20-bc7a-ce22397d6309-local-ed093a0b-dfb8-4a6e-97c6-df58db202db4-output-eko9ak/6f0ef7b7-0899-4a3c-91e4-9f68ad54f806/tool-results/mcp-77fe3d40-0fd4-4495-9461-39958487c4d8-get_metadata-1781647039120.txt"

print("Loading file...", file=sys.stderr)
with open(filepath, 'r') as f:
    data = json.load(f)

# Concatenate all text fields
xml_text = ""
for entry in data:
    if isinstance(entry, dict) and 'text' in entry:
        xml_text += entry['text']

print(f"XML length: {len(xml_text)} chars", file=sys.stderr)

# Use regex to find nodes - parse iteratively
# Find node 2452:4490 and its direct children
# XML uses id="..." and name="..." attributes on nodes

# Strategy: find the opening tag for 2452:4490, then find all direct child tags

def find_node_and_children(xml, node_id):
    """Find the node with given id and return its direct children's id+name."""
    # Find the opening tag
    # Tags look like: <FRAME id="2452:4490" name="..." ...> or self-closing
    # Search for the tag containing this id
    pattern = r'<(\w+)\s[^>]*id="' + re.escape(node_id) + r'"[^>]*>'
    m = re.search(pattern, xml)
    if not m:
        print(f"Node {node_id} not found", file=sys.stderr)
        return []

    tag_type = m.group(1)
    start = m.end()
    print(f"Found node {node_id} as <{tag_type}> at position {m.start()}", file=sys.stderr)

    # Find the closing tag - need to handle nesting
    # Count depth
    open_pat = re.compile(r'<' + re.escape(tag_type) + r'[\s>]')
    close_pat = re.compile(r'</' + re.escape(tag_type) + r'>')

    depth = 1
    pos = start
    end = -1
    while pos < len(xml) and depth > 0:
        next_open = open_pat.search(xml, pos)
        next_close = close_pat.search(xml, pos)
        if next_close is None:
            break
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            if depth == 0:
                end = next_close.start()
            pos = next_close.end()

    if end == -1:
        print(f"Could not find closing tag for {node_id}", file=sys.stderr)
        inner = xml[start:start+5000]  # take a chunk
    else:
        inner = xml[start:end]

    print(f"Inner content length: {len(inner)}", file=sys.stderr)

    # Find direct children - any opening tag at depth 1
    # We need to parse direct children only (not grandchildren)
    children = []
    child_pattern = re.compile(r'<(\w+)\s([^>]*)>')
    i = 0
    while i < len(inner):
        cm = child_pattern.search(inner, i)
        if not cm:
            break
        child_tag = cm.group(1)
        child_attrs = cm.group(2)

        # Extract id and name
        id_m = re.search(r'id="([^"]*)"', child_attrs)
        name_m = re.search(r'name="([^"]*)"', child_attrs)
        child_id = id_m.group(1) if id_m else "(no id)"
        child_name = name_m.group(1) if name_m else "(no name)"

        children.append((child_tag, child_id, child_name))

        # Skip past this child's entire subtree to get only direct children
        # Check if self-closing
        if cm.group(0).endswith('/>') or inner[cm.end()-2:cm.end()] == '/>':
            i = cm.end()
        else:
            # Find matching close tag
            o_pat = re.compile(r'<' + re.escape(child_tag) + r'[\s>]')
            c_pat = re.compile(r'</' + re.escape(child_tag) + r'>')
            d = 1
            p = cm.end()
            while p < len(inner) and d > 0:
                no = o_pat.search(inner, p)
                nc = c_pat.search(inner, p)
                if nc is None:
                    i = p + 1
                    break
                if no and no.start() < nc.start():
                    d += 1
                    p = no.end()
                else:
                    d -= 1
                    p = nc.end()
                    if d == 0:
                        i = p
            else:
                if d > 0:
                    i = cm.end()

    return children

# Find node 2452:4490 children
print("\n=== Direct children of node 2452:4490 ===")
children = find_node_and_children(xml_text, "2452:4490")
for tag, cid, cname in children:
    print(f"  [{tag}] id={cid!r}  name={cname!r}")

print(f"\nTotal children: {len(children)}")

# Find top-level FRAME nodes under page 2006:1223
print("\n=== Direct children of page node 2006:1223 ===")
page_children = find_node_and_children(xml_text, "2006:1223")
for tag, cid, cname in page_children:
    print(f"  [{tag}] id={cid!r}  name={cname!r}")

print(f"\nTotal page children: {len(page_children)}")
