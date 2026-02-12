# Grammar Reference

MOL uses an LALR(1) grammar parsed by [Lark](https://github.com/lark-parser/lark). The full grammar is in `mol/grammar.lark`.

## EBNF Grammar

### Program Structure

```ebnf
program : statement+

statement : show_stmt
          | declare_stmt
          | assign_stmt
          | if_stmt
          | while_stmt
          | for_stmt
          | func_def
          | return_stmt
          | trigger_stmt
          | link_stmt
          | process_stmt
          | access_stmt
          | sync_stmt
          | evolve_stmt
          | emit_stmt
          | listen_stmt
          | block_stmt
          | guard_stmt
          | pipeline_def
          | expr_stmt
```

### Statements

```ebnf
show_stmt     : "show" expr
declare_stmt  : "let" NAME "be" expr
              | "let" NAME ":" TYPE "be" expr
assign_stmt   : "set" NAME "to" expr
if_stmt       : "if" expr "then" block elif* else? "end"
while_stmt    : "while" expr "do" block "end"
for_stmt      : "for" NAME "in" expr "do" block "end"
func_def      : "define" NAME "(" params? ")" block "end"
return_stmt   : "return" expr?
guard_stmt    : "guard" expr
              | "guard" expr ":" expr
pipeline_def  : "pipeline" NAME "(" params? ")" block "end"
```

### Expressions (by precedence, low → high)

```ebnf
expr         : pipe_chain
pipe_chain   : or_expr ("|>" or_expr)*
or_expr      : and_expr ("or" and_expr)*
and_expr     : not_expr ("and" not_expr)*
not_expr     : "not" not_expr | comparison
comparison   : addition (comp_op addition)*
addition     : multiply (("+"|"-") multiply)*
multiply     : unary (("*"|"/"|"%") unary)*
unary        : "-" unary | power
power        : atom ("^" unary)?
```

### Atoms

```ebnf
atom : NUMBER
     | ESCAPED_STRING
     | "true" | "false" | "null"
     | "[" (expr ("," expr)*)? "]"          -- list
     | "{" (pair ("," pair)*)? "}"          -- map
     | NAME "(" (expr ("," expr)*)? ")"     -- function call
     | atom "." NAME "(" (expr ("," expr)*)? ")"  -- method call
     | atom "." NAME                        -- field access
     | atom "[" expr "]"                    -- index access
     | NAME                                -- variable reference
     | "(" expr ")"                        -- grouping
```

### Type Names

```ebnf
TYPE : "Thought" | "Memory" | "Node" | "Stream"
     | "Number" | "Text" | "Bool" | "List"
     | NAME
```

## Lexical Rules

### Comments

```text
-- This is a comment (to end of line)
```

### Identifiers

Names must start with a letter or underscore, followed by letters, digits, or underscores.

### Keywords (30)

```text
if then elif else end while for in do define return begin
let be set to show and or not is true false null
trigger link process access sync evolve emit listen with
pipeline guard
```

### Operators

```text
|>  +  -  *  /  %  ^
==  !=  >  <  >=  <=  is  is not
and  or  not
```

### Literals

```text
Numbers:  42  3.14  -17  0.001
Strings:  "hello"  "multi\nline"  "with \"escapes\""
Booleans: true  false
Null:     null
```
