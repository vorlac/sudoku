from itertools import groupby, product
from random import sample


class Sudoku:
    """
    A Sudoku (i.e. the puzzle) is a partially completed grid.
    * A grid has 9 rows, 9 columns and 9 boxes, each having 9 cells (81 total).
    * Boxes can also be called blocks or regions.
    * Three horizontally adjacent blocks are a band.
    * Three vertically adjacent blocks are a stack.
    * The initially defined values are clues or givens.
    """

    def __init__(self):
        # all possible digits that can be assigned to each cell of the grid
        self.digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        # row indexes (1 based indexing)
        self.rows = self.digits[:]
        # col indexes (1 based indexing)
        self.columns = self.digits[:]

        # box row index groupings
        self.box_group_rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        # box col index groupings
        self.box_group_cols = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        # coordinates for each possible cell in the grid
        self.cells = list(product(self.rows, self.columns))
        # the sudoku grid of values
        # [len(self.columns) * [None]] * len(self.rows)
        self.grid: dict[tuple[int, int], None | int] = {c: None for c in self.cells}
        self.values: dict[tuple[int, int], list[int]] = {c: [] for c in self.cells}

        # coordinates of all row groups in the grid
        self.row_groups = [list(product([row], self.columns)) for row in self.rows]
        # coordinates of all column groups in the grid
        self.column_groups = [list(product(self.rows, [col])) for col in self.columns]
        # coordinates of all box/region groups in the grid
        self.box_groups = [
            list(product(row_group, col_group))
            for row_group in self.box_group_rows
            for col_group in self.box_group_cols
        ]

        # combined list of all different groups represented within the grid
        self.groupings = self.column_groups + self.row_groups + self.box_groups
        # mapping of each of the three groups that each cell belongs to (a row, a col, and a box)
        # { cell(x, y) => [[row group cells], [col group cells], [box group cells]] }
        self.cell_groups = dict(
            (c, [g for g in self.groupings if c in g]) for c in self.cells
        )
        # mapping of each unique cell belonging to any group that each cell belongs to
        # { cell(x, y) => [cell groups list] }
        self.related_cells = {
            c: set(sum(self.cell_groups[c], [])) - set([c]) for c in self.cells
        }

    def __repr__(self):
        grid_str: list[str] = []
        cell_row_groups = groupby(self.cells, key=lambda cell: cell[0])
        for idx, (_, row) in enumerate(cell_row_groups):
            row_cell_list = [
                " ".join(group)
                for group in zip(
                    *(
                        iter(
                            [
                                "".join(
                                    str(self.grid[cell] if self.grid[cell] else ".")
                                )
                                for cell in row
                            ]
                        ),
                    )
                    * 3
                )
            ]
            row_cell_str = " | ".join(row_cell_list)
            if grid_str and idx % 3 == 0:
                grid_str.append(
                    " + ".join([str("-" * int((len(row_cell_str) - 6) / 3))] * 3)
                )

            grid_str.append(row_cell_str)

        return "\n" + "\n".join(grid_str) + "\n"

    # def __str__(self):
    #     grid_str: list[str] = []
    #     cell_row_groups = groupby(self.cells, key=lambda cell: cell[0])
    #     for idx, (_, row) in enumerate(cell_row_groups):
    #         row_cell_list = [
    #             " ".join(group)
    #             for group in zip(
    #                 *(iter(["".join(str(self.values[cell])) for cell in row]),) * 3
    #             )
    #         ]
    #         row_cell_str = " | ".join(row_cell_list)
    #         if grid_str and idx % 3 == 0:
    #             grid_str.append(
    #                 " + ".join([str("-" * int((len(row_cell_str) - 6) / 3))] * 3)
    #             )

    #         grid_str.append(row_cell_str)

    #     return "\n" + "\n".join(grid_str) + "\n"

    def _reset(self):
        self.grid: dict[tuple[int, int], None | int] = {c: None for c in self.cells}
        self.values: dict[tuple[int, int], list[int]] = {c: [] for c in self.cells}

    def validate(self) -> bool:
        assert len(self.cells) == 81
        assert len(self.groupings) == 27
        assert all(len(self.cell_groups[s]) == 3 for s in self.cells)
        assert all(len(self.related_cells[s]) == 20 for s in self.cells)
        return True

    def _related_cell_values(self, cell: tuple[int, int]) -> list[int]:
        ret: list[int] = []
        for related_cell in self.related_cells[cell]:
            val = self.grid[related_cell]
            if val is not None:
                ret.append(val)

        return ret

    def _seed_puzzle_generation(self) -> bool:
        nums = sample(self.digits, len(self.digits))
        for n in nums:
            cells = sample(self.cells, len(self.cells))
            for cell in cells:
                if self.grid[cell] is None:
                    self.grid[cell] = n
                    break

        return True

    def generate(self) -> bool:
        self._seed_puzzle_generation()
        if not self.solve():
            self._reset()
            return False
        return True

    # def generate_puzzle2(self) -> bool:
    #     # randomly iterate through all grid cells
    #     cells = sample(self.cells, len(self.cells))
    #     for count, cell in enumerate(cells):
    #         # randomly iterate through all digits that couls be stored in each cell
    #         nums = sample(self.digits, len(self.digits))
    #         group_values = self._related_cell_values(cell)
    #         for n in nums:
    #             if n not in group_values:
    #                 self.grid[cell] = n
    #                 break

    #         if self.grid[cell] is None:
    #             print(self)
    #             self._reset()
    #             return False
    #         elif count >= 9:
    #             solved = self.solve()
    #             if not solved:
    #                 self._reset()
    #             return solved

    #     return True

    def _init_solution_values(self) -> bool:
        for cell in self.cells:
            grid_val = self.grid[cell]
            if grid_val:
                self.values[cell].append(grid_val)
            else:
                for num in self.digits:
                    group_values = self._related_cell_values(cell)
                    if num not in group_values:
                        self.values[cell].append(num)
        return True

    def propagate_value_changes(self) -> bool:
        for cell in self.cells:
            if len(self.values[cell]) == 1:
                cell_value = self.values[cell][0]
                # remove the assigned value from all connected
                # groups (row, col, box) related to the cell
                for related_cell in self.related_cells[cell]:
                    if cell_value in self.values[related_cell]:
                        self.values[related_cell].remove(cell_value)
                        # if the last potential digit value was removed
                        # from this cell, the grid won't be solvable
                        if len(self.values[related_cell]) == 0:
                            return False

        return True

    def solve(self) -> bool:
        self._init_solution_values()

        modified_grid_values = True
        while modified_grid_values:
            modified_grid_values = False
            # check each cell that still has more than one
            # potential value that could be assigned to it
            for cell in self.cells:
                cell_value_candidates = self.values[cell]
                if len(cell_value_candidates) > 1:
                    # iterate through all possible values that haven't
                    # been eliminated for the current cell yet
                    for possible_value in cell_value_candidates:
                        # for each value, check it against all related cells
                        # in each of the three groups (row, col, box/region)
                        related_cells = self.related_cells[cell]
                        for rel_cell in related_cells:
                            # if no other related cells contain the current cell's
                            # potential value, then it's safe to assign the value
                            # since we know it can't go anywhere else and isn't
                            # already in one of the cell's related cell groups
                            rel_cell_values = self._related_cell_values(rel_cell)
                            if possible_value in rel_cell_values:
                                continue

                            self.values[cell] = [possible_value]
                            self.propagate_value_changes()
                            modified_grid_values = True
                            #####################################
                            #####################################
                            print(self)
                            self.grid[cell] = possible_value  ###
                            print(self)
                            #####################################
                            #####################################
                            # break

        for cell in self.cells:
            cell_value_candidates = self.values[cell]
            if len(cell_value_candidates) != 1:
                print(self)
                return False

        return True


def main():
    sudoku = Sudoku()
    if sudoku.validate():
        attempts = 0
        generated = False
        while not generated:
            generated = sudoku.generate()
            if attempts % 50 == 0:
                print(attempts, end="    \r")

            attempts += 1
            if generated:
                print(sudoku)
                break
    return True


if __name__ == "__main__":
    main()
