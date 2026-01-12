import os

# Try to import google.genai types for schema declaration; tests/envs
# without the package should still be able to import this module.
try:
    from google.genai import types
except Exception:
    types = None


def write_file(working_directory, file_path, content):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(
            os.path.join(working_dir_abs, file_path))

        # Ensure target_path is inside working_directory
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # If target_path is an existing directory, cannot write
        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        # Ensure parent directories exist
        parent_dir = os.path.dirname(target_path)
        if parent_dir:
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except OSError as e:
                return f'Error: {e}'

        # Write the content, overwriting if file exists
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            return f'Error: {e}'

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {e}'


if types is not None:
    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes content to a file (creates or overwrites) relative to the working directory",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Path to the file to write, relative to the working directory",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="String content to write to the file",
                ),
            },
        ),
    )
else:
    schema_write_file = None
