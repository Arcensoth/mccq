# Minecraft Command Query
Minecraft command query program. Inspired by the in-game help command, with added features like multiple version support and expandable regex search.

## Basic usage
Start with a basic command:
```bash
>mccq say
```

This produces some output:
```bash
say <message>  # 18w03b
```
Which will generally outline all possible variations of the command for the currently configured version(s).

Try something with several subcommands/arguments:
```bash
>mccq tag
tag <targets> add|list|remove ...  # 18w03b
```
The command is rolled out until a choice can be made, which saves on vertical space and is often more readable than assigning a separate line to each possibility.

## Program options
Various flags and options can be written **before the command query** to augment behaviour.

Normally several subcommands/arguments are condensed to one line, but `-e` can be used to forcibly expand the command:
```bash
>mccq -e tag
# 18w03b
tag <targets> add <name>
tag <targets> list
tag <targets> remove <name>
```
Be warned that this can cause a large amount of output for commands with many subcommands/arguments.

Search for specific subcommands/arguments:
```bash
>mccq tag targets add
tag <targets> add <name>  # 18w03b
```
Arguments are shown inside `<>`, but can be searched by name just like subcommands.

Speaking of arguments, use `-t` to render their types:
```bash
>mccq -t tag targets add
tag <targets: entity> add <name: string>  # 18w03b
```

Use `-c CAPACITY` to provide a threshold determining whether to expand a command:
```bash
>mccq -c 3 tag
# 18w03b
tag <targets> add <name>
tag <targets> list
tag <targets> remove <name>
```
This allows a command to expand so long as the number of subcommands/arguments it contains does not exceed the given threshold.

Use `-v VERSION` to query a particular version:
```bash
>mccq -v 18w01a execute
execute align|as|at|if|offset|run|store|unless ...  # 18w01a
```

Repeat `-v VERSION` to query several versions at once:
```bash
>mccq -v 18w01a -v 18w02a execute
execute align|as|at|if|offset|run|store|unless ...  # 18w01a
execute align|anchored|as|at|facing|if|in|positioned|rotated|run|store|unless ...  # 18w02a
```

## Dynamic search
Each search term of the provided `command` is treated as a regex pattern, meaning any number of subcommands/arguments can be flexibly queried:
```bash
>mccq execute a.*
# 18w03b
execute align <axes> -> execute
execute anchored <anchor> -> execute
execute as <targets> -> execute
execute at <targets> -> execute
```

Going even deeper:
```bash
>mccq execute a.* targets
# 18w03b
execute as <targets> -> execute
execute at <targets> -> execute
```

Search terms are case-insensitive:
```bash
>mccq gamerule domob.*
# 18w03b
gamerule doMobLoot
gamerule doMobLoot <value>
gamerule doMobSpawning
gamerule doMobSpawning <value>
```

Special-case: a single `.` is treated as a wildcard and will match any subcommands/argument:
```bash
>mccq clone . . . masked
# 18w03b
clone <begin> <end> <destination> masked
clone <begin> <end> <destination> masked force
clone <begin> <end> <destination> masked move
clone <begin> <end> <destination> masked normal
```
Which is a convenient way of quickly reaching deeper subcommands/arguments without hving to type out each term explicitly.
