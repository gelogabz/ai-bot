import os

# Try to import google.genai types for schema declaration; tests/envs
# without the package should still be able to import this module.
try:
    from google.genai import types
except Exception:
    types = None


def get_files_info(working_directory, directory="."):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

        # Ensure target_dir is inside working_directory
        if os.path.commonpath([working_dir_abs, target_dir]) != working_dir_abs:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        items = []
        for name in sorted(os.listdir(target_dir)):
            path = os.path.join(target_dir, name)
            try:
                is_dir = os.path.isdir(path)
                size = os.path.getsize(path) if os.path.exists(path) else 0
            except OSError as e:
                return f'Error: {e}'

            items.append(f'- {name}: file_size={size} bytes, is_dir={is_dir}')

        return "\n".join(items)
    except Exception as e:
        return f'Error: {e}'


if types is not None:
    # Schema for LLM function declaration
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
                ),
            },
        ),
    )
else:
    schema_get_files_info = None
