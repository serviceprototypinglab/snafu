def fib(n):
	if type(n) == str:
		n = int(n)
	if n in (1, 2):
		return 1
	return fib(n - 1) + fib(n - 2)
