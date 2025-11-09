""" Makes bulk fixes to the decompiled projects
"""
import os
import re
import sys
from contextlib import contextmanager
from enum import Enum
from typing import Iterator, ContextManager, Optional, Dict, Iterable, Union, Callable, Set, List
import xml.etree.ElementTree as ET

RegExp = re.Pattern[str]
Replacement = Union[str, Callable[[RegExp], str]]

EXPECTED_GAME_VERSION = 1207022
GAME_VERSION_STRING = f'SE_VERSION = {EXPECTED_GAME_VERSION}'

RX_TARGET_FRAMEWORK = re.compile(r'<TargetFramework>.*?</TargetFramework>')
TARGET_FRAMEWORK = '<TargetFramework>net8.0-windows</TargetFramework>'

NUGET_PACKAGES = {
    'System.Buffers': (
        '<PackageReference Include="System.Buffers" Version="4.5.1" />',
    ),
    'System.Memory': (
        '<PackageReference Include="System.Memory" Version="4.5.5" />',
    ),
    'System.Management': (
        '<PackageReference Include="System.Management" Version="4.5.0" />',
    ),
    'System.Management.dll': (
        '<PackageReference Include="System.Management" Version="4.5.0" />',
    ),
    'System.ComponentModel.Annotations': (
        '<PackageReference Include="System.ComponentModel.Annotations" Version="4.6.0" />',
    ),
    'System.Runtime.CompilerServices.Unsafe': (
        '<PackageReference Include="System.Runtime.CompilerServices.Unsafe" Version="6.0.0" />',
    ),
    'System.Collections.Immutable': (
        '<PackageReference Include="System.Collections.Immutable" Version="8.0.0" />',
    ),
    'System.Configuration.Install': (
        '<PackageReference Include="Core.System.Configuration.Install" Version="1.1.0" />',
    ),
    'ProtoBuf.Net': (
        '<PackageReference Include="protobuf-net" Version="3.0.131" />',
    ),
    'ProtoBuf.Net.Core': (
        '<PackageReference Include="protobuf-net.Core" Version="3.0.131" />',
    ),
    'SharpDX': (
        '<PackageReference Include="SharpDX" Version="4.2.0" />',
    ),
    'SharpDX.XAudio2': (
        '<PackageReference Include="SharpDX.XAudio2" Version="4.2.0" />',
    ),
    'SharpDX.Desktop': (
        '<PackageReference Include="SharpDX.Desktop" Version="4.2.0" />',
    ),
    'SharpDX.Direct3D11': (
        '<PackageReference Include="SharpDX.Direct3D11" Version="4.2.0" />',
    ),
    'SharpDX.DirectInput': (
        '<PackageReference Include="SharpDX.DirectInput" Version="4.2.0" />',
    ),
    'SharpDX.DXGI': (
        '<PackageReference Include="SharpDX.DXGI" Version="4.2.0" />',
    ),
    'SharpDX.D3DCompiler': (
        '<PackageReference Include="SharpDX.D3DCompiler" Version="4.2.0" />',
    ),
    'SharpDX.XInput': (
        '<PackageReference Include="SharpDX.XInput" Version="4.2.0" />',
    ),
    'Microsoft.CodeAnalysis': (
        '<PackageReference Include="Microsoft.CodeAnalysis" Version="4.11.0" />',
    ),
    'Microsoft.CodeAnalysis.CSharp': (
        '<PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.11.0" />',
    ),
    'DirectShowLib': (
        '<PackageReference Include="DirectShowLib" Version="1.0.0" />',
    ),
    'GameAnalytics.Mono': (
        '<PackageReference Include="GameAnalytics.Mono.SDK" Version="3.3.5" />',
    ),
    'RestSharp': (
        '<PackageReference Include="RestSharp" Version="106.6.10" />',
    ),
    'Steamworks.NET': (
        '<PackageReference Include="Steamworks.NET" Version="20.1.0" />',
    ),
    'SixLabors.Core': (
    ),
    'SixLabors.ImageSharp': (
        '<PackageReference Include="SixLabors.ImageSharp" Version="3.1.5" />',
    ),
    'Newtonsoft.Json': (
        '<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />',
    ),
}

SIMPLE_REPLACEMENTS = [
    ('[Nullable]',
     '[VRage.Serialization.Nullable]'),

    ('public sealed void Invoke(',
     'public void Invoke('),

    ('public virtual sealed void Set(',
     'public virtual void Set('),

    ('public virtual sealed void Get(',
     'public virtual void Get('),

    ('public virtual sealed ISyncType Compose(',
     'public virtual ISyncType Compose('),
]

REGEX_REPLACEMENTS = [
    ('class Sandbox_Engine_Multiplayer_',
     re.compile(r'(\s*)protected (class Sandbox_Engine_Multiplayer_[A-Za-z0-9_]+Msg.*)'),
     r'\1private \2'),

    ('CreateInstance',
     re.compile(r'(\s*)(?:protected|private) virtual sealed ([A-Za-z0-9_]+(?:<T>|<TYPE>)? CreateInstance.*)'),
     r'\1protected virtual \2'),

    (' = (Sync<',
     re.compile(r'(\s*\(\([A-Za-z_][A-Za-z0-9_]*\)[A-Za-z_][A-Za-z0-9_]*\)\.[A-Za-z_][A-Za-z0-9_]*)(\s*=\s*\(Sync<[^,]+,\s*SyncDirection\.[A-Za-z_][A-Za-z0-9_]*>\)[A-Za-z_][A-Za-z0-9_]*;\s*)'),
     r'\1.Value\2'),
]

CONTEXT_RULES = {
    'class': re.compile(r'.*?(private|protected|internal|public) (new )?(sealed )?class [A-Za-z0-9_]+?.*'),
    'struct': re.compile(r'.*?(private|protected|internal|public) (new )?(sealed )?struct [A-Za-z0-9_]+?.*'),
}

REGEX_REPLACEMENTS_IN_CONTEXT = [
    # Inside a class the member classes must be protected
    ('class',
     'Accessor : IMemberAccessor<',
     re.compile(r'(\s*)private (class Medieval_.*?Accessor : IMemberAccessor<.*)'),
     r'\1protected \2'),
    ('class',
     'Accessor : IMemberAccessor<',
     re.compile(r'(\s*)private (class VRage_.*?Accessor : IMemberAccessor<.*)'),
     r'\1protected \2'),

    # Inside a struct the member classes must be private
    ('struct',
     'Accessor : IMemberAccessor<',
     re.compile(r'(\s*)protected (class [A-Za-z0-9_]+Accessor : IMemberAccessor<.*)'),
     r'\1private \2'),
]

DELETE_BLOCKS = [
    ('VRage_Library_Collections_MyList_',
     re.compile(r'.*?class VRage_Library_Collections_MyList_.*?Accessor : IMemberAccessor<.*')),

    ('VRage_Library_Collections_NativeDictionary_',
     re.compile(r'.*?class VRage_Library_Collections_NativeDictionary_.*?Accessor : IMemberAccessor<.*')),

    ('VRage_Serialization_SerializableDictionaryHack_',
     re.compile(r'.*?class VRage_Serialization_SerializableDictionaryHack_.*?Accessor : IMemberAccessor<.*')),

    ('VRageMath_Color_',
     re.compile(r'.*?class VRageMath_Color_.*?Accessor : IMemberAccessor<.*')),

    ('VRageMath_PackedVector_HalfVector4_',
     re.compile(r'.*?class VRageMath_PackedVector_HalfVector4_.*?Accessor : IMemberAccessor<.*')),

    ('VRage_Serialization_SerializableDictionaryHack_',
     re.compile(r'.*?class VRage_Serialization_SerializableDictionaryHack_.*?Accessor : IMemberAccessor<.*')),

    ('VRage_Library_Collections_MyList_',
     re.compile(r'.*?class VRage_Library_Collections_MyList_.*?Accessor : IMemberAccessor<.*')),
]

RX_ACTIVATOR_CLASS = re.compile(r'\s*private\s+class\s+(\w+)(?:<\w+>)?\s*:\s*IActivator,\s*IActivator<(\w+(?:<\w+>)?)>\s*')

ACTIVATOR_CLASS_TEMPLATE = '''\
private class %(activator_type)s : IActivator, IActivator<%(game_type)s>
{
    object IActivator.CreateInstance() => (object) new %(game_type)s();
    %(game_type)s IActivator<%(game_type)s>.CreateInstance() => new %(game_type)s();
}'''


class ProjectFileProcessors:

    def normalize_element(element: ET.Element) -> str:
        element_str = ET.tostring(element, encoding='unicode')
        return re.sub(r'\s+', ' ', element_str).strip()

    def sort_group_children(group: ET.Element) -> None:
        children = list(group)
        if not children:
            return

        for child in list(group):
            group.remove(child)

        children.sort(key=ProjectFileProcessors.normalize_element)

        for child in children:
            group.append(child)

    def process_project_file(xml_content: str) -> str:
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()

        groups = root.findall(".//PropertyGroup") + root.findall(".//ItemGroup")
        for group in groups:
            ProjectFileProcessors.sort_group_children(group)

        ET.indent(tree, space="  ")

        result = ET.tostring(root, encoding='unicode')
        return result


class LineProcessor:
    class Context:
        def __init__(self, rules: Dict[str, RegExp]):
            self.rules = rules
            self.stack = []

        def update(self, line: str) -> None:
            depth = len(line) - len(line.lstrip())
            for rule_name, rx in self.rules.items():
                m = rx.match(line)
                if m is not None:
                    self.stack.append((depth, rule_name))
            if self.stack:
                if line.strip() == '}' and depth == self.stack[-1][0]:
                    self.stack.pop()

        def is_in_context(self, rule_name):
            return self.stack and self.stack[-1][1] == rule_name

    @staticmethod
    def remove_blocks(quick_search_text: str, rx_first_line: RegExp, lines: Iterable[str]) -> Iterator[str]:
        end: str = ''
        tail: bool = False
        skip: bool = False
        for line in lines:

            if skip and tail:
                if not line.strip():
                    continue
                skip = False

            if skip and not end:
                end = line.replace('{', '}')
                continue

            if skip:
                if line == end:
                    tail = True
                continue

            if quick_search_text in line and rx_first_line.match(line):
                skip = True
                tail = False
                end = ''
                continue

            yield line

    @staticmethod
    def rewrite_activators(lines: Iterable[str]) -> Iterator[str]:
        skip = False
        end = ''
        for line in lines:

            if skip:
                if line == end:
                    skip = False
                    end = ''
                continue

            m = RX_ACTIVATOR_CLASS.match(line)
            if m is None:
                yield line
                continue

            indent_size = len(line) - len(line.lstrip())
            indent = line[:indent_size]
            end = indent + '}'
            skip = True

            kws = dict(activator_type=m.group(1), game_type=m.group(2))
            replacement_class_definition = ACTIVATOR_CLASS_TEMPLATE % kws
            yield from (indent + replacement_line for replacement_line in replacement_class_definition.split('\n'))

    @staticmethod
    def regex_replace(quick_search_text: str, regex: RegExp, replacement: str, lines: Iterable[str]) -> Iterator[str]:
        for line in lines:
            if quick_search_text not in line:
                yield line
                continue

            m = regex.match(line)
            if m is None:
                yield line
                continue

            yield regex.subn(replacement, line)[0]

    @staticmethod
    def regex_replace_in_context(rules: Dict[str, RegExp], ctx_rule_name: str, quick_search_text: str, regex: RegExp, replacement: str, lines: Iterable[str]) -> Iterator[str]:
        ctx = LineProcessor.Context(rules)
        for line in lines:
            if quick_search_text not in line or not ctx.is_in_context(ctx_rule_name):
                yield line
                ctx.update(line)
                continue

            m = regex.match(line)
            if m is None:
                yield line
                ctx.update(line)
                continue

            yield regex.subn(replacement, line)[0]
            ctx.update(line)

    @staticmethod
    def split_long_if_else(method: str, start: str, lines: Iterable[str]) -> Iterator[str]:
        class State(Enum):
            SEARCHING = 'SEARCHING'
            METHOD_FOUND = 'METHOD_FOUND'
            IF_ELSE = 'IF_ELSE'
            ELSE = 'ELSE'
            IN_CLAUSE = 'IN_CLAUSE'
            IN_ELSE_CLAUSE = 'IN_ELSE_CLAUSE'
            END_OF_CLAUSE = 'END_OF_CLAUSE'
            FINISHED = 'FINISHED'

        state = State.SEARCHING

        begin = ''
        end = ''
        indent = ''
        if_ = ''
        else_if = ''
        else_ = ''
        depth = 0
        lineno = 0

        for line in lines:
            lineno += 1

            depth += line.count('{')
            depth -= line.count('}')

            match state:

                case State.FINISHED:
                    yield line

                case State.SEARCHING:
                    if method in line:
                        state = State.METHOD_FOUND
                    yield line

                case State.METHOD_FOUND:
                    if 'BEGIN COMPILER WORKAROUND' in line:
                        state = State.FINISHED
                    elif start in line:
                        state = State.IF_ELSE
                        assert line.startswith('\t'), repr(line)
                        indent = '\t' * (len(line) - len(line.lstrip('\t')))
                        if_ = f'{indent}if'
                        else_if = f'{indent}else if'
                        else_ = f'{indent}else'
                        depth = 0
                        yield ''
                        yield f'{indent}do {{ // BEGIN COMPILER WORKAROUND'
                        yield ''
                    yield line

                case State.IF_ELSE:
                    assert depth == 1, (lineno, depth)
                    if not begin:
                        assert line.strip() == '{', repr(line)
                        begin = line
                        end = line.replace('{', '}')
                    state = State.IN_CLAUSE
                    yield line

                case State.ELSE:
                    assert depth == 0, (lineno, depth)
                    state = State.IN_ELSE_CLAUSE
                    yield line

                case State.IN_CLAUSE:
                    if line == end:
                        state = State.END_OF_CLAUSE
                        yield f'{indent}\tbreak;'
                    yield line

                case State.IN_ELSE_CLAUSE:
                    yield line
                    if line == end:
                        state = State.FINISHED
                        yield ''
                        yield f'{indent}}} while(false); // END COMPILER WORKAROUND'
                        yield ''

                case State.END_OF_CLAUSE:
                    assert depth == 0, (lineno, depth)
                    if line.startswith(else_if):
                        state = State.IN_CLAUSE
                        yield f'{if_}{line[len(else_if):]}'
                    elif line.startswith(else_):
                        state = State.IN_ELSE_CLAUSE
                        yield line
                    else:
                        state = State.FINISHED
                        yield line


class Project:

    @classmethod
    def iter(cls) -> Iterator['Project']:
        for name in os.listdir('.'):
            if os.path.isdir(name) and os.path.exists(f'{name}/{name}.csproj'):
                yield cls(name)

    def __init__(self, name: str):
        super().__init__()
        self.name: str = name
        self.project_file: Optional[str] = None
        self.project_file_original: Optional[str] = None
        self.sources: Dict[str, str] = {}
        self.sources_original: Dict[str, str] = {}
        self.project_dependencies: Set[str] = set()

    @property
    def project_dir(self) -> str:
        return self.name

    @property
    def project_file_path(self) -> str:
        return f'{self.name}/{self.name}.csproj'

    def iter_sources(self) -> str:
        for dirpath, dirnames, filenames in os.walk(self.project_dir):
            for filename in filenames:
                if not filename.endswith('.cs'):
                    continue
                yield os.path.join(dirpath, filename)

    def load(self) -> None:
        with open(self.project_file_path, 'rt', encoding='utf-8') as f:
            self.project_file = f.read()

        self.project_file_original = self.project_file

        self.sources.clear()
        for path in self.iter_sources():
            if path.endswith('.csproj'):
                continue
            with open(path, 'rt', encoding='utf-8') as f:
                try:
                    self.sources[path] = f.read()
                except Exception:
                    print(f'Failed to read source file: {path}')
                    raise

        self.sources_original = self.sources.copy()

    def save(self) -> None:
        if self.project_file != self.project_file_original:
            with open(self.project_file_path, 'wt', encoding='utf-8') as f:
                f.write(self.project_file)

        for path, source in self.sources.items():
            original = self.sources_original[path]
            if source != original:
                with open(path, 'wt', encoding='utf-8') as f:
                    f.write(source)

        self.discard()

    def discard(self) -> None:
        self.project_file = None
        self.project_file_original = None

        self.sources.clear()
        self.sources_original.clear()

    @contextmanager
    def read(self) -> ContextManager:
        assert self.project_file is None
        self.load()
        yield
        self.discard()

    @contextmanager
    def write(self) -> ContextManager:
        assert self.project_file is None
        self.load()
        yield
        self.save()

    def replace_in_project_file(self, a, b):
        self.project_file = self.project_file.replace(a, b)

    def regex_replace_in_project_file(self, rx: RegExp, replacement: Replacement):
        self.project_file = rx.subn(replacement, self.project_file)[0]

    def replace_target_framework(self):
        self.project_file = RX_TARGET_FRAMEWORK.subn(TARGET_FRAMEWORK, self.project_file)[0]

    def fix_obsolete_sdk(self):
        self.replace_in_project_file(
            '<Project Sdk="Microsoft.NET.Sdk.WindowsDesktop">',
            '<Project Sdk="Microsoft.NET.Sdk">'
        )

    def delete_source_blocks(self, quick_search_text: str, rx_first_line: RegExp) -> None:
        for path in self.sources:
            source = self.sources[path]
            if quick_search_text not in source:
                continue
            self.sources[path] = '\n'.join(LineProcessor.remove_blocks(quick_search_text, rx_first_line, source.split('\n')))

    def replace_in_source_files(self, original: str, replacement: str):
        for path in self.sources:
            self.sources[path] = self.sources[path].replace(original, replacement)

    def regex_replace_in_source_lines(self, quick_search_text: str, regex: RegExp, replacement: str):
        for path in self.sources:
            source = self.sources[path]
            if quick_search_text not in source:
                continue
            self.sources[path] = '\n'.join(LineProcessor.regex_replace(quick_search_text, regex, replacement, source.split('\n')))

    def regex_replace_in_source_lines_in_context(self, ctx_rule_name: str, quick_search_text: str, regex: RegExp, replacement: str):
        for path in self.sources:
            source = self.sources[path]
            if quick_search_text not in source:
                continue
            self.sources[path] = '\n'.join(LineProcessor.regex_replace_in_context(CONTEXT_RULES, ctx_rule_name, quick_search_text, regex, replacement, source.split('\n')))

    def rewrite_activators(self):
        for path in self.sources:
            source = self.sources[path]
            if 'object IActivator.CreateInstance()' not in source:
                continue
            self.sources[path] = '\n'.join(LineProcessor.rewrite_activators(source.split('\n')))

    def add_project_references(self, projects: Iterable['Project']) -> None:
        for project in projects:
            rx_dll_reference = re.compile(rf'<Reference Include="{project.name}">\s*<HintPath>../Bin64/{project.name}.dll</HintPath>\s*</Reference>', re.DOTALL)
            project_reference = lambda m: rf'<ProjectReference Include="..\{project.name}\{project.name}.csproj" />'
            self.regex_replace_in_project_file(rx_dll_reference, project_reference)

    def fix_nuget_dependencies(self):
        for dll_name, nuget_references in NUGET_PACKAGES.items():
            rx_dll_reference = re.compile(rf'<Reference Include="{dll_name}">\s*<HintPath>.*?Bin64[\\/]{dll_name}.dll</HintPath>\s*</Reference>', re.DOTALL)
            package_reference = lambda m: '\n    '.join(nuget_references)
            self.regex_replace_in_project_file(rx_dll_reference, package_reference)

    def store_project_dependencies(self, projects: Iterable['Project']):
        for project in projects:
            if rf'<ProjectReference Include="..\{project.name}\{project.name}.csproj" />' in self.project_file:
                self.project_dependencies.add(project.name)

    def fix_long_if_else(self, path: str, method: str, start: str):
        path = path.replace('/', '\\')
        source = self.sources[path]
        self.sources[path] = '\n'.join(LineProcessor.split_long_if_else(method, start, source.split('\n')))

    def fix_hint_paths(self):
        self.regex_replace_in_project_file(re.compile(r'<HintPath>(..[\\/])?Bin64[\\/]'), '<HintPath>../Bin64/')

    def sort_project_items(self):
        """Sorting the project items which can be in any random order after decompilation
        Sorting them ensures that the diff containing the manual fixes can be applied.
        """
        self.project_file = ProjectFileProcessors.process_project_file(self.project_file)


def verify_game_version(project_map: Dict[str, Project]):
    project = project_map['SpaceEngineers.Game']
    with project.read():
        source = project.sources[r'SpaceEngineers.Game\SpaceEngineers\Game\SpaceEngineersGame.cs']
        if GAME_VERSION_STRING not in source:
            print(f'Incompatible game version. Expected: {EXPECTED_GAME_VERSION}')
            sys.exit(-1)


def fix_project_files_and_code(projects: List[Project]):
    for project in projects:
        print(f'- {project.name}')
        with project.write():
            project.replace_target_framework()
            project.fix_obsolete_sdk()

            project.fix_hint_paths()
            project.add_project_references(projects)
            project.fix_nuget_dependencies()

            for original, replacement in SIMPLE_REPLACEMENTS:
                project.replace_in_source_files(original, replacement)

            for quick_search_text, regex, replacement in REGEX_REPLACEMENTS:
                project.regex_replace_in_source_lines(quick_search_text, regex, replacement)

            for ctx_rule_name, quick_search_text, regex, replacement in REGEX_REPLACEMENTS_IN_CONTEXT:
                project.regex_replace_in_source_lines_in_context(ctx_rule_name, quick_search_text, regex, replacement)

            for quick_search_text, regex in DELETE_BLOCKS:
                project.delete_source_blocks(quick_search_text, regex)

            project.rewrite_activators()
            project.sort_project_items()
            project.store_project_dependencies(projects)


def split_long_xml_serializers(project_map: Dict[str, Project]):
    project = project_map['VRage.Game.XmlSerializers']
    with project.write():
        path = 'VRage.Game.XmlSerializers/Microsoft/Xml/Serialization/GeneratedAssembly/XmlSerializationWriter1.cs'
        project.fix_long_if_else(
            path,
            'private void Write3184_Object(string n, string ns, object o, bool isNullable, bool needType)',
            'if (type == typeof(MyAtmosphereSettings))'
        )
        project.fix_long_if_else(
            path,
            'private void Write3716_Object(string n, string ns, object o, bool isNullable, bool needType)',
            'if (type == typeof(SerializableDictionary<ulong, int>))'
        )
        project.fix_long_if_else(
            path,
            'private void Write2649_Object(string n, string ns, object o, bool isNullable, bool needType)',
            'if (type == typeof(SerializableDictionary<string, object>))'
        )


def print_project_dependencies(projects: List[Project]):
    for project in projects:
        print(f'- {project.name}:')
        for dependency in sorted(project.project_dependencies):
            print(f'  - {dependency}')


def print_build_plan(project_map: Dict[str, Project]):
    remaining: Set[str] = set(project_map)
    while remaining:
        print('Parallel:')
        already_built = set(project_map) - remaining
        buildable = {name for name in remaining if not (project_map[name].project_dependencies - already_built)}
        for name in sorted(buildable):
            print(f'  - {name}')
        remaining.difference_update(buildable)


def main():
    projects = list(Project.iter())
    projects.sort(key=lambda p: p.name)
    project_map: Dict[str, Project] = {project.name: project for project in projects}

    print('Verifying game version')
    verify_game_version(project_map)

    print('Fixing project files and source code:')
    fix_project_files_and_code(projects)
    print()

    print('Fixing long XML serializers')
    split_long_xml_serializers(project_map)

    print('Project dependencies:')
    print_project_dependencies(projects)
    print()

    print('Build plan:')
    print()
    print_build_plan(project_map)
    print()


if __name__ == '__main__':
    main()
