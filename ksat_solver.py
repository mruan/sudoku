import numpy as np

class kSAT_Solver(object):

	def __init__(self):
		self.raw_map = [list()] * 9
		self.infomap = 9*np.ones((9, 9, 9), int)
		self.todo = []

		self.lev_count = 9*np.ones((9,9), int)
		self.row_count = 9*np.ones((9,9), int)
		self.col_count = 9*np.ones((9,9), int)
		self.box_count = 9*np.ones((9,9), int)

	def phase_one(self):

		# process the clues first:
		while len(self.todo) > 0:
			row, col, lev = self.todo.pop()

			self.sweep(row, col, lev)

#		self.print_info()
#		self.print_raw()
		# see if we make any new progress
		self.look_for_singleton()
		
		while len(self.todo) > 0:

			row, col, lev = self.todo.pop()

			self.sweep(row, col, lev)

			self.look_for_singleton()

#		self.print_info()
#		self.print_raw()

	def eliminate_single_cell(self, row, col, lev):

		self.lev_count[row, col] -= 1
		self.row_count[col, lev] -= 1
		self.col_count[row, lev] -= 1
		self.box_count[row//3*3+col//3, lev] -= 1


	def update_single_cell(self, row, col, num):
		self.todo.append((row, col, num))
		self.raw_map[row][col] = '%d' % (num+1)
		self.sweep(row, col, num)
		print("\nFound %d at (%d, %d)" % (num+1, row, col))
		self.print_raw()

	def look_for_singleton(self):

		ind = [(i,j) for i in range(9) for j in range(9)]
			
		for (row, col) in ind:
			if self.lev_count[row, col] == 1:
				# find lev that is 1
				levs = np.nonzero(self.infomap[row, col, :])
				self.update_single_cell(row, col, levs[0][0])

		for (col, lev) in ind:
			if self.row_count[col, lev] == 1:
				rows = np.nonzero(self.infomap[:, col, lev])
				self.update_single_cell(rows[0][0], col, lev)

		for (row, lev) in ind:
			if self.col_count[row, lev] == 1:
				cols = np.nonzero(self.infomap[row, :, lev])
				self.update_single_cell(row, cols[0][0], lev)

		for (box, lev) in ind:
			if self.box_count[box, lev] == 1:
				br = box // 3 * 3
				bc = box % 3  * 3
				where = np.nonzero(self.infomap[br:br+3, bc:bc+3, lev])
#				print(self.infomap[br:br+3, bc:bc+3, lev])
#				print(br, bc, where[0][0], where[1][0])
				self.update_single_cell(br+where[0][0], bc+where[1][0], lev)

	def eliminate_row(self, col, lev):
		for i in range(9):
			if self.infomap[i, col, lev] > 1:
				self.infomap[i, col, lev] = 0
				self.eliminate_single_cell(i, col, lev)

	def eliminate_col(self, row, lev):
		for i in range(9):
			if self.infomap[row, i, lev] > 1:
				self.infomap[row, i, lev] = 0
				self.eliminate_single_cell(row, i, lev)

	def eliminate_box(self, row, col, lev):
		box_r = row // 3 * 3
		box_c = col // 3 * 3
		for i in range(box_r, box_r+3):
			for j in range(box_c, box_c+3):
				if self.infomap[i, j, lev] > 1:
					self.infomap[i, j, lev] = 0
					self.eliminate_single_cell(i, j, lev)

	def eliminate_lev(self, row, col):
		for i in range(9):
			if self.infomap[row, col, i] > 1:
				self.infomap[row, col, i] = 0
				self.eliminate_single_cell(row, col, i)

	def sweep(self, row, col, lev):

		#row, col, lev = self.todo.pop()

		# set this particular cell to 1
		self.infomap[row, col, lev] = 1
		self.eliminate_single_cell(row, col, lev)

		# sweep level
		self.eliminate_lev(row, col)

		# sweep row
		self.eliminate_row(col, lev)

		# sweep col
		self.eliminate_col(row, lev)

		# sweep box
		self.eliminate_box(row, col, lev)

	def read(self, filename):

		fh = open(filename, 'r')

		if fh == 0:
			return -1

		text_buffer = fh.read().split('\n')

		for i in range(9):
			self.raw_map[i] = text_buffer[i].split(' ')

			for j in range(9):
				char = self.raw_map[i][j]

				if char !='.':
					self.todo.append((i,j,int(char)-1))

	def print_raw(self):

		for i in range(9):

			buffer = ' '.join(self.raw_map[i])
			print(buffer)

	def print_info(self):

		for i in range(9):
			print('Level %d' % i)
			print(self.infomap[:, :, i])

def main():
	mysolver = kSAT_Solver()

	mysolver.read("sudoku/game1.txt")

	print("Input puzzle:")
	mysolver.print_raw()

	mysolver.phase_one()

#	mysolver.print_info()
	print("Output puzzle")
	mysolver.print_raw()


if __name__ == '__main__':
	main()