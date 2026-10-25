"""Makes tests/cases.json: how Python's csv module reads and writes
thousands of texts, for the Tessel tests to compare against.

Run from the library's folder:  python3 tools/oracle/oracle.py

Author: Alexius Academia
Date: 2026-10-25
"""

import csv
import io
import json
import random

random.seed(20261025)

# How each case is read: separator, quote, lenient (Python's strict=False),
# skipSpaces (Python's skipinitialspace).
DIALECTS = [
    (",", '"', False, False),
    (",", '"', True, False),
    (";", '"', False, False),
    ("\t", '"', False, False),
    ("|", "'", False, False),
    (",", '"', False, True),
    (",", '"', True, True),
]

HAND = [
    "", "a", "a,b,c", "a,b,c\n", "a,b,c\r\n", "a,b,c\r", "a\nb\n", "a\r\nb\r\n", "a\rb\r",
    "\n", "\n\n", "\r\n\r\n", "a\n\nb", ",", ",,", "a,", ",a", "a,\n", "\"\"", "\"\",\"\"",
    "\"a,b\",c", "\"a\nb\",c", "\"a\r\nb\",c\r\n", "\"x\"\"y\"", "\"\"\"\"", "\"\"\"\"\"\"",
    "\"abc", "a,\"bc", "\"ab\"c", "\"ab\"c,d", "\"ab\" ,c", "ab\"c", "a\"b\"c", "\"a\"\"",
    " a, b , c ", "a, \"b,c\"", "a,  \"b\"", "\"a\"\n\"b\"", "\"a\"\r", "\"a\"\r\n",
    "é,😀\nñ,中文", "\"é\n😀\",x", "a;b;c", "a\tb\tc", "a|b|c", "'a|b'|c", "'it''s'|x",
    "name,age\n\"Smith, J\",42\n", "1,2,3\n4,5\n6\n", "\"\"\n\"\"", "a,\"\"\n",
    "\"a\nb", "x,\"\n", "\"\r", "\"\n\"", "a\r\r\nb",
]

ALPHABET = ["a", "b", "1", ",", ";", "\t", "|", "\"", "'", " ", "\n", "\r", "é", "😀"]
WEIGHTS = [10, 6, 4, 6, 3, 2, 2, 6, 2, 3, 4, 2, 1, 1]


def read(text, sep, quote, lenient, skip):
    """Python's rows, or the kind of error."""
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=sep, quotechar=quote,
                        strict=not lenient, skipinitialspace=skip)
    try:
        return {"ok": True, "rows": [row for row in reader], "error": ""}
    except csv.Error as e:
        message = str(e)
        if "unexpected end of data" in message:
            kind = "never closed"
        elif "expected after" in message:
            kind = "after a closing quote"
        else:
            raise
        return {"ok": False, "rows": [], "error": kind}


def write(rows, sep, quote, ending, quote_all):
    out = io.StringIO(newline="")
    w = csv.writer(out, delimiter=sep, quotechar=quote, lineterminator=ending,
                   quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL)
    for row in rows:
        w.writerow(row)
    return out.getvalue()


def main():
    reads = []
    for text in HAND:
        for (sep, quote, lenient, skip) in DIALECTS:
            case = {"text": text, "separator": sep, "quote": quote, "lenient": lenient, "skipSpaces": skip}
            case.update(read(text, sep, quote, lenient, skip))
            reads.append(case)
    for _ in range(6000):
        n = random.randint(0, 24)
        text = "".join(random.choices(ALPHABET, WEIGHTS, k=n))
        sep, quote, lenient, skip = random.choice(DIALECTS)
        case = {"text": text, "separator": sep, "quote": quote, "lenient": lenient, "skipSpaces": skip}
        case.update(read(text, sep, quote, lenient, skip))
        reads.append(case)

    writes = []
    fields = ["", "a", "b c", " a ", "a,b", "a;b", "a\tb", "a|b", "say \"hi\"", "it's", "x\ny", "x\r\ny",
              "x\ry", "\"", "é😀", "1.5", "-", "''"]
    for _ in range(1500):
        rows = []
        for _ in range(random.randint(0, 4)):
            rows.append([random.choice(fields) for _ in range(random.randint(0, 4))])
        sep, quote, _, _ = random.choice(DIALECTS)
        ending = random.choice(["\n", "\r\n"])
        if ending == "\n":
            # Python 3.9 leaves a lone \r unquoted when lines end with \n,
            # which reads back wrong; this library quotes it, as later
            # Pythons do. Those rows aren't compared.
            rows = [[f for f in row if "\r" not in f] for row in rows]
        quote_all = random.random() < 0.2
        writes.append({"rows": rows, "separator": sep, "quote": quote, "lineEnding": ending,
                       "quoteAll": quote_all, "text": write(rows, sep, quote, ending, quote_all)})

    with open("tests/cases.json", "w", encoding="utf-8") as f:
        json.dump({"reads": reads, "writes": writes}, f, ensure_ascii=False)
    failures = sum(1 for c in reads if not c["ok"])
    print(f"{len(reads)} reads ({failures} failures), {len(writes)} writes -> tests/cases.json")


main()
