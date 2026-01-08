@echo off
echo Copying binary dependencies...

set BIN64=Bin64
set TARGET=%~1

REM Native binary dependencies
xcopy /Q /D /Y /-I "Bin64\AnselSDK64.dll" "%TARGET%\AnselSDK64.dll"
xcopy /Q /D /Y /-I "Bin64\EOSSDK-Shipping.dll" "%TARGET%\EOSSDK-Shipping.dll"
xcopy /Q /D /Y /-I "Bin64\GfnRuntimeSdk.dll" "%TARGET%\GfnRuntimeSdk.dll"
xcopy /Q /D /Y /-I "Bin64\GFSDK_Aftermath_Lib.x64.dll" "%TARGET%\GFSDK_Aftermath_Lib.x64.dll"
xcopy /Q /D /Y /-I "Bin64\Havok.dll" "%TARGET%\Havok.dll"
xcopy /Q /D /Y /-I "Bin64\msvcp110.dll" "%TARGET%\msvcp110.dll"
xcopy /Q /D /Y /-I "Bin64\msvcp120.dll" "%TARGET%\msvcp120.dll"
xcopy /Q /D /Y /-I "Bin64\msvcr110.dll" "%TARGET%\msvcr110.dll"
xcopy /Q /D /Y /-I "Bin64\msvcr120.dll" "%TARGET%\msvcr120.dll"
xcopy /Q /D /Y /-I "Bin64\Optick.dll" "%TARGET%\Optick.dll"
xcopy /Q /D /Y /-I "Bin64\opus.dll" "%TARGET%\opus.dll"
xcopy /Q /D /Y /-I "Bin64\RecastDetour.dll" "%TARGET%\RecastDetour.dll"
xcopy /Q /D /Y /-I "Bin64\steam_api64.dll" "%TARGET%\steam_api64.dll"

REM Managed binary dependencies
xcopy /Q /D /Y /-I "Bin64\VRage.Native.dll" "%TARGET%\VRage.Native.dll"
xcopy /Q /D /Y /-I "Bin64\HavokWrapper.dll" "%TARGET%\HavokWrapper.dll"
xcopy /Q /D /Y /-I "Bin64\EmptyKeys.UserInterface.dll" "%TARGET%\EmptyKeys.UserInterface.dll"
xcopy /Q /D /Y /-I "Bin64\EmptyKeys.UserInterface.Core.dll" "%TARGET%\EmptyKeys.UserInterface.Core.dll"
xcopy /Q /D /Y /-I "Bin64\RecastDetourWrapper.dll" "%TARGET%\RecastDetourWrapper.dll"
xcopy /Q /D /Y /-I "Bin64\EOSSDK.dll" "%TARGET%\EOSSDK.dll"
xcopy /Q /D /Y /-I "Bin64\CppNet.dll" "%TARGET%\CppNet.dll"
