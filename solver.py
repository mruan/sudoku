class Solver(object):

    def __init__(self):
        self.raw_map = [list()] * 9
        self.stackmap= [range(1,10)]*81
        self.todo = []

    def rc2ind(self, i, j):
        return i * 9 + j

    def read(self, filename):
        fh = open(filename, 'r')

        if fh == 0:
            return -1

        text_buffer = fh.read().split('\n')

        for i in range(9):
            self.raw_map[i] = text_buffer[i].split(' ')

            for j in range(9):
                char = self.raw_map[i][j]
                idx = self.rc2ind(i, j)
                #print(i, j, char)
                if char != '.':
                 #   print((idx, int(char)))
                    self.todo.append((idx, int(char)))

    def pp(self):

        for i in range(9):

            buffer = ' '.join(self.raw_map[i])
            print(buffer)

    def sqr_sweep(self, row, col):


    def solve(self):

        while True: 
            idx, num = self.todo.pop()

            row, col = ind2rc(idx)
            row_sweep(row)
            col_sweep(col)
            sqr_sweep(row, col)


def main():
    mysolver = Solver()

    mysolver.read("game1.txt")

    mysolver.pp()

if __name__ == '__main__':
    main()