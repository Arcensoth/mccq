# Minecraft Command Query
Minecraft command query program. Inspired by the in-game help command, with added features like version reporting and expandable regex search.

## Program options
Start with a basic command:
```bash
# mccq tag

tag <targets> add|list|remove ...  # 18w03b
```
Notice how the command is expanded until more than one subcommand/argument is found. At this point, subcommands/arguments are concatenated on the same line rather than producing a separate line for each one. This saves a considerable amount of space for commands like `gamerule` that have many subcommands.

Choose one of the subcommands:
```bash
# mccq tag targets add

tag <targets> add <name>  # 18w03b
```

Use `-t` to render argument types:
```bash
# mccq -t tag targets add

tag <targets: entity> add <name: string>  # 18w03b
```

Use `-e` to expand all subcommands, bypassing capacity:
```bash
# mccq -e tag

# 18w03b
tag <targets> add <name>
tag <targets> list
tag <targets> remove <name>
```

Use `-c CAPACITY` to provide a threshold determining whether to expand subcommands:
```bash
# mccq -c 3 tag

# 18w03b
tag <targets> add <name>
tag <targets> list
tag <targets> remove <name>
```

Use `-v VERSION` to specify a particular version to query:
```bash
# mccq -v 18w01a execute

execute align|as|at|if|offset|run|store|unless ...  # 18w01a
```

Use multiple `-v VERSION` to query several versions at once:
```bash
# mccq -v 18w01a -v 18w02a execute

execute align|as|at|if|offset|run|store|unless ...  # 18w01a
execute align|anchored|as|at|facing|if|in|positioned|rotated|run|store|unless ...  # 18w02a
```

## Regex search
Each search term of the provided `command` is treated as a regex pattern, meaning any number of subcommands and arguments can be queried dynamically:
```bash
# mccq execute a.*

# 18w03b
execute align <axes> -> execute
execute anchored <anchor> -> execute
execute as <targets> -> execute
execute at <targets> -> execute
```

Searching for multiple subcommands/arguments:
```bash
# mccq execute a.* targets

# 18w03b
execute as <targets> -> execute
execute at <targets> -> execute
```

Search terms are case-insensitive:
```bash
# mccq gamerule domob.*

# 18w03b
gamerule doMobLoot
gamerule doMobLoot <value>
gamerule doMobSpawning
gamerule doMobSpawning <value>
```

There is a special-case: a single `.` is treated as a wildcard. Basically it just turns into `.*`, which will match any term:
```bash
# mccq clone . . . masked

# 18w03b
clone <begin> <end> <destination> masked
clone <begin> <end> <destination> masked force
clone <begin> <end> <destination> masked move
clone <begin> <end> <destination> masked normal
```
Which is preferable for quickly reaching subcommands, over explicitly typing out each term.