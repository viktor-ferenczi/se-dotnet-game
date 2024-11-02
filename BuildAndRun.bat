@set SolutionDir=%cd%
dotnet run --configuration Release --project SpaceEngineers -- -skipintro >build.log 2>&1
