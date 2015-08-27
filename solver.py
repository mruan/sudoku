class Solver(object):

    def __init__(self):
        self.raw_map = [[] for _ in range(9)]
        self.infomap = [[[1,2,3,4,5,6,7,8,9] for _ in range(9)] for _ in range(9)]
        self.debug   = [[9]*9 for _ in range(9)]
        self.todo = [] # [(num, row, col)]

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

            debug_buffer = '     %d %d %d %d %d %d %d %d %d' %(
                self.debug[i][0], self.debug[i][1], self.debug[i][2],
                self.debug[i][3], self.debug[i][4], self.debug[i][5],
                self.debug[i][6], self.debug[i][7], self.debug[i][8])
            print(buffer + debug_buffer)

    def check_unique(self, num, row, col):

        list_ptr = self.infomap[row][col]
 #       print(row, col, list_ptr)
        try:
            list_ptr.remove(num)
        except ValueError:
            pass

        # Now it's unique, has to be the answer
        if len(list_ptr)==1:

            unique_int = list_ptr.pop()
            self.todo.append((unique_int, row, col))
            self.raw_map[row][col] = "%d" % unique_int
            print("Unique item found: %d at (%d %d)" % (unique_int, row, col))
            self.pp()
            a = input()

        self.debug[row][col] = len(list_ptr)
 #       print(row, col, list_ptr)

    def sqr_sweep(self, num, row, col):
     
        r = row // 3 * 3
        c = col // 3 * 3

        for i in range(r, r+3):
            for j in range(c, c+3):
                self.check_unique(num, i, j)

    def row_sweep(self, num, row):

        for j in range(9):
            self.check_unique(num, row, j)

    def col_sweep(self, num, col):

        for i in range(9):
            self.check_unique(num, i, col)

    def solve(self):

        for item in self.todo:
            num, row, col = item
            self.infomap[row][col].clear()
            self.debug[row][col] = len(self.infomap[row][col])

#        self.row_sweep(num, row)
#        self.col_sweep(num, col)
#        self.sqr_sweep(num, row, col)
        while len(self.todo)>0:
            print(self.todo)
            num, row, col = self.todo.pop()
            print(num, row, col)

            self.row_sweep(num, row)
            self.col_sweep(num, col)
            self.sqr_sweep(num, row, col)

        self.pp()
        
def main():
    mysolver = Solver()

    mysolver.read("game1.txt")

    mysolver.pp()
    mysolver.solve()

if __name__ == '__main__':
    main()