import numpy as np

class Sum_Solver(object):

	def __init__(self):
		self.N = 9
		self.N2 = self.N**2

		self.raw_map = [list()] * self.N

		self.todo = []

		# C_mat.shape = (4*N^2, N^2+1) last col is count of 1s
		self.C_mat = np.zeros((4*self.N2, self.N2+1), int)
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

	def phase_one(self):

		while len(self.todo) > 0:
			row, col, lev = self.todo.pop()
			ind = self.rcl2ind(row, col, lev)

			rows_todie, cols_todie = self.do_something(ind)

	def found_new_cell(self, ind):

		row, col, lev = self.ind2rcl(new_ind)
		self.todo.append((row, col, lev))
		self.raw_map[row][col] = '%d' % (lev+1)

	def do_something(self, v_ind):

		# Find all row where this 1 appears
		# then remove all other variables
		nz_r = np.nonzero(self.C_mat[:, v_ind])[0]

		for row_i in nz_r:

			# Find out the variables to be eliminated
			nz_c = np.nonzero(self.C_mat[row_i, :-1])[0]

			for col_j in nz_c:
				# Their appearance in other rows are wiped out
				nz_rr = np.nonzero(self.C_mat[:, col_j])[0]

				for row_ii in nz_rr:
					# Don't double count (when wiping out)
					self.C_mat[row_ii, col_j] = 0
					# Decrement count of remaining variables
					self.C_mat[row_ii, -1] -= 1

					if row_ii != row_i and self.C_mat[row_ii, -1]==1:
						new_ind = np.nonzero(self.C_mat[row_ii, :-1])
						self.found_new_cell(new_ind[0][0])

		return (nz_r, nz_c)


def test_rcl2ind():
	pass



if __name__ == '__main__':
	test_rcl2ind()