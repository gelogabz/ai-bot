import os

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
