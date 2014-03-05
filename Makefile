# Makefile for StripCmt
# --
# Excuse me for this ugly thing.

CC = gcc
# CFLAGS = -s -O3 -Wall -ansi -pedantic -ffast-math -fexpensive-optimizations
CFLAGS =  -Wall -ansi -pedantic
INSTALL = `which install`

stripcmt: stripcmt-0.1.2/stripcmt.c stripcmt-0.1.2/strip.c stripcmt-0.1.2/misc.c stripcmt-0.1.2/stripcmt.h
	$(CC) $(CFLAGS) \
	  stripcmt-0.1.2/stripcmt.c  -o stripcmt

clean:
	rm stripcmt
