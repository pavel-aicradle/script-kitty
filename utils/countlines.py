
n_code = 0
n_comments = 0
n_whitespace = 0
docstring = False

with open('coda.py') as code:
	for line in code:
		line = line.strip()

		if len(line) == 0:
			n_whitespace += 1
		elif line[0] == '#':
			n_comments += 1
		elif line[0:3] == '"""' and not docstring:
			n_comments += 1
			docstring = True
		elif line[0:3] == '"""' and docstring:
			n_comments += 1
			docstring = False
		elif docstring:
			n_comments += 1
		else:
			n_code += 1

print("n_code: ", n_code)
print("n_comments: ", n_comments)
print("n_whitespace: ", n_whitespace)