#ifndef ELEMENTS_H
#define ELEMENTS_H

#include "stdafx.h"
#include "Colormap.h"

class Image{
public:
	HDC * mywindow;
	Colormap * colormap;
	bool ontop;
	FILE* entry;
	int length, height;
	COLORREF matrix[32][32];
	void Getptrs(HDC * windowPtr, Colormap * colormapptr);
	void load();
	void print(int x, int y, int orientation, int ratiox, int ratioy);
	void erase(int x, int y, int orientation, int ratiox, int ratioy);
	void printrope(int xi, int yi, int xf, int yf);
	void eraserope(int xi, int yi, int xf, int yf);
private:
	int sign(int x);
};

//0 = mario, 1 = luigi, 2 = mushroom. 3 = block, 4 = coin, 5 = coinbox, 6 = spentcoinbox, 7 = brick, 8 = bomb

class Element{
public:
	Element();
	int num, sizex, sizey, orientation, timeofdeath;
	float vely;
	int top, left, spent;
	void print();
	void erase();
	int bottom();
	int right();
	int middlex();
	int middley();
	void InitializeElements(HDC * windowPtr, Colormap * colormapptr);
};

class Rope{
public:
	int x[100];
	int y[100];
	int n;
	float w;
	float len;
	float teta[100];
	bool side[100];
	int userforce;
	void print();
	void erase();
	void printall();
	void eraseall();
};
#endif