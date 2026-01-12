import os
import subprocess

# Try to import google.genai types for schema declaration; tests/envs
# without the package should still be able to import this module.
try:
    from google.genai import types
except Exception:
    types = None


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(
            os.path.join(working_dir_abs, file_path))

        # Ensure target_path is inside working_directory
        if os.path.commonpath([working_dir_abs, target_path]) != working_dir_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Ensure it exists and is a regular file
        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        # Ensure it's a Python file
        if not file_path.lower().endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        # Build command
        command = ["python", target_path]
        if args:
            if isinstance(args, (list, tuple)):
                command.extend([str(a) for a in args])
            else:
                command.append(str(args))

        try:
            proc = subprocess.run(
                command,
                cwd=working_dir_abs,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except Exception as e:
            return f'Error: executing Python file: {e}'

        parts = []
        if proc.returncode != 0:
            parts.append(f'Process exited with code {proc.returncode}')

        stdout_text = proc.stdout or ''
        stderr_text = proc.stderr or ''

        if not stdout_text and not stderr_text:
            parts.append('No output produced')
        else:
            if stdout_text:
                parts.append('STDOUT:\n' + stdout_text.rstrip())
            if stderr_text:
                parts.append('STDERR:\n' + stderr_text.rstrip())

        return "\n".join(parts)
    except Exception as e:
        return f'Error: executing Python file: {e}'


if types is not None:
    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Executes a Python file located in the working directory and returns stdout/stderr and exit code",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Path to the Python file to execute, relative to the working directory",
                ),
                "args": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="Optional list of string arguments to pass to the Python program",
                ),
            },
        ),
    )
else:
    schema_run_python_file = None
