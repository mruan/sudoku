import numpy as np
#import scipy as sp

class Exp_Solver(object):

	def __init__(self):

		self.n = 3
		self.N  = self.n**2 # 9
		self.N2 = self.N**2 # 81
		self.N3 = self.N**3 # 729

		self.game_map = [list()] * self.N
		self.cand_map = [['123456789' for _ in range(9)] for _ in range(9)]

		self.singletons = []

		# bool_map.shape = (4*N^2, N^2) last col is count of 1s
		self.bool_map = np.zeros((4*self.N2, self.N3), int)

	def read(self, filename):
		fh = open(filename, 'r')

		if fh == 0:
			return -1

		text_buffer = fh.read().split('\n')

		for i in range(self.N):
			self.game_map[i] = text_buffer[i].split(' ')

			for j in range(self.N):
				char = self.game_map[i][j]

				if char !='.':
					# (row, col, lev)
					self.singletons.append((i,j,int(char)-1))
					self.cand_map[i][j] = char
		return 1

	def rcl2ind(self, row, col, lev):
		return lev*self.N2 + row*self.N + col

	def ind2rcl(self, ind):
		return ((ind//self.N)%self.N, ind%self.N, ind//self.N2)


	def pprint(self, show_more = 1):
		"Display candaites on a 2d grid."

		dim = range(self.N)

		if show_more:
			width = 1 + max(len(self.cand_map[i][j]) for i in dim for j in dim)
			line = '+'.join(['-'*(width*3)]*3)

			for r in dim:

				print(''.join(self.cand_map[r][c].center(width) + ('|' if c in [2,5] else '') for c in dim))

				if r in [2,5]: print(line)
		else:
			for i in range(self.N):

				buffer = ' '.join(self.game_map[i])
				print(buffer)

	def eliminate_singleton(self, ind):

		# Find all rows(i.e. constraints) where the singleton appears
		nz_r = np.nonzero(self.bool_map[:, ind])[0].tolist()
		self.bool_map[nz_r, ind] = 0

		# Find columns that are zeroed out due to that naked 1
		nz_c = {c for r in nz_r for c in np.nonzero(self.bool_map[r,:])[0].tolist()}
		nz_c = list(nz_c) # set guarantees uniqueness

		# Remove them from candidate lists
		for col_idx in nz_c:
			self.bool_map[:, col_idx] = 0

			row, col, lev = self.ind2rcl(col_idx)
			num = '%d' % (lev+1)
			# delete this number from the candidate list
			self.cand_map[row][col] = self.cand_map[row][col].replace(num, '')


	def has_singletons(self):

		if len(self.singletons) > 0:
			return True

		e1_rows = np.where(np.sum(self.bool_map, axis = 1) == 1)[0].tolist()
		
		# Find the unique singleton cols 
		single_set = {np.nonzero(self.bool_map[r,:])[0][0] for r in e1_rows}

		for ind in single_set:
			row, col, lev = self.ind2rcl(ind)
			num = '%d' % (lev+1)
			self.game_map[row][col] = num 
			self.cand_map[row][col] = num
			self.singletons.append((row, col, lev))

		return len(self.singletons) > 0

	def init_constraints(self):

		dim = range(self.N)
		pair = [(i,j) for i in dim for j in dim]
	
		sat_count = 0
		# For all levels
		for (row, col) in pair:
			for lev in dim:
				self.bool_map[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1

		# For all rows
		for (col, lev) in pair:
			for row in dim:
				self.bool_map[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1

		# For all columns
		for (row, lev) in pair:
			for col in dim:
				self.bool_map[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1

		# For all boxes
		for (lev, box) in pair:
			r = box // self.n * self.n
			c = box %  self.n * self.n
			for row in range(r, r+self.n):
				for col in range(c, c+self.n):
					self.bool_map[sat_count, self.rcl2ind(row, col, lev)] = 1
			sat_count += 1  # one constraint per box

	def phase_one(self):

		while self.has_singletons():

			row, col, lev = self.singletons.pop()

			print(row, col, lev)

			ind = self.rcl2ind(row, col, lev)

			self.eliminate_singleton(ind)

	def phase_two(self):
		"Optimize sigmoid"
		live_var = np.nonzero(np.sum(self.bool_map, axis = 0))[0].tolist()

		var = [self.ind2rcl(ind) for ind in live_var]
		print(var)
		print(len(live_var))

def test_solver():

	solver = Exp_Solver()

	solver.read("game2.txt")
	print("Input puzzle")
	solver.pprint(1)

	solver.init_constraints()
	solver.phase_one()
	solver.phase_two()

	print("Output puzzle")
	solver.pprint(1)

if __name__ == '__main__':
#	test_rcl2ind()
	test_solver()