# How to run Space Engineers on .NET 8.0

For support please [join the SE Mods Discord](https://discord.gg/PYPFPGf3Ca).

**Please consider supporting my work on [Patreon](https://www.patreon.com/semods) or a one time donation via [PayPal](https://www.paypal.com/paypalme/vferenczi/).**

*Thank you and enjoy!*

## What's this?

This repository provides a way to decompile the game into C# 11.0 source
code in several projects, combined into a single solution. It also 
contains a script and patches to fix the code to run on .NET 8.0.

## Legal

_Space Engineers is a trademark of Keen Software House s.r.o._

_I have no affiliation with Keen Software House._

### Warning for players

This repository contains an advanced development tool.
If you are only playing Space Engineers and not developing for it,
then you **should not** use this repository in any way.
Play the original game as it is installed by Steam.

### Disclaimer

The method described in this repository is completely unsupported
by the game's developer. Use it only at your own risk.

**Do not** report any bugs based on running the game this way,
unless the exact same issue is reproducible in the original game.

If decompiling software for your own personal learning, research,
testing or debugging purposes is against the law in your country,
then do not use this repository. 

**Never** publish the decompiled source code, including, but not
limited to uploading it to publicly available source code repositories.

## Prerequisites

- [.NET 8.0 SDK, Windows x64](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
- [JetBrains Rider](https://www.jetbrains.com/rider/) or Microsoft Visual Studio
- [ILSpy]() version 8.2.0.7535 - Install by running `SetupILSpy.bat`
- [Python 3.12](https://python.org) or newer
- [Git](https://gitforwindows.org/) to create a **local** repository 

Make sure these executables are available on `PATH`:
- `ilspycmd`
- `python`
- `git`

## Usage

1. Create a new git repository in an empty folder: `git init`
2. Copy over all files from this repository (do **not** overwrite `.git`)
3. Commit: `git add .` then `git commit -m "Initial"`
4. Edit and run `LinkBin64.bat` to link the game's `Bin64` folder
5. Decompile the game (10-20 minutes): `Decompile.bat`
6. Commit: `git add .` then `git commit -m "Game Version"`
7. Make the bulk fixes: `python FixBulk.py`
8. Commit: `git add .` then `git commit -m "Bulk fixes"`
9. Copy the `ReplicatedTypes.json` file into the `VRage` folder
10. Commit: `git add .` then `git commit -m "Replicated types"`
11. Apply the code patches (whitespace warnings are normal): `git apply -p1 --whitespace=fix Manual_fixes.patch`
12. Commit: `git add .` then `git commit -m "Manual fixes"`
13. Open the solution in your IDE
14. Force a NuGet Restore for the whole solution
15. Make a `Debug` build and run it

The above steps have not been automated by a single script in order to 
give greater control over the process and awareness of the version
control involved, so you can revert and try again if needed.

_Enjoy!_

### Build targets

`Debug` builds are running a bit slower than normal due to the lack
of code optimization, but still usable for development/research.

`Release` builds should also work and provide the usual performance. 
Release builds are less debuggable due to code optimization, you
may not be able to break the code everywhere and some variable
values may not be observable.

You can build and run a `Release` build from the command line by
executing the `BuildAndRun.bat` script. It should work without an IDE.

## Expected use cases

**Investigating game bugs and performance issues** directly without 
continuously waiting on the decompiler. Being able to quickly navigate 
the code and even change it at runtime. You can see all variable values 
and can break the code anywhere if you run a `Debug` build.

**Prototyping plugins** by directly changing the game's source code. Once it
works and tested, it can be turned into a plugin usable on Plugin Loader. 
Combined with publicizer support (yet to be accepted to PL) it can be a 
powerful way to develop new plugins.
 
## Remarks

### Disabled code

- The game analytics is disabled, because its logging broke. We don't want to confuse Keen's telemetry with our custom builds anyway.
- The script performance profiling is disabled, because it broke the script compiler. It has not been fixed, because without game analytics it is pointless to have anyway.

### Ceveats

- There is no compatible Plugin Loader, currently
- Transpiler patches would likely break even if you could load plugins

### How the manual patch was made?

```shell
git format-patch -1 HEAD --stdout >Manual_fixes.patch
```

## Credits

*In alphabetical order*

### Patreon

#### Admiral level supporters
- BetaMark
- Bishbash777
- Casinost
- Dorimanx
- wafoxxx

#### Captain level supporters
- DontFollowOrders
- Gabor
- Lazul
- Lotan
- mkaito
- ransomthetoaster
- Raidfire

### Developers
- zznty: motivation, slight hints into the right direction

## Troubleshooting

### Dependencies appear to be missing

Make sure you have the `Bin64` folder linked to your solution folder.
If it is not there, then run `LinkBin64.bat` to restore it.