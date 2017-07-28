#!/usr/bin/env python3

import sys

ALIGN = "$"

text = []
aligns = [] # Contiguous lines containing the same align code
            # E.g.: If lines 3 to 7 (incl.) contained align code "B"
            # there would be an entry like:
            # {code="b", first=3, last=7, pos=[...(len=5)]}
rels = []

for l, line in enumerate(sys.stdin):
    blocs = line[:-1].split(ALIGN)
    text.append([blocs[0]] + [bloc[1:] for bloc in blocs[1:]])
    lastn = len(line) - 1
    pos = 0
    linealigns = []
    newaligns = []
    for n, bloc in enumerate(blocs):
        if n == 0:
            pos += len(bloc)
            continue
        assert len(bloc) > 0, "ALIGN must be followed by an aligncode"
        code = bloc[0]
        def goodalign(align):
            return align["code"] == code \
               and align["last"] == l - 1
        for align in aligns:
            if goodalign(align):
                align["last"] = l
                align["pos"].append(pos)
                align["prev"].append((l, n-1))
                linealigns.append(align)
                break
        else:
            align = {
                "code"  : code,
                "first" : l,
                "last"  : l,
                "pos"   : [pos],
                "prev"  : [(l, n-1)]}
            aligns.append(align)
            linealigns.append(align)
            newaligns.append(align)
        pos += len(bloc) - 1
    for newalign in newaligns:
        before = True
        for linealign in linealigns:
            if linealign == newalign:
                before = False
                continue
            if before:
                if linealign not in newaligns:
                    rels.append((linealign, newalign))
            else:
                rels.append((newalign, linealign))

ordered_aligns = []
while len(aligns) > 0:
    for n, align in enumerate(aligns):
        for rel in rels:
            if align == rel[1]:
                break
        else:
            ordered_aligns.append(align)
            del aligns[n]
            for m, rel in reversed(list(enumerate(rels))):
                if rel[0] == align:
                    del rels[m]
            break
aligns = ordered_aligns

for align in aligns:
    maxpos = max(align["pos"])
    for n in range(align["last"] - align["first"] + 1):
        pos = align["pos"][n]
        if pos == maxpos:
            continue
        shift = maxpos - pos
        text[align["prev"][n][0]] \
            [align["prev"][n][1]] += " " * shift
        line = n + align["first"]
        for other in aligns:
            if other["first"] <= line <= other["last"]:
                other["pos"][line-other["first"]] += shift

for blocs in text:
    print("".join(blocs))
