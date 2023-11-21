def get_file_lines(file_name: str) -> int:
    with open(file_name) as f:
        return len(f.readlines())
