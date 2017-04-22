#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int fib(int n)
{
	if(n < 2)
		return 1;
	else
		return fib(n - 1) + fib(n - 2);
}

const char *handler(const char *input)
{
	int n = atoi(input);
	n = fib(n);
	char result[100];
	snprintf(result, sizeof(result) - 1, "%d", n);
	return strdup(result);
}
