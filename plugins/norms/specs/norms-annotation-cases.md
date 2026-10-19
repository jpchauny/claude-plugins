# Norms Annotation Cases

**Status:** Draft
**Audience:** Whoever builds the layer 2 generator, and the agents that read its output

**Scope:** Where the generator puts IDs in the special cases of GFM: items, link reference definitions, tables, block quotes, unclosed blocks, tabs, and the cases where only a wider frame keeps the file

specs/norms-tree.md gives the general rule: an ID goes at the end of its node, or the node is framed (R24), and the annotated file keeps the blocks of the foundation file. This document holds the cases where that rule needs more: the ones where an ID at the end, or a marker line, would change how the file parses. It holds the requirements R35–R52, each followed by its examples E25–E68. The examples are requirements too, and serve as test cases for the generator (R28). Each one shows a foundation text and its annotated copy, numbered as on a first run, without the file marker (R29). Every annotated example is the generator's exact output: removing its insertions gives back the input byte for byte (R23), and it parses to the same blocks as the input (R64). Following nodes across versions is in specs/norms-versions.md.

Some examples hold bytes that do not show: a tab, or a space at the end of a line. The prose under each example says where they are.

## Items

- **R35. An item whose first block is not a paragraph has its ID right after its marker.**
  - This covers a first block that is a heading, code block, HTML block, quote, list, table, thematic break or definition.
  - In a task item, the item's content starts after its checkbox (R38), so the ID goes right after the checkbox instead, as for a definition after a task checkbox (E31).
  - It also covers an item paragraph whose ID at the end would change how the item parses. One case is `- [ ]`, which would become a task item (E15 in specs/norms-tree.md). Another is a paragraph whose last line is a bare list marker (`1.`). This is probed on the whole file.
  - The rest of the marker line moves to a new line, indented to the item's content, with a blank line between (R30). The block keeps its bytes, and an indented code block keeps its indentation.
  - When the move would change the file, R36 applies. When nothing works, R49 applies.
  - A definition may start after any blanks on a line that no block covers (`- [ ]\t[x]: /u`).

### E25. Item whose first block is a fenced code block or a table

The item's ID goes after its marker. The fence moves to a line of its own, indented to the item's content, and is framed (R26). Nothing is written on its opening line.

````markdown
- ```
  x
  ```
- b
````

````markdown
⟬TYP-1 begin⟭

- ⟬TYP-2⟭

  ⟬TYP-3 begin⟭

  ```
  x
  ```

  ⟬TYP-3 end⟭

- b ⟬TYP-4⟭

⟬TYP-1 end⟭
````

A table as the first block is moved and framed the same way. Its cells keep their IDs.

```markdown
- | a |
  |---|
- b
```

```markdown
⟬TYP-1 begin⟭

- ⟬TYP-2⟭

  ⟬TYP-3 begin⟭

  | a ⟬TYP-4⟭ |
  |---|

  ⟬TYP-3 end⟭

- b ⟬TYP-5⟭

⟬TYP-1 end⟭
```

### E26. Item whose first block is indented code

The code starts on the marker line, after five spaces: one for the marker and four of indentation. Moved to a line of its own, it keeps its column, so it stays indented code (R37). Those four spaces are part of the code. `more` is a child paragraph of the item, after the code, with its own ID: the item has no paragraph of its own (R33).

```markdown
-     code
  more
- b
```

```markdown
⟬TYP-1 begin⟭

- ⟬TYP-2⟭

  ⟬TYP-3 begin⟭

      code

  ⟬TYP-3 end⟭

  more ⟬TYP-4⟭
- b ⟬TYP-5⟭

⟬TYP-1 end⟭
```

### E27. Item whose only content is a thematic break

The second item's ID goes after its marker, and the break moves to the item's content column. A thematic break has no ID (R7).

```markdown
1. a
2. ***
```

```markdown
⟬TYP-1 begin⟭

1. a ⟬TYP-2⟭
2. ⟬TYP-3⟭

   ***

⟬TYP-1 end⟭
```

### E28. Item text that an ID would turn into a checkbox

Followed by an ID, `- [ ]` would become a task item. So the ID goes after the marker, and `[ ]` moves below it, where it stays text. A list of one item has one ID, the item's (R27).

```markdown
- [ ]
```

```markdown
- ⟬TYP-1⟭

  [ ]
```

### E29. Item paragraph ending with a bare list marker

The last line `1.` is text: an empty item cannot interrupt a paragraph. Followed by an ID, `1.` would be an item that can, and would open a list. So the ID goes after the item's marker.

```markdown
- a
  1.
```

```markdown
- ⟬TYP-1⟭

  a
  1.
```

### E30. Item whose first block is a definition

The definition moves below the item's ID and is framed, as every definition is (E7 in specs/norms-tree.md). The reference `[a]` after the list still resolves.

```markdown
- [a]: /u
- b

[a]
```

```markdown
⟬TYP-1 begin⟭

- ⟬TYP-2⟭

  ⟬TYP-3 begin⟭

  [a]: /u

  ⟬TYP-3 end⟭

- b ⟬TYP-4⟭

⟬TYP-1 end⟭

[a] ⟬TYP-5⟭
```

### E31. Definition after a task checkbox

The item's ID goes after the checkbox, which stays first (E15 in specs/norms-tree.md). The definition is framed below it.

```markdown
- [ ] [a]: /u
```

```markdown
- [ ] ⟬TYP-1⟭

  ⟬TYP-2 begin⟭

  [a]: /u

  ⟬TYP-2 end⟭
```

- **R36. A marker line that cannot be split.**
  - When moving the rest of an item's marker line would change how the file parses, the item's ID goes at the end of its first line. One case is `- - [ ] t`: on a line of its own, the inner item would become a task item.
  - So do the IDs of the nodes that start on that line and would be framed, such as a nested list. The deeper IDs come first.
  - This is probed on the whole file, with its containers.
  - The ID at the end of the line must not fall into an indented code block, a code span or a link that runs on, or after a definition. If it would, the ID goes at the end of the code span or link, when that keeps the blocks (E34). Otherwise R49 applies.

### E32. Nested task-like list on its parent's marker line

On its parent's marker line, `[ ] t` is plain text. Moved to a line of its own, it would be a checkbox. So the line is not split. Its end holds the inner item's ID (TYP-3), then the nested list's (TYP-2), then the outer item's (TYP-1). The outer list has one item, so it has no ID of its own (R27).

```markdown
- - [ ] t
  - b
```

```markdown
- - [ ] t ⟬TYP-3⟭ ⟬TYP-2⟭ ⟬TYP-1⟭
  - b ⟬TYP-4⟭
```

### E33. Setext heading starting with `#` in a task item

The item holds a setext heading, `# done` underlined by `---`. On a line of its own, `# done` would become an ATX heading and `---` a thematic break. So the line is not split: the heading's ID and then the item's go at the end of it, above the underline.

```markdown
- [ ] # done
  ---
```

```markdown
- [ ] # done ⟬TYP-2⟭ ⟬TYP-1⟭
  ---
```

### E34. Line-end ID never inside a code span

The inner item's text ends in a code span that runs onto the next line. At the end of the marker line, an ID would fall inside the span (E17 in specs/norms-tree.md). So the inner item's ID goes at the end of the code span. The outer item has no place on that line, so it is framed at the bounds of its top-level block, the list (R49).

```markdown
- - [ ] see `a
  b`
```

```markdown
⟬TYP-1 begin⟭

- - [ ] see `a
  b` ⟬TYP-2⟭

⟬TYP-1 end⟭
```

- **R37. A moved rest of line keeps its column.**
  - When the rest of an item's marker line moves to a line of its own, or a frame begins mid-line, the rest is written after the line's own prefix. Every `>` is kept, and every other byte becomes a space. A tab becomes as many spaces as the columns it took.
  - Columns are counted from the quote's content, as the parser counts an item's content. After a `>` with no space (`>-`), one more space is written.
  - A tab in the rest may then take one column less. If that changes the file, the rest keeps the line's own columns instead. If neither keeps the file, R36 applies.
  - Several moves on one line compose. Each is computed on the line as the earlier one wrote it, and probed with it.
  - An item whose ID ends a line that an earlier move rewrote is probed again. If it fails, it is framed at its top-level block (R49).

### E35. Indented code in an item, in a quote with no space after `>`

The marker lines take the item's content indentation, counted from the quote's content, and one more space for the missing space after `>`. The code moves to a line of its own and keeps its column, so it stays indented code. The quote and the list have one child each, so the item's ID stands for them (R27).

```markdown
>7)     code
```

```markdown
>7) ⟬TYP-1⟭
>
>    ⟬TYP-2 begin⟭
>
>        code
>
>    ⟬TYP-2 end⟭
```

### E36. Two moves on one line, with a tab

The line starts with a space, and a tab follows the `-`, the line's second marker. The first item's first block is a list, so its ID goes after `1.` and the rest of the line moves. The inner item's first block is a heading, so its ID goes after `-` and its tab, and the heading moves again. The second move is computed on the line the first one wrote. The tab is kept on the moved line.

```markdown
 > 1. -	# h
```

```markdown
 > 1. ⟬TYP-1⟭
 >
 >    -	⟬TYP-2⟭
 >
 >      # h ⟬TYP-3⟭
```

- **R38. Tabs and content columns.**
  - Item content columns follow GFM tab stops, every 4 columns: a tab after `-` reaches column 4. A marker line inside the item is indented with spaces to that virtual column.
  - After `-\t`, the tab is the blank before an ID on the marker line, since one more space would move the item's content column. An empty item is the exception: it has no content column to keep, and its ID takes R39's inserted spaces, the tab staying after it.
  - After `>`, a tab takes one column for the optional space.
  - On a later line, an item's content column is counted from its container's content on that line. A line not indented that far is not in the item.
  - On a task item's marker line, its content starts after the checkbox.

### E37. ID after the tab of `-\t`

A tab follows `-`. It is the blank before the ID, and the heading moves to the item's content column, 4.

```markdown
-	# h
```

```markdown
-	⟬TYP-1⟭

    # h ⟬TYP-2⟭
```

### E38. Markers in a tab-indented item take 4 spaces

A tab follows each `-`, and a tab indents each line of the fenced code block. The code block's frame markers are indented with four spaces, the virtual column the tab reaches. The code keeps its tabs.

````markdown
-	one

	```
	code
	```
-	two
````

````markdown
⟬TYP-1 begin⟭

-	one ⟬TYP-2⟭

    ⟬TYP-3 begin⟭

	```
	code
	```

    ⟬TYP-3 end⟭

-	two ⟬TYP-4⟭

⟬TYP-1 end⟭
````

### E39. Tab after `>`

A tab follows `>` on each line. It takes one column for the optional space, and the rest of its width counts toward the item. The nested list's marker lines are indented with spaces to the same virtual column.

```markdown
>	- a
>	  - b
>	  - c
```

```markdown
>	- a ⟬TYP-1⟭
>
>     ⟬TYP-2 begin⟭
>
>	  - b ⟬TYP-3⟭
>	  - c ⟬TYP-4⟭
>
>     ⟬TYP-2 end⟭
```

- **R39. Empty item.** An item with nothing on its marker line and no paragraph as its first block has its ID on that line, right after its marker: an item with no content, or one whose first block starts on a later line and is not a paragraph (R35, E42). An item whose first paragraph starts on the next line has its ID at the end of that paragraph, as any item (R24, R33): `-`, `  x` → `-`, `  x ⟬TYP-1⟭`. The one exception is a first paragraph on a later line that a table interrupts, when the table's frame begins above the paragraph (R44): the item takes its ID here, on its marker line, so that the marker line keeps content. Any trailing spaces or tabs of the line stay after the ID, with the probes' inserted blanks before it: `-  ` → `- ⟬TYP-1⟭  `, and after `-\t` too, `-\t` → `- ⟬TYP-1⟭\t` (R38). The ID gives the item content, though. An unindented next line would then continue it as a lazy line, and a line indented to the new content column would nest in it. The placements are probed on the whole file, in this order, and the first that keeps its blocks wins:
  - ` ⟬ID⟭`;
  - ` ⟬ID⟭` and a blank line;
  - 2, 3 or 4 blanks before the ID, which moves the item's content column past the next line's indentation (5 would make the ID indented code), first without and then with the blank line.

  An empty item that took its quote's place (R27) keeps the quote's `>` in that blank line. The ID never joins a setext heading's text on the next line.

### E40. Empty item, next line lazy

After `- ⟬TYP-1⟭`, the line `para` would be a lazy line of the item. The blank line keeps it a paragraph of its own.

```markdown
-
para
```

```markdown
- ⟬TYP-1⟭

para ⟬TYP-2⟭
```

### E41. Empty item whose ID takes two blanks

`  - b` is the second item of the list, not a child of the empty one. After `- ⟬TYP-2⟭`, the item's content column would be 2, and `  - b` would nest in it. Two blanks move the column to 3, so `  - b` stays a sibling.

```markdown
-

  - b
```

```markdown
⟬TYP-1 begin⟭

-  ⟬TYP-2⟭

  - b ⟬TYP-3⟭

⟬TYP-1 end⟭
```

### E42. Empty item above a setext heading

The item's content is a setext heading on the next lines. Without the blank line, the ID would join the heading's text.

```markdown
+
  t
  =
```

```markdown
+ ⟬TYP-1⟭

  t ⟬TYP-2⟭
  =
```

### E43. Empty item that took its quote's place

The quote has one child, the list, which has one item: the item's ID stands for all three (R27). The blank line after the ID keeps the quote's `>`.

```markdown
>-
>   2)
```

```markdown
>- ⟬TYP-1⟭
>
>   2) ⟬TYP-2⟭
```

- **R40. Empty task item.** A task item with nothing after its checkbox is an empty item whose content starts after the checkbox (R38).
  - Its ID goes on its marker line, right after the checkbox and before any trailing blanks, with R39's probes (`- [ ] ` → `- [ ] ⟬TYP-1⟭ `, E44).
  - When no placement on that line keeps the file's blocks, it is framed at its top-level block (R49). This happens when a later line is indented to the item's content after a blank line: the ID would take that line into the item (E44b).

### E44. Empty task item

The first line ends with a space after `]`. The ID goes after the checkbox, and the space stays after it.

```markdown
- [ ] 

next
```

```markdown
- [ ] ⟬TYP-1⟭ 

next ⟬TYP-2⟭
```

Here the first line also ends with a space after `]`, and `  b` is indented to the item's content after a blank line. An ID on the marker line would take `  b` into the item, so the item is framed at its top-level block.

```markdown
- [ ] 

  b
```

```markdown
⟬TYP-1 begin⟭

- [ ] 

⟬TYP-1 end⟭

  b ⟬TYP-2⟭
```

## Link reference definitions

- **R41. A definition joined to the text after it.**
  - The parser reads a definition and the text right after it, with no blank line between, as one block.
  - Framing the definition apart could change how that text parses. An indented line would become code, `---` a thematic break, a lazy line of an item would leave the item, `<img>` would become an HTML block, or a setext heading would lose its first line.
  - When it would, the definition is not a node of its own. The paragraph or heading starts at it, and the definition's text is part of that node's own text.
  - Text that parses the same keeps the definition framed apart (E7 in specs/norms-tree.md).

### E45. Definition before an indented line

Framed apart, the definition would leave `    ind` as indented code. So the paragraph starts at the definition. It has two lines, so it is framed.

```markdown
[r]: /u
    ind
```

```markdown
⟬TYP-1 begin⟭

[r]: /u
    ind

⟬TYP-1 end⟭
```

### E46. Definition in an item before a lazy line

Framed apart, the definition would leave `lazy` outside the item. So the item's paragraph starts at the definition, and the item's ID goes at the end of its text (E12 in specs/norms-tree.md).

```markdown
- [r]: /u
lazy
```

```markdown
- [r]: /u
lazy ⟬TYP-1⟭
```

- **R42. A definition whose destination is on the next line.** When that destination starts with `[` (`[a]:` then `[x]`), the two lines are one definition. A line starting with `[` opens a new definition only once the current one is whole.

### E47. Destination that starts with `[`

```markdown
[a]:
[x]

[t][a]
```

```markdown
⟬TYP-1 begin⟭

[a]:
[x]

⟬TYP-1 end⟭

[t][a] ⟬TYP-2⟭
```

- **R43. Definitions on lazy lines.**
  - The definitions of a block quote or list item stay open until a blank line or another block. The non-blank lines after them that no block covers are their lazy continuation lines. They are inside the container, even past its last line.
  - Such a line continues the last definition (`> [a]:` then `/u`, `:-`, `=`, `***`, a fence or `<div>`) or opens a new one. Which of the two is probed with the lazy lines parsed as lazy lines in a quote.
  - Every definition has its node, and the container holds them.
  - A frame between an in-container line and a lazy line would cut the lazy line off. So the definitions on each side of such a boundary are framed at the bounds of their top-level block (R49).

### E48. Second definition on a lazy line of a quote

`[m]: /v` has no `>`, but it is a lazy line of the quote, and a second definition in it. The quote (TYP-1) and its two definitions (TYP-2, TYP-3) are all framed at the bounds of the quote.

```markdown
> [l]: /u
[m]: /v

after
```

```markdown
⟬TYP-1 begin⟭

⟬TYP-2 begin⟭

⟬TYP-3 begin⟭

> [l]: /u
[m]: /v

⟬TYP-3 end⟭

⟬TYP-2 end⟭

⟬TYP-1 end⟭

after ⟬TYP-4⟭
```

### E49. Definition completed on a lazy line

The destination `/u` is on a lazy line. The quote has one child, the definition, so the definition's ID stands for both (R27).

```markdown
> [a]:
/u
```

```markdown
⟬TYP-1 begin⟭

> [a]:
/u

⟬TYP-1 end⟭
```

## Tables

- **R44. A paragraph that a table interrupts.**
  - Its first line stays text even when it looks like a definition.
  - The placements are probed on the whole file, in order:
    - the usual ID, with the table's begin marker between paragraph and table;
    - the ID at the end of the last line, with the begin marker between them, and then above the paragraph (the paragraph stays right above the table, inside its frame);
    - the same with the ID at the end of an earlier line (a last line `1.` or `*` would become an item);
    - else both are framed at their top-level block (R49).
  - Above the paragraph, when the paragraph is the content of an empty item, the probe includes the item's ID (R39).
  - A header row that was an indented line of the paragraph stays one.
  - When the header row follows a paragraph made only of definitions (`[a]: /u`, `---`, `|-|`), the definitions are part of the table's text (R50, E66).

### E50. Definition-like line right above a table

`[r]: /u` is the paragraph that the table interrupts, so it is text, with its ID at the end.

```markdown
[r]: /u
| a |
|---|
```

```markdown
[r]: /u ⟬TYP-1⟭

⟬TYP-2 begin⟭

| a ⟬TYP-3⟭ |
|---|

⟬TYP-2 end⟭
```

### E51. Begin marker above the paragraph

The paragraph has two lines and no blank line before the table. The table's begin marker goes above the paragraph, which stays right above the table, inside its frame.

```markdown
[r]: /u
text
| a |
|---|
```

```markdown
⟬TYP-2 begin⟭

[r]: /u
text ⟬TYP-1⟭
| a ⟬TYP-3⟭ |
|---|

⟬TYP-2 end⟭
```

### E52. ID at the end of an earlier line

The paragraph's last line is `1.`. Followed by an ID, it would become an item. So the ID goes at the end of the paragraph's first line.

```markdown
[l]: /u
1.
a | b
--|--
```

```markdown
[l]: /u ⟬TYP-1⟭
1.

⟬TYP-2 begin⟭

a ⟬TYP-3⟭ | b ⟬TYP-4⟭
--|--

⟬TYP-2 end⟭
```

### E53. Header row that is an indented line of the paragraph

`    a | b` is a line of the paragraph and the table's header row. The begin marker goes above the paragraph, and the header row stays as it was.

```markdown
para
    a | b
--|--
```

```markdown
⟬TYP-2 begin⟭

para ⟬TYP-1⟭
    a ⟬TYP-3⟭ | b ⟬TYP-4⟭
--|--

⟬TYP-2 end⟭
```

- **R45. Table rows are read from the source.**
  - A row starts at its container's content, blanks skipped.
  - Its cells are the bytes between its unescaped pipes. A pipe right after a backslash is escaped, even inside a code span.
  - The parser gives only each row's line and its number of columns.
  - A cell's ID goes at the end of its text. An empty cell's ID goes right after the cell's opening pipe, before its padding (`|  |` → `| ⟬ID⟭  |`).
  - A short row first gets its missing cells as empty ones (` |`), so that its ID lands past the last column.
  - A long row's extra cells are row text with no ID (R33 in specs/norms-tree.md).
  - A row's ID is written as an extra cell after its last cell. A row with a closing pipe gets ` ⟬ID⟭ |` after that pipe, and a row without one gets ` | ⟬ID⟭` at its end (E55).
  - The parser drops the row's ID cell, so the row's ID lives only in the text (E10 in specs/norms-tree.md).

### E54. Short, long and empty-celled rows

The row `| c |` gets one empty cell before its ID. The row `| d | e | f |` has one cell past the header's columns: `f` has no ID. The empty cell of the last row keeps its ID, right after its opening pipe and before its two spaces of padding. Each row's ID ends with ` |`, after the row's closing pipe.

```markdown
| a | b |
|---|---|
| c |
| d | e | f |
|  | g |
```

```markdown
⟬TYP-1 begin⟭

| a ⟬TYP-2⟭ | b ⟬TYP-3⟭ |
|---|---|
| c ⟬TYP-5⟭ | | ⟬TYP-4⟭ |
| d ⟬TYP-7⟭ | e ⟬TYP-8⟭ | f | ⟬TYP-6⟭ |
| ⟬TYP-10⟭  | g ⟬TYP-11⟭ | ⟬TYP-9⟭ |

⟬TYP-1 end⟭
```

### E55. Rows without pipes at the ends

The body row gets ` | ` before its ID.

```markdown
a | b
--|--
c | d
```

```markdown
⟬TYP-1 begin⟭

a ⟬TYP-2⟭ | b ⟬TYP-3⟭
--|--
c ⟬TYP-5⟭ | d ⟬TYP-6⟭ | ⟬TYP-4⟭

⟬TYP-1 end⟭
```

### E56. Escaped pipe in a code span

The third line is `` | `x\|y` | z | ``. The pipe after the backslash is escaped, so `` `x\|y` `` is one cell.

```markdown
| a | b |
|---|---|
| `x\|y` | z |
```

```markdown
⟬TYP-1 begin⟭

| a ⟬TYP-2⟭ | b ⟬TYP-3⟭ |
|---|---|
| `x\|y` ⟬TYP-5⟭ | z ⟬TYP-6⟭ | ⟬TYP-4⟭ |

⟬TYP-1 end⟭
```

- **R46. A pipe before a row.** Some rows have no leading pipe and a first cell of `-`, `+`, `1.`, `7)`, `#` or `<div`. Once ` ⟬ID⟭` follows that cell, the row becomes a list item, a heading or an HTML block. The generator then inserts a `|` at the start of the row, the header row included. A leading pipe is optional in GFM, so the row and its cells stay as they are. Removing the recorded insertions removes the pipe too (R23).

### E57. Body row starting with `-`

`- ⟬TYP-5⟭` would be a list item. The inserted `|` keeps it a row.

```markdown
a | b
--|--
-|x
```

```markdown
⟬TYP-1 begin⟭

a ⟬TYP-2⟭ | b ⟬TYP-3⟭
--|--
|- ⟬TYP-5⟭|x ⟬TYP-6⟭ | ⟬TYP-4⟭

⟬TYP-1 end⟭
```

### E58. Header row starting with `#`

`# ⟬TYP-2⟭` would be a heading. The inserted `|` keeps it the header row.

```markdown
#|b
-|-
c|d
```

```markdown
⟬TYP-1 begin⟭

|# ⟬TYP-2⟭|b ⟬TYP-3⟭
-|-
c ⟬TYP-5⟭|d ⟬TYP-6⟭ | ⟬TYP-4⟭

⟬TYP-1 end⟭
```

## Block quotes

- **R47. A block quote ends with its blank `>` lines.**
  - The `>` lines after a quote's last child belong to the quote. They are in its span and its own text, and its end marker goes after them. Before them, it would leave them to open a new, empty quote.
  - A line holding `>` past the quotes of its block is content, not a blank line.
  - A `>` line indented less than its item is not in it.

### E59. Trailing blank `>` line

```markdown
> - a
> - b
>

next
```

```markdown
⟬TYP-1 begin⟭

> - a ⟬TYP-2⟭
> - b ⟬TYP-3⟭
>

⟬TYP-1 end⟭

next ⟬TYP-4⟭
```

### E60. A `>` that is content

The second line's second `>` is inside the quote, so it is a line of the HTML block, not a blank line. The quote has one child, so the HTML block's ID stands for both (R27).

```markdown
> <div>
> >
```

```markdown
⟬TYP-1 begin⟭

> <div>
> >

⟬TYP-1 end⟭
```

## Unclosed blocks

- **R48. Unclosed blocks.**
  - A fenced code block never closed, or an HTML block of types 1-5 without its closing sequence (`<!--` with no `-->`, `<pre>` with no `</pre>`), runs to the end of its container, blank lines included.
  - It is framed, and nothing else is inserted: no closing fence, no closing tag. Foundation is never corrected.
  - Its span runs to the end of its code, trailing blank lines included.
  - For a parser, its end marker, the end markers of the containers that close there, and the blank lines next to them (R30), fall inside it. This is the one accepted exception (R26 in specs/norms-tree.md, U1), and verify tolerates exactly those end markers and blank lines (R64 in specs/norms-versions.md, E61, E62).

### E61. Fence never closed

````markdown
```
x
````

````markdown
⟬TYP-1 begin⟭

```
x

⟬TYP-1 end⟭
````

### E62. HTML comment never closed

```markdown
<!-- a

b
```

```markdown
⟬TYP-1 begin⟭

<!-- a

b

⟬TYP-1 end⟭
```

### E63. Unclosed fence in an item

The fence runs to the end of the item. `next` is not in the item, so it keeps its own ID.

````markdown
- ~~~~
  x

next
````

````markdown
- ⟬TYP-1⟭

  ⟬TYP-2 begin⟭

  ~~~~
  x

  ⟬TYP-2 end⟭

next ⟬TYP-3⟭
````

## Wider frames

- **R49. A frame widened to the top-level block.**
  - When no placement at a node keeps the file's blocks, the node is framed at the start and end of the top-level block that holds it (a child of the file or of a section), inside that block's own frame.
  - Examples are an ID that would fall into indented code on its marker line (`>-\t\tc`), after a definition the item cannot lose, or into a code span or link with no end that fits.
  - The frame is wider than the node, but it nests, holds the node, and changes nothing of how the file parses.
  - Such frames nest right inside the top-level block's own frame, and outside every other frame that begins or ends at those lines, such as those of the block's descendants. Of several widened to one block, a deeper node's frame is inside a shallower one's, and of two at one depth, the node later in pre-order is inside the earlier (E48: `⟬TYP-2 begin⟭`, then `⟬TYP-3 begin⟭`; E64: the item TYP-1 outside its code TYP-2).
  - A frame begun mid-line right after a `>` with no space continues the line after `>` (R37).

### E64. ID that would fall into indented code

Two tabs follow `-`, so the item's first block is indented code on its marker line. No placement at the item keeps the file's blocks. The item (TYP-1, which stands for its quote and list, R27) and its code (TYP-2) are framed at the bounds of the quote.

```markdown
>-		c
```

```markdown
⟬TYP-1 begin⟭

⟬TYP-2 begin⟭

>-		c

⟬TYP-2 end⟭

⟬TYP-1 end⟭
```

### E65. Definition on a marker line that cannot be split

The item holds only a definition, on its marker line, and has no content: `  b`, after the blank lines, is a paragraph after the list. Splitting the marker line (R35) would give the item content, its ID, and the line indented to it would then join the item, as in E44b. An ID at the end of the definition would also turn the definition into a paragraph. So the item and its definition are framed at the bounds of the list. `b` is not in the item: it keeps its own ID.

```markdown
- [a]: /u


  b
```

```markdown
⟬TYP-1 begin⟭

⟬TYP-2 begin⟭

- [a]: /u

⟬TYP-2 end⟭

⟬TYP-1 end⟭


  b ⟬TYP-3⟭
```

- **R50. The whole annotated file is checked.**
  - Placements are probed one at a time, and two that are each safe alone can still clash.
  - After annotating, the generator parses the whole file once more and compares its blocks with the source's.
  - When they differ, it finds the nodes that cause it, one top-level block at a time, and node by node inside the blocks that need it.
  - It frames them at the bounds of their top-level block (R49).

### E66. Header cell `---` right under a definition

`---` is the table's header row, and the definition above it is part of the table's text (R44). The whole-file check frames the header cell (TYP-2) at the bounds of the table (TYP-1).

```markdown
[a]: /u
---
|-|
```

```markdown
⟬TYP-1 begin⟭

⟬TYP-2 begin⟭

[a]: /u
---
|-|

⟬TYP-2 end⟭

⟬TYP-1 end⟭
```

## Headings

- **R51. An empty ATX heading off column 1** has its ID where it has it at column 1 (R18 and E2 in specs/norms-tree.md).
  - Without a closing sequence, the ID goes at the end of the line, after any trailing spaces or tabs, with one space before it (E67).
  - With a closing sequence, it goes right after the opening `#`s, and the blanks before the sequence stay after it (`  #  ##` → `  # ⟬TYP-1⟭  ##`, E2b in specs/norms-tree.md).

### E67. Indented empty heading

The line starts with two spaces.

```markdown
  #
```

```markdown
  # ⟬TYP-1⟭
```

Here the line is `  #` followed by two spaces. The ID goes after them, at the end of the line, with its own space before it.

```markdown
  #  
```

```markdown
  #   ⟬TYP-1⟭
```

### E68. Empty heading in a quote

The quote has one child, so the heading's ID stands for both (R27).

```markdown
> #
```

```markdown
> # ⟬TYP-1⟭
```

## Line endings

- **R52. Line endings and BOM.**
  - An inserted line ends with the file's line ending: `\r\n` in a file that has one; else `\r` in a file that has a `\r` and no `\n`; else `\n`.
  - So in a file whose only line endings are lone `\r`, every inserted line ends with `\r`, the file marker's included (`⟬TYP⟭\r\r` at the start).
  - In a file with both, the lines inserted right after a lone `\r` (a `\r` not followed by `\n`) end with `\r`, so that they do not join the source's `\r` into one `\r\n`. In `a\rb\n`, nothing is inserted right after the lone `\r`, so every inserted line ends with `\n`.
  - The file marker goes after a BOM (R29 in specs/norms-tree.md).

  There is no example, since these bytes do not show in a fence. The unit tests `test_crlf_line_endings_are_kept`, `test_lone_cr_line_endings_keep_their_blank_lines_r30`, `test_a_lone_cr_file_ends_every_inserted_line_with_cr_r52` and `test_file_marker_after_a_bom_r29` cover it.
