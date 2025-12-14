# How to run Space Engineers on .NET 8.0

For support please [join the SE Mods Discord](https://discord.gg/PYPFPGf3Ca).

**Please consider supporting my work on [Patreon](https://www.patreon.com/semods) or a one time donation via [PayPal](https://www.paypal.com/paypalme/vferenczi/).**

*Thank you and enjoy!*

## What's this?

This repository provides a way to decompile the game into C# 11.0 source
code in several projects, combined into a single solution. It also 
contains a script and patches to fix the code to run on .NET 8.0.

See also: [Plugin Loader on .NET 8.0](https://github.com/viktor-ferenczi/se-dotnet-plugin-loader)

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

- **Space Engineers** installed via Steam
- [.NET 8.0 SDK, Windows x64](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
- [JetBrains Rider](https://www.jetbrains.com/rider/) or Microsoft Visual Studio
- [ILSpy](https://github.com/icsharpcode/ILSpy) version 8.2.0.7535 - Install it by running `SetupILSpy.bat`
- [Python 3.12](https://python.org) or newer
- [Git](https://gitforwindows.org/) to create a **local** repository 

Make sure these executables are available on `PATH`:
- `ilspycmd`
- `python`
- `git`

Define this environment variable: `SPACE_ENGINEERS_ROOT`
- Usual value: `C:\Program Files (x86)\Steam\steamapps\common\SpaceEngineers`
- If you installed the game at a custom path, then use that path.

## Usage

Run `Prepare.bat`, it should take about 10-20 minutes to complete.

It should print `DONE` at the end. If it prints `FAILED`, then investigate
the console output and try again. This script is designed to be retryable,
but it requires reverting the working copy to the latest commit beforehand.

You can then open and built the project in your C# IDE (Rider, Visual Studio).

Alternatively you can build and run a `Release` build from the command line by
executing the `BuildAndRun.bat` script. It should work without an IDE.

_Enjoy!_

### Build targets

`Debug` builds are running a bit slower than normal due to the lack
of code optimization, but still usable for development/research.

`Release` builds should also work and provide the usual performance. 
Release builds are less debuggable due to code optimization, you
may not be able to break the code everywhere and some variable
values may not be observable.

## Expected use cases

**Investigating game bugs and performance issues** directly without 
continuously waiting on the decompiler. Being able to quickly navigate 
the code and even change it at runtime. You can see all variable values 
and can put breakpoints anywhere in the code if you run a `Debug` build.

**Prototyping plugins** by directly changing the game's source code. Once it
works and tested, it can be turned into a plugin to publish on Pulsar. 
Combined with publicizer support it is a powerful way to develop plugins.

## Remarks

### Pulsar

TBD: Pulsar support for .NET 8/9

`(((`

_Outdated documentation which applied to Plugin Loader_

You can use the modified [Plugin Loader on .NET 8.0](https://github.com/viktor-ferenczi/se-dotnet-plugin-loader).
Please see the instructions there.

Please note, that plugins using transpiler patches or verifying the bytecode would likely break.
Incompatible plugins could be made compatible with the .NET 8.0 build of the game, they just need some work.
The plugin authors may make them available at their discretion either as an alternate version or by using
runtime conditions on the IL code.

`)))`

### Disabled code

- The game analytics is disabled, because its logging broke. We don't want to confuse Keen's telemetry with our custom builds anyway.
- The script performance profiling is disabled, because it broke the script compiler. It has not been fixed, because without game analytics it is pointless to have anyway.

### How to follow major game updates?

This is how I update this repository after major (and sometimes minor) game updates. 

- Always keep a **local** Git repository with `Prepare.bat` fully applied on the most recent game version supported by this repository. (You can always choose an older game version on Steam and install that one temporarily to build your local repository, should your game has already been updated since.)
- Always keep a branch for each game version, for example: `ver/1.207.022`
- Switch back to the `main` branch.
- Create a new branch for the new game version. Base it on the `Git ignore` commit of the previous game version's branch.
- Cherry-pick the `Initial` commit from the previous game version's branch.
- Use the [DotNet Dump](https://github.com/viktor-ferenczi/se-dotnet-dump) client plugin to export a new `ReplicatedTypes.json` from the game. It will be written to the `%AppData%\SpaceEngineers\DotNetDump` folder. You need to build this client plugin from sources, it is not listed on Pulsar, since it is useless for players.
- Overwrite `ReplicatedTypes.json` in your working copy with the file exported by the client plugin.
- Update the `EXPECTED_GAME_VERSION` in the `FixBulk.py` script to the current game version, keep the same number formatting.
- Commit your changes with the comment "Initial" into your branch.
- Run `Prepare.bat`, it should decompile the game without errors and apply the bulk fixes (Python script). It will likely fail to apply `Manual_fixes.patch`, which is normal due to the game code changes.
- If the patch failed, then you need to fix the game code: 
  - Cherry-pick the `Manual fixes` commit from the previous version's branch of your local repo.
  - Fix any merge conflicts. There should not be too many changes. Mostly due to ordering, renamed symbols and minor changes to the game code.
  - Run a NuGet Force Restore.
  - Make a `Debug` build and smoke test the game. Fix the code as needed until it builds and works.
  - Test a `Release` build, just to be on the safe side. It should run faster than a `Debug` build.
  - Commit your changes and squash them into a single `Manual fixes` commit. This will be the basis for a new patch and any future updates.
  - Re-generate the `Manual_fixes.patch` file as described in the next section below
  - Commit the updated `Manual_fixes.patch` file
  - Squash all your changes back into the "Initial" commit, so they are at a single place for the next update

### How the manual patch was made?

It was made from the very last commit, which contained all the code changes made manually.

```shell
git diff --binary HEAD~1..HEAD >Manual_fixes.patch
```

The file generated should be UTF-8 encoded without a BOM. Otherwise, it won't work on patching by command line git.

If it generates an UCS-16 file with a BOM, then open a new classic `cmd` window and run the command from there.

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
- Raidfire
- ransomthetoaster

### Developers

- zznty: motivation, slight hints into the right direction

## Troubleshooting

### Dependencies appear to be missing

Make sure you have the `Bin64` folder linked to your solution folder.
If it is not there, then run `LinkBin64.bat` to restore it.

### Patch application fails

It may happen that applying `Manual_fixes.patch` fails.

In this case just revert all files which may have changed, then apply the patch manually.
Once resolved, commit the changes with comment `Manual fixes`, run a NuGet Force Restore
and build the project for testing. (No need to rerun `Prepare.bat`.)
