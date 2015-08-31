import numpy as np

class Sum_Solver(object):

	def __init__(self):
		self.n = 3
		self.N  = self.n**2 # 9
		self.N2 = self.N**2 # 81
		self.N3 = self.N**3 # 729

		self.raw_map = [list()] * self.N

		self.todo = []

		# C_mat.shape = (4*N^2, N^2+1) last col is count of 1s
		self.C_mat = np.zeros((4*self.N2, self.N3+1), int)
		self.C_mat[ : , -1] = self.N
	
	def print_raw(self):

		for i in range(self.N):

			buffer = ' '.join(self.raw_map[i])
			print(buffer)

	def read(self, filename):
		fh = open(filename, 'r')

		if fh == 0:
			return -1

		text_buffer = fh.read().split('\n')

		for i in range(self.N):
			self.raw_map[i] = text_buffer[i].split(' ')

			for j in range(self.N):
				char = self.raw_map[i][j]

				if char !='.':
					# (row, col, lev)
					self.todo.append((i,j,int(char)-1))
		return 1

	def rcl2ind(self, row, col, lev):
		return lev*self.N2 + row*self.N + col

	def ind2rcl(self, ind):
		return ((ind//self.N)%self.N, ind%self.N, ind//self.N2)

	def init_SAT(self):

		pair = [(i,j) for i in range(self.N) for j in range(self.N)]
	
		sat_count = 0
		# For all levels
		for (row, col) in pair:
			for lev in range(self.N):
				self.C_mat[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1

		# For all rows
		for (col, lev) in pair:
			for row in range(self.N):
				self.C_mat[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1

		# For all columns
		for (row, lev) in pair:
			for col in range(self.N):
				self.C_mat[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1

		# For all boxes
		for (lev, box) in pair:
			r = box // self.n * self.n
			c = box %  self.n * self.n
			for row in range(r, r+self.n):
				for col in range(c, c+self.n):
					self.C_mat[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1  # one SAT per box

	def phase_one(self):

		print(self.todo)

		while len(self.todo) > 0:
			row, col, lev = self.todo.pop()

			ind = self.rcl2ind(row, col, lev)

			print(row, col, lev, ind)

			rows_todie = self.do_something(ind)
#			self.do_something(ind)

			self.C_mat = np.delete(self.C_mat, rows_todie, 0)

	def found_new_cell(self, new_ind):

		row, col, lev = self.ind2rcl(new_ind)
		self.todo.append((row, col, lev))
		self.raw_map[row][col] = '%d' % (lev+1)

		print("Found (%d %d %d)->%d with %r" %(row, col, lev, new_ind, np.nonzero(self.C_mat[:, new_ind])[0]))


	def do_something(self, v_ind):

		# Find all row where this 1 appears
		# then remove all other variables
		nz_r = np.nonzero(self.C_mat[:, v_ind])[0]
		self.C_mat[nz_r.tolist(), -1] = -1

		print(nz_r, '\t', v_ind)
#		print(self.C_mat[:, v_ind])
		for row_i in nz_r:

			# Find out the variables to be eliminated
			nz_cc = np.nonzero(self.C_mat[row_i, :-1]);
			nz_c = nz_cc[0]

			print('\t', row_i, '\t', nz_c)
			for col_j in nz_c:
				# Their appearance in other rows are wiped out
				nz_rr = np.nonzero(self.C_mat[:, col_j])[0]

				print('\t\t', nz_rr, '\t', col_j)

				for row_ii in nz_rr:
					# Don't double count (when wiping out)
					if self.C_mat[row_ii, col_j] == 0:
						continue

					self.C_mat[row_ii, col_j] = 0
					#print('%d %d' %(row_ii, col_j))
					# Decrement count of remaining variables
					self.C_mat[row_ii, -1] -= 1
#row_ii != row_i and 
					if self.C_mat[row_ii, -1]==1:
#						print('row_ii = ', row_ii, ' row_i = ', row_i)
						new_ind = np.nonzero(self.C_mat[row_ii, :-1])
						self.found_new_cell(new_ind[0][0])

		return nz_r


def test_rcl2ind():
	pass


def test_solver():

	solver = Sum_Solver()

	solver.read("game1.txt")
	print("Input puzzle")
	solver.print_raw()

	solver.init_SAT()
	solver.phase_one()

	print("Output puzzle")
	solver.print_raw()

if __name__ == '__main__':
#	test_rcl2ind()
	test_solver()