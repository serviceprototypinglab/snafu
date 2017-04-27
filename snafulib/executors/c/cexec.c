#include <stdio.h>
#include <dlfcn.h>

int main(int argc, char *argv[])
{
	void *handler;
	const char *(*handlerfunc)(const char*);
	const char *ret;

	if(argc != 3)
	{
		fprintf(stderr, "Syntax: cexec <handler.so> <inputarg>\n");
		return -1;
	}

	handler = dlopen(argv[1], RTLD_NOW);
	*(void**)(&handlerfunc) = dlsym(handler, "handler");
	ret = (*handlerfunc)(argv[2]);
	printf("ret:%s\n", ret);
	dlclose(handler);

	return 0;
}
