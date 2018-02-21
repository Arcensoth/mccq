# Minecraft Command Query
Minecraft command query program. Inspired by the in-game help command, with added features like multiple version support and expandable regex search.


## Basic usage
Enter the CLI (command line interface) with some default version, say `18w03b`:
```bash
python -m mccq -s 18w03b
```

Start with a basic command:
```bash
> say
```

This produces some output:
```bash
# 18w03b
say <message>
```
Which will generally outline all possible variations of the command for the currently configured version(s).

Try something a little more involved:
```bash
> effect
# 18w03b
effect clear|give ...
```
The command is rolled out until a choice can be made, which saves on vertical space and is often more readable than assigning a separate line to each possibility.

## Program options
Various flags and options can be written **before the command query** to augment behaviour.

Normally several subcommands/arguments are condensed to one line, but `-e` can be used to forcibly expand the command:
```bash
> -e effect
# 18w03b
effect clear <targets>
effect clear <targets> <effect>
effect give <targets> <effect>
effect give <targets> <effect> <seconds>
effect give <targets> <effect> <seconds> <amplifier>
effect give <targets> <effect> <seconds> <amplifier> <hideParticles>
```
Be warned that this can cause a large amount of output for commands with many subcommands/arguments.

Search for specific subcommands/arguments:
```bash
> tag targets add
# 18w03b
tag <targets> add <name>
```
Arguments are shown inside `<>`, but can be searched by name just like subcommands.

Speaking of arguments, use `-t` to render their types:
```bash
> -t tag targets add
# 18w03b
tag <targets: entity> add <name: string>
```

Use `-c CAPACITY` to provide a threshold determining whether to expand a command:
```bash
> -c 6 effect
# 18w03b
effect clear <targets>
effect clear <targets> <effect>
effect give <targets> <effect>
effect give <targets> <effect> <seconds>
effect give <targets> <effect> <seconds> <amplifier>
effect give <targets> <effect> <seconds> <amplifier> <hideParticles>
```
This allows a command to expand so long as the number of subcommands/arguments it contains does not exceed the given threshold.

Use `-v VERSION` to query a particular version:
```bash
> -v 18w01a execute
# 18w01a
execute align|as|at|if|offset|run|store|unless ...
```

Repeat `-v VERSION` to query several versions at once:
```bash
> -v 18w01a -v 18w02a execute
# 18w01a
execute align|as|at|if|offset|run|store|unless ...
# 18w02a
execute align|anchored|as|at|facing|if|in|positioned|rotated|run|store|unless ...
```

## Dynamic search
Each search term of the provided `command` is treated as a regex pattern, meaning any number of subcommands/arguments can be flexibly queried:
```bash
> execute a.*
# 18w03b
execute align <axes> -> execute
execute anchored <anchor> -> execute
execute as <targets> -> execute
execute at <targets> -> execute
```

Going even deeper:
```bash
> execute a.* targets
# 18w03b
execute as <targets> -> execute
execute at <targets> -> execute
```

Search terms are case-insensitive:
```bash
> gamerule domob.*
# 18w03b
gamerule doMobLoot
gamerule doMobLoot <value>
gamerule doMobSpawning
gamerule doMobSpawning <value>
```

Special-case: a single `.` is treated as a wildcard, matching all subcommands/arguments:
```bash
> clone . . . masked
# 18w03b
clone <begin> <end> <destination> masked
clone <begin> <end> <destination> masked force
clone <begin> <end> <destination> masked move
clone <begin> <end> <destination> masked normal
```
Which is a convenient way of quickly diving into the command without having to explicitly type out each term.
