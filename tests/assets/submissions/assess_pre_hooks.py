apple: int = 1


def sum_file(file_name: str) -> int:
    with open(file_name) as f:
        return sum(map(lambda line: int(line.strip()), f.readlines()), 0)
