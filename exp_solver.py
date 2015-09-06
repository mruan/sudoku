import numpy as np
#from scipy.integrate import odeint
#from scipy.optimize import linprog

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
		self.inactive_rows = set()
		self.inactive_cols = set()
		self.active_cols = set([i for i in range(self.N3)])

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

	def eliminate_candidate(self, cand_idx):

		r, c, n = self.ind2rcl(cand_idx)
		num = '%d' % (n+1)
		# delete this number from the candidate list
		self.cand_map[r][c] = self.cand_map[r][c].replace(num, '')

	def eliminate_singleton(self, ind):

		# Find all rows(i.e. constraints) where the singleton appears
		nz_r = np.nonzero(self.bool_map[:, ind])[0].tolist()
		self.inactive_rows |= set(nz_r)

		# Find columns that are zeroed out due to that naked 1
		nz_c = {c for r in nz_r for c in np.nonzero(self.bool_map[r,:])[0].tolist()}
		self.inactive_cols |= nz_c
		self.active_cols -= nz_c
		nz_c = list(nz_c) # set guarantees uniqueness

		# Remove them from candidate lists
		self.bool_map[nz_r, ind] = 0
		for cand_idx in nz_c:
			if cand_idx != ind:
				self.bool_map[:, cand_idx] = 0
				self.eliminate_candidate(cand_idx)
			


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

		#	print(row, col, lev)

			ind = self.rcl2ind(row, col, lev)

			self.eliminate_singleton(ind)

	def phase_two(self):
		"Optimize sigmoid"

		self.active_vars = [i for i in range(self.N3) if i not in self.inactive_cols]
#		print(self.active_vars)
		# delete rows not active any more
		self.inactive_rows = list(self.inactive_rows)
		self.inactive_cols = list(self.inactive_cols)

		self.bool_map = np.delete(self.bool_map, self.inactive_rows, 0)

		# Find active variable indices and delete inactive ones
		var_ind = np.nonzero(np.sum(self.bool_map, axis = 0))[0].tolist()
		self.bool_map = np.delete(self.bool_map, self.inactive_cols, 1)

#		var = [self.ind2rcl(ind) for ind in var_ind]
		# print(var_ind)
		# print(self.active_cols)
#		print(var)
#		print(len(var))
#		np.savetxt('bm.out', self.bool_map, fmt='%d', delimiter=',')
		c = np.ones(2*n)
		A_ub = np.vstack((self.bool_map, -self.bool_map))
		b_ub = np.ones(2*n)

		res = linprog(c, A_ub, b_ub)

		np.savetxt('y.out', res.x, delimiter=',')
		np.savetxt('x.out', res.slack[n:], delimiter=',')

		# m, n = self.bool_map.shape
		# # print(m,n, len(var_ind))
		# y0 = 0.5 * np.ones(2*n+m)  # initialize all to 0.5
		# c = 7.0

		# for i in range(0,300,10):
		# 	t = np.arange(i, i+10, 1.0)
		# 	y = odeint(func, y0, t, args=(self.bool_map, c,))

		# 	y0 = y[-1,:]

		# 	Ax_m_b, x2mx = calc_gap(y0, self.bool_map)
		# 	print(i, Ax_m_b, x2mx)
		

		# results = y0#y[-1, 0:n].ravel()
		# for i in range(n):
		# 	if results[i] < 1e-1:
		# 		self.eliminate_candidate(var_ind[i])

def calc_gap(y, A):
	m, n = A.shape
	x = y[0:n]
	Ax_m_b = np.sum((np.dot(A,x) - 1.0)**2)

	x2mx  = np.sum((x**2 - x)**2)

	return (Ax_m_b, x2mx)


def func(y, t, A, c):
	# m = 244, n= 291
	m, n = A.shape
	x = y[0:n]
	u = y[n:n+m]
	v = y[n+m:]

	x2mx  = x**2 - x # x^2 - x
	dx2mx = 2.0*x - 1.0

#	b = np.ones(m)

	L = np.zeros(2*n+m)

	Ax_m_b = np.dot(A,x) - 1.0 #b

	L[0:n] = -2.0*c*(np.dot(A.T, Ax_m_b) + x2mx*dx2mx ) - np.dot(A.T,u) - v*dx2mx
	L[n:n+m] = Ax_m_b
	L[n+m:] = x2mx

	return L

def test_solver():

	solver = Exp_Solver()

	solver.read("game1.txt")
	print("\nInput puzzle")
	solver.pprint(1)

	solver.init_constraints()
	solver.phase_one()

	print("\nOutput phase1")
	solver.pprint(1)

	#print(solver.cand_map[0][0], solver.rcl2ind(0,0,4))
#	solver.phase_two()

	print("\nOutput phase2")
	solver.pprint(1)

if __name__ == '__main__':
#	test_rcl2ind()
	test_solver()