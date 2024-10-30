set OPTIONS=--project --nested-directories --referencepath Bin64 --languageversion CSharp11_0 --disable-updatecheck

ilspycmd %OPTIONS% -o Sandbox.Common Bin64\Sandbox.Common.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o Sandbox.Game Bin64\Sandbox.Game.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o Sandbox.Game.XmlSerializers Bin64\Sandbox.Game.XmlSerializers.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o Sandbox.Graphics Bin64\Sandbox.Graphics.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o Sandbox.RenderDirect Bin64\Sandbox.RenderDirect.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o SpaceEngineers Bin64\SpaceEngineers.exe
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o SpaceEngineers.Game Bin64\SpaceEngineers.Game.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o SpaceEngineers.ObjectBuilders Bin64\SpaceEngineers.ObjectBuilders.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o SpaceEngineers.ObjectBuilders.XmlSerializers Bin64\SpaceEngineers.ObjectBuilders.XmlSerializers.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Ansel Bin64\VRage.Ansel.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Audio Bin64\VRage.Audio.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage Bin64\VRage.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.EOS Bin64\VRage.EOS.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.EOS.XmlSerializers Bin64\VRage.EOS.XmlSerializers.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Game Bin64\VRage.Game.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Game.XmlSerializers Bin64\VRage.Game.XmlSerializers.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Input Bin64\VRage.Input.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Library Bin64\VRage.Library.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Math Bin64\VRage.Math.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Math.XmlSerializers Bin64\VRage.Math.XmlSerializers.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Mod.Io Bin64\VRage.Mod.Io.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.NativeAftermath Bin64\VRage.NativeAftermath.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.NativeWrapper Bin64\VRage.NativeWrapper.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Network Bin64\VRage.Network.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Platform.Windows Bin64\VRage.Platform.Windows.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Render Bin64\VRage.Render.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Render11 Bin64\VRage.Render11.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Scripting Bin64\VRage.Scripting.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.Steam Bin64\VRage.Steam.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.UserInterface Bin64\VRage.UserInterface.dll
if %ERRORLEVEL% NEQ 0 goto failed

ilspycmd %OPTIONS% -o VRage.XmlSerializers Bin64\VRage.XmlSerializers.dll
if %ERRORLEVEL% NEQ 0 goto failed

echo Successfully decompiled the game
exit /b 0

:failed
echo Failed to decompile the game
exit /b 1
