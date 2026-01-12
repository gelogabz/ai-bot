import os

# Try to import google.genai types for schema declaration; tests/envs
# without the package should still be able to import this module.
try:
    from google.genai import types
except Exception:
    types = None

MAX_CHARS = 10000


def get_file_content(working_directory, file_path):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(
            os.path.join(working_dir_abs, file_path))

        # Ensure target_path is inside working_directory
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # Read up to MAX_CHARS and detect truncation
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(MAX_CHARS)
                if f.read(1):
                    content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return content
        except OSError as e:
            return f'Error: {e}'
    except Exception as e:
        return f'Error: {e}'


if types is not None:
    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Reads and returns the contents of a file relative to the working directory, truncating very large files",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Path to the file to read, relative to the working directory",
                ),
            },
        ),
    )
else:
    schema_get_file_content = None
