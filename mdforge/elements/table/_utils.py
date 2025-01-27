from .cell import Cell

__all__ = [
    "get_dims",
]


def get_dims(rows: list[list[Cell]]) -> tuple[int, int]:
    """
    Get effective dimensions of provided matrix, accounting for any
    merged cells.
    """

    if not rows:
        return (0, 0)

    col_counts: list[int] = []  # counts per row

    def add_at(index: int, val: int):
        """
        Add value at the given index, inserting elements as needed.
        """
        nonlocal col_counts
        if index >= len(col_counts):
            col_counts += [0] * (index - len(col_counts) + 1)
        col_counts[index] += val

    # get col counts
    for row_idx, row in enumerate(rows):

        # add columns for this row, accounting for spanned columns
        add_at(row_idx, sum(cell.cspan for cell in row))

        # look ahead to account for spanned rows
        for cell in row:
            for row_offset in range(1, cell.rspan):
                add_at(row_idx + row_offset, cell.cspan)

    # verify consistency
    for row_idx, col_count in enumerate(col_counts):
        assert (
            col_count == col_counts[row_idx - 1]
        ), f"Inconsistent column counts: row {row_idx}={col_count}, row {row_idx-1}={col_counts[row_idx-1]}"

    row_count = len(rows)
    col_count = col_counts[0]

    return row_count, col_count
