class Solver(object):

    def __init__(self):
        self.raw_map = [list()] * 9
        self.infomap = [[[]]]
        for i in range(9):
        self.todo = []

    def rc2ind(self, i, j):
        return i * 9 + j

    def ind2rc(self, idx):
        return idx // 9, idx % 9

    def read(self, filename):
        fh = open(filename, 'r')

        if fh == 0:
            return -1

        text_buffer = fh.read().split('\n')

        for i in range(9):
            self.raw_map[i] = text_buffer[i].split(' ')

            for j in range(9):
                char = self.raw_map[i][j]
                #print(i, j, char)
                if char != '.':
                 #   print((idx, int(char)))
                    self.todo.append((int(char), i, j))

    def pp(self):

        for i in range(9):

            buffer = ' '.join(self.raw_map[i])
            print(buffer)

    def check_unique(self, row, col, num):
        idx = self.rc2ind(row, col)
        print(row, col, self.infomap[idx])
        try:
            self.infomap[idx].remove(num)
        except ValueError:
            pass

        # Not it's unique, has to be the answer
        if len(self.infomap[idx])==1:
            unique_int = self.infomap[idx]
            self.todo.append((idx, unique_int))
            self.infomap[idx].clear()
            self.raw_map[row][col] = "%d" % unique_int

    def sqr_sweep(self, row, col, num):
     
        r = row // 3 * 3
        c = col // 3 * 3

        for i in range(r, r+3):
            for j in range(c, c+3):
                self.check_unique(i, j, num)

    def row_sweep(self, row, num):

        for j in range(9):
            self.check_unique(row, j, num)

    def col_sweep(self, col, num):

        for i in range(9):
            self.check_unique(i, col, num)

    def solve(self):

        print(self.todo)

        num, row, col = self.todo.pop()

        print(idx, num)

        row, col = self.ind2rc(idx)
        self.row_sweep(row, num)
#        while True: 
#            idx, num = self.todo.pop()

#            row, col = ind2rc(idx)
#            row_sweep(row, num)
#            col_sweep(col, num)
#            sqr_sweep(row, col, num)


def main():
    mysolver = Solver()

    mysolver.read("game1.txt")

#    mysolver.pp()
    mysolver.solve()

if __name__ == '__main__':
    main()