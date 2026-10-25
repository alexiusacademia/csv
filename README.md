# csv

Read and write CSV files in [Tessel](https://tessel-lang.syncster.dev)
programs: quoted fields with commas, quotes and line breaks in them, any
separator, a header to find columns by name, and columns read as numbers.
It reads and writes exactly as Python's `csv` module does, checked on
thousands of cases.

```tessel
import csv

fn main() {
    match csv.read("flows.csv") {
        .ok(t) -> {
            let flow = t.numbers("flow (m³/s)") ?? []
            print(flow)
            print(t.value(1, "Note") ?? "")
            print("{t.rows.count} rows, peak {flow.max() ?? 0.0}")
        }
        .failure(e) -> print(e.message)
    }
}
```

with `flows.csv`:

```text
Time (h),Flow (m³/s),Note
0,12.5,
6,80,"rising, fast"
12,310,
18,520,peak
24,450,
```

prints

```text
[12.5, 80.0, 310.0, 520.0, 450.0]
rising, fast
5 rows, peak 520.0
```

## Using it

Add it to a project (Tessel 0.10 or later):

```sh
tessel add csv
```

then `import csv`.

## Reading

| Function | Gives |
|---|---|
| `csv.read(path, separator:, header:)` | The file as a `Table`, or a failure saying why: no such file, not UTF-8 text, or a quote that's wrong, with its line and column. |
| `csv.table(text, separator:, header:)` | The same, from text. |
| `csv.parse(text, separator:)` | The rows as lists of fields, `[[String]]`, with no header. A blank line is an empty row. |
| `csv.guessSeparator(text)` | The separator the text most likely uses: `,` `;` tab or `\|`. |

- `separator` is `","` unless you say: `";"`, `"\t"`, `"|"`, any one ASCII
  character, or `""` to guess it from the text.
- With `header: false`, every line is a row.
- Lines may end with `\n`, `\r\n` or `\r`. A byte order mark at the start
  of the file is left out.
- A field in quotes may hold the separator, line breaks, and quotes
  written twice (`"said ""hi"""`).
- Two mistakes make a failure: a quote that's never closed, and more of
  the field after a closing quote (`"ab"c`). The message says where:

  ```text
  line 2, column 3: this quote is never closed
  ```

  With `lenient: true` these are read as Python reads them by default
  instead: the field runs to the end of the text, or goes on after the
  quote. `skipSpaces: true` leaves out spaces after each separator, and
  `quote: "'"` uses another quote character.

## Tables

A `Table` has the `header` (the first line's names) and the `rows` after
it. Blank lines are left out, and rows may be shorter or longer than the
header: a field that isn't there reads as `""`.

| Method | Gives |
|---|---|
| `column(name)` | The column's fields, or `nil` when there's no such column. |
| `numbers(name, decimalComma:)` | The column as `[Float]`, with `NaN` where a field is blank or isn't a number, or `nil` when there's no such column. |
| `columnAt(i)`, `numbersAt(i)` | The same, by the column's index. |
| `index(name)` | The column's index, or `nil`. |
| `value(row, name)` | One field. |
| `record(row)` | A row as `[String: String]`, from column name to field. |
| `append(row)` | Adds a row. |
| `text(separator:, lineEnding:, quoteAll:)` | The table as CSV text. |
| `save(path, …)` | Saves it as a file, and returns whether it worked. |

A column is found by its exact name first, then ignoring case and spaces
at either end, so `t.numbers("flow (m³/s)")` finds `Flow (m³/s)`.

`NaN` breaks a line in [chart](https://chart-package.syncster.dev), so a
column with gaps plots as it should:

```tessel
import csv
import chart

fn main() {
    let t = try csv.read("flows.csv")
    var c = chart.Chart(title: "Inflow", xLabel: t.header[0], yLabel: t.header[1])
    c.line(t.numbersAt(0), t.numbersAt(1), markers: true)
    print(c.savePNG("flows.png"))
}
```

## Numbers

`csv.number(text, decimalComma:)` reads one field as a `Float`, or `nil`.
Spaces at either end are ignored, and so are thousands separators in
groups of three. With `decimalComma: true`, the comma is the decimal
point and `.` or a space separates thousands, as in files from much of
Europe (which use `;` as the separator):

```tessel
print(csv.number(" 1,234.5 ") ?? 0.0)                   // 1234.5
print(csv.number("2,5", decimalComma: true) ?? 0.0)    // 2.5
```

## Writing

| Function | |
|---|---|
| `csv.format(rows, separator:, lineEnding:, quoteAll:)` | Rows as CSV text. |
| `csv.write(path, rows, …)` | Saves rows as a file, and returns whether it worked. |
| `csv.fromColumns(header, columns, decimals:)` | A `Table` made from columns of numbers, ready to save. `NaN` is written as an empty field. |

A field is put in quotes only when it holds the separator, a quote or a
line break (or always, with `quoteAll: true`). Lines end with `"\n"`
unless you say; `lineEnding: "\r\n"` is what Excel and RFC 4180 write.

```tessel
print(csv.format([["name", "note"], ["Ann", "said \"hi\", left"]]))
let t = csv.fromColumns(["t", "q"], [[0, 1, 2], [1.5, 2.25, 3]])
print(t.text())
```

```text
name,note
Ann,"said ""hi"", left"

t,q
0.0,1.5
1.0,2.25
2.0,3.0

```

## Mistakes in the code

A separator or quote that isn't one ASCII character, is a line break, or
is the same as the other is a mistake in the code, and stops the program
with a message like `csv: the separator must be one ASCII character, like
"," or ";", not "::"`.

## Speed

Fields are cut out of the file's bytes in one piece. On an Apple M5 Pro,
a 4.3 MB file of 100 000 rows reads in about 0.04 s and is written again
in about 0.03 s.

## Tests

```sh
tessel run tests
```

checks the library against Python's `csv` module on 6 392 readings (56
texts written by hand to be tricky, each read in 7 ways, and 6 000 random
ones, with different separators, quotes and settings, including every kind of
mistake) and 1 500 sets of rows written and read back. Then it tests the
tables, numbers, files, messages and speed. `python3
tools/oracle/oracle.py` makes the cases again (`tests/cases.json`).

## What's where

| File | |
|---|---|
| `read.tsl` | `parse` and `guessSeparator`: reading text into rows. |
| `table.tsl` | `Table`, `table`, `read`, `fromColumns` and `number`. |
| `write.tsl` | `format` and `write`. |
| `tests/` | The tests and the cases from Python. |
| `tools/oracle/oracle.py` | Makes the cases from Python. |

## Licence

MIT: see [LICENSE](LICENSE).
