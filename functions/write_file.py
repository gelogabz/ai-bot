import os


def write_file(working_directory, file_path, content):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

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
