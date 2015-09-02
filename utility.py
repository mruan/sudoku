# Sudoku utility module

def read(filename):

	fh = open(filename, 'r')
	if fh ==0:
		return ([], [])

	hints = []

	raw_map = [[] for _ in range(9)]

	text_buffer = fh.read().split('\n')

	for i in range(9):
		raw_map[i] = text_buffer[i].split(' ')

		for j in range(9):
				char = raw_map[i][j]

				if char !='.':
					# (row, col, lev)
					hints.append((i,j,int(char)-1))

	return (raw_map, hints)

def pprint(raw_map):
	"""
		Assumes raw_map nxn
	"""
	for i in range(9):

		if i > 0 and i % 3 == 0:
			print("-----+-----+-----")

		segments = [' '.join(raw_map[i][j:j+3]) for j in range(0,9,3)]
		print('|'.join(segments))


if __name__ == '__main__':

	raw_map, hint_list = read('game1.txt')

#	print(raw_map)

	pprint(raw_map)

	print(hint_list)