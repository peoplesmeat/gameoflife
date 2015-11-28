from flask import Flask, render_template, Response, request
import json

"""Flask Application implementing game of life rules

This module implements the game of life rules via the API /advance, which takes in the m width, n height
and list of active cells and after applying the cell rules, returns the resultant list of active cells.
"""

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')


def process_live_cells_parameter():
    live_cells = []
    i = 0
    live_cells_for_i = request.args.getlist("liveCells[%d][]" % i)
    while live_cells_for_i:
        live_cells.append([int(x) for x in live_cells_for_i])
        i += 1
        live_cells_for_i = request.args.getlist("liveCells[%d][]" % i)
    return live_cells


@app.route("/advance")
def advance():
    callback = request.args.get('callback')
    m = int(request.args.get('M'))
    n = int(request.args.get('N'))
    live_cells = process_live_cells_parameter()

    frame = GameOfLifeFrame(m, n, live_cells)
    next_frame = frame.advance_frame()

    cells = next_frame.get_active_cells()
    next_frame = json.dumps(cells)
    content = str(callback) + '(' + next_frame + ')'
    return Response(content, mimetype='application/json')


class GameOfLifeFrame(object):
    """Initialize GameOfLife frame with width m and height n number of cells
    Args:
        m (int): Width
        n (int): Height
        live_cells (list[tuple]): List of active cells in (x,y) tuple format

    Internally the list of live_cells is stored as a map of sets, this allows for limited storage in the case
    of sparsely populated grids. In the map the key is the x parameter and the y is a set of active y cells for that
    x coordinate.

    """

    def __init__(self, m, n, live_cells):
        self.m = m
        self.n = n
        self.cell_array = {}

        for cell in live_cells:
            self.cell_array.setdefault(cell[0], set()).add(cell[1])

    """Advance Frame returns the next frame, leaving the current frame unmodified

    Returns:
        The GameOfLifeFrame resulting by applying the rules to the current frame

        The general algorithm is given the current frame

        1. Compute the list of cells to investigate, these are basically the cells surrounding the current
        active cells.
        2. For each cell to investigate, check the number of surrounding active cells
        3. Apply the rules based on the # of surrounding cells
        4. Return the new frame

    """

    def advance_frame(self):
        cells_to_investigate = self.get_cells_to_investigate()
        new_active_cells = []
        for cell in cells_to_investigate:
            num_surrounding_cells_active = self.compute_surrounding_active_cells(cell)
            if num_surrounding_cells_active < 2:
                pass
            elif num_surrounding_cells_active == 2:
                if self.is_cell_active(cell):
                    new_active_cells.append(cell)
            elif num_surrounding_cells_active == 3:
                new_active_cells.append(cell)
            elif num_surrounding_cells_active > 3:
                pass
        return GameOfLifeFrame(self.m, self.n, new_active_cells)

    """Given the current active cells, return all cells that might become active

    Returns:
        a list of cells surrounding the current set of active cells.
        This is optimized for sparsely populated frames.

    """

    def get_cells_to_investigate(self):
        cells_to_investigate = set()
        for x, set_y in self.cell_array.iteritems():
            for y in set_y:
                cells_to_investigate.add((x - 1, y - 1))
                cells_to_investigate.add((x - 1, y))
                cells_to_investigate.add((x - 1, y + 1))
                cells_to_investigate.add((x, y + 1))
                cells_to_investigate.add((x, y - 1))
                cells_to_investigate.add((x + 1, y - 1))
                cells_to_investigate.add((x + 1, y))
                cells_to_investigate.add((x + 1, y + 1))

        cells_on_board = [(x[0], x[1]) for x in cells_to_investigate if ((0 <= x[0] < self.m) and (0 <= x[1] < self.n))]
        return cells_on_board

    """Check if a cell is active

    Args:
        Cell (tuple): (x,y) coordinate to check

    Returns:
        True if cell is active, otherwise False
    """

    def is_cell_active(self, cell):
        x = cell[0]
        y = cell[1]
        return y in self.cell_array.get(x, set())

    """Get list of active cells
    Returns:
        List of tuples of cells active in this frame

    """

    def get_active_cells(self):
        cells = []
        for x, y_set in self.cell_array.iteritems():
            for y in y_set:
                cells.append((x, y))

        return cells

    """Compute number of surrounding active cells

    Args:
        cell (tuple): (x,y) coordinate to check

    Returns:
        Integer number of surrounding cells that are active

    """

    def compute_surrounding_active_cells(self, cell):
        x = cell[0]
        y = cell[1]
        surrounding_cells = 0
        if (y - 1) in self.cell_array.get(x, set()):
            surrounding_cells += 1
        if (y + 1) in self.cell_array.get(x, set()):
            surrounding_cells += 1
        if y in self.cell_array.get(x - 1, set()):
            surrounding_cells += 1
        if y in self.cell_array.get(x + 1, set()):
            surrounding_cells += 1

        if (y - 1) in self.cell_array.get(x + 1, set()):
            surrounding_cells += 1
        if (y + 1) in self.cell_array.get(x + 1, set()):
            surrounding_cells += 1
        if (y - 1) in self.cell_array.get(x - 1, set()):
            surrounding_cells += 1
        if (y + 1) in self.cell_array.get(x - 1, set()):
            surrounding_cells += 1

        return surrounding_cells


if __name__ == "__main__":
    app.run()
