from flask import Flask, render_template, Response, request
import json

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
    def __init__(self, m, n, live_cells):
        self.m = m
        self.n = n
        self.cell_array = {}

        for cell in live_cells:
            self.cell_array.setdefault(cell[0], set()).add(cell[1])

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

    def is_cell_active(self, cell):
        x = cell[0]
        y = cell[1]
        return y in self.cell_array.get(x, set())

    def get_active_cells(self):
        cells = []
        for x, y_set in self.cell_array.iteritems():
            for y in y_set:
                cells.append((x,y))

        return cells

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
