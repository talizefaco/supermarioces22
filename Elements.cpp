#include "stdafx.h"
#include "Elements.hpp"


#define RED RGB(255, 0, 0)
#define BLUE  RGB(0, 0, 255)
#define BLACK RGB(0, 0, 0)
#define WHITE RGB(255, 255, 255)
#define NONE RGB(1, 2, 3)
#define BROWN RGB(43, 17, 0)
#define SKIN RGB(255, 179, 128)
#define YELLOW RGB(255, 255, 0)
#define SHOE RGB(80, 45, 22)
#define SKY RGB(101, 156, 239)
#define	COLOR1 RGB(203, 79, 15)
#define COLOR2 RGB(255, 191, 179)
#define COLOR3 RGB(248, 216, 30)
#define COLOR4 RGB(248, 248, 0)
#define COLOR5 RGB(216, 158, 54)
#define COLOR6 RGB(255, 210, 67)
#define COLOR7 RGB(247, 150, 70)
#define COLOR8 RGB(255, 97, 29)
#define COLOR9 RGB(0,85,170)
#define COLOR0 RGB(131,91,9)
#define COLORZ RGB(246, 182, 4)
#define GREEN RGB(40, 170, 85)

Image images[10];


void Image::load() {
	char read;
	for (int j = 0; j != height; j++) {
		for (int i = 0; i != length; i++) {
			fscanf(entry, "%c", &read);
			if (read == 'R')
				matrix[i][j] = RED;
			else if (read == 'L')
				matrix[i][j] = BLUE;
			else if (read == 'S')
				matrix[i][j] = SKIN;
			else if (read == 'Y')
				matrix[i][j] = YELLOW;
			else if (read == 'N')
				matrix[i][j] = BROWN;
			else if (read == 'W')
				matrix[i][j] = WHITE;
			else if (read == 'Q')
				matrix[i][j] = SHOE;
			else if (read == 'B')
				matrix[i][j] = BLACK;
			else if (read == '1')
				matrix[i][j] = COLOR1;
			else if (read == '2')
				matrix[i][j] = COLOR2;
			else if (read == '3')
				matrix[i][j] = COLOR3;
			else if (read == '4')
				matrix[i][j] = COLOR4;
			else if (read == '5')
				matrix[i][j] = COLOR5;
			else if (read == '6')
				matrix[i][j] = COLOR6;
			else if (read == '7')
				matrix[i][j] = COLOR7;
			else if (read == '8')
				matrix[i][j] = COLOR8;
			else if (read == '9')
				matrix[i][j] = COLOR9;
			else if (read == '0')
				matrix[i][j] = COLOR0;
			else if (read == 'Z')
				matrix[i][j] = COLORZ;
			else if (read == 'G')
				matrix[i][j] = GREEN;
			else
				matrix[i][j] = NONE;
		}
		fscanf(entry, "%c", &read);
	}
	fclose(entry);
}
int Image::sign(int x) {
	if (x > 0)
		return 1;
	else
		return -1;
}
void Image::print(int x, int y, int orientation, int ratiox, int ratioy) {
	COLORREF color;
	int i;
	for (int j = 0; j < height; j++) {
		for (int k = 0; k < length; k++) {
			if (orientation == 0)
				i = k;
			else
				i = 11 - k;
			if (matrix[i][j] == NONE)
				continue;
			for (int m = 0; m < ratiox; m++) {
				for (int n = 0; n < ratioy; n++) {
					if (!ontop)
						(*colormap).map[x + ratiox*k + m][y + ratioy*j + n] = matrix[i][j];
					SetPixelV((*mywindow), x + ratiox*k + m, y + ratioy*j + n, matrix[i][j]);
				}
			}
		}
	}
}
void Image::erase(int x, int y, int orientation, int ratiox, int ratioy) {
	COLORREF color;
	int i;
	for (int j = 0; j < height; j++) {
		for (int k = 0; k < length; k++) {
			if (orientation == 0)
				i = k;
			else
				i = 11 - k;
			if (matrix[i][j] == NONE) {
				continue;
			}
			for (int m = 0; m < ratiox; m++) {
				for (int n = 0; n < ratioy; n++) {
					if (ontop == 1) {
						SetPixelV((*mywindow), x + ratiox*k + m, y + ratioy*j + n, colormap->map[x + ratiox*k + m][m, y + ratioy*j + n]);
					}
					else {
						SetPixelV((*mywindow), x + ratiox*k + m, y + ratioy*j + n, SKY);
						(*colormap).map[x + ratiox*k + m][y + ratioy*j + n] = SKY;
					}
				}
			}
		}
	}
}
void Image::Getptrs(HDC * windowPtr, Colormap * colormapptr) {
	colormap = colormapptr;
	mywindow = windowPtr;
}
void Image::printrope(int x1, int y1, int x0, int y0) {
	int deltax = x1 - x0;
	int deltay = y1 - y0;
	float error = 0;
	if (deltax != 0) {
		float deltaerr = abs(1.0*deltay / deltax);
		int y = y0;
		for (int x = x0; x <= x1 && (y - y1) != 0; x++) {
			SetPixelV((*mywindow), x, y, BLACK);
			error += deltaerr;
			while (error >= 0.5) {
				SetPixelV((*mywindow), x, y, BLACK);
				y = y + sign(y1 - y0);
				error = error - 1.0;
			}
		}
		for (int x = x0; x >= x1 && (y - y1) != 0; x--) {
			SetPixelV((*mywindow), x, y, BLACK);
			error += deltaerr;
			while (error >= 0.5) {
				SetPixelV((*mywindow), x, y, BLACK);
				y = y + sign(y1 - y0);
				error = error - 1.0;
			}
		}
		if (y0 == y1) {
			for (int x = x0; x <= x1; x++)
				SetPixelV((*mywindow), x, y0, BLACK);
			for (int x = x0; x >= x1; x--)
				SetPixelV((*mywindow), x, y0, BLACK);
		}
	}
	else {
		for (int y = y0; y <= y1; y++)
			SetPixelV((*mywindow), x0, y, BLACK);
		for (int y = y0; y >= y1; y--)
			SetPixelV((*mywindow), x0, y, BLACK);
	}
}
void Image::eraserope(int x1, int y1, int x0, int y0) {
	int deltax = x1 - x0;
	int deltay = y1 - y0;
	float error = 0;
	if (deltax != 0) {
		float deltaerr = abs(1.0*deltay / deltax);
		int y = y0;
		for (int x = x0; x <= x1; x++) {
			SetPixelV((*mywindow), x, y, colormap->map[x][y]);
			error += deltaerr;
			while (error >= 0.5) {
				SetPixelV((*mywindow), x, y, colormap->map[x][y]);
				y = y + sign(y1 - y0);
				error = error - 1.0;
			}
		}
		for (int x = x0; x >= x1; x--) {
			SetPixelV((*mywindow), x, y, colormap->map[x][y]);
			error += deltaerr;
			while (error >= 0.5) {
				SetPixelV((*mywindow), x, y, colormap->map[x][y]);
				y = y + sign(y1 - y0);
				error = error - 1.0;
			}
		}
	}
	else {
		for (int y = y0; y <= y1; y++)
			SetPixelV((*mywindow), x0, y, colormap->map[x0][y]);
		for (int y = y0; y >= y1; y--)
			SetPixelV((*mywindow), x0, y, colormap->map[x0][y]);
	}
}


Element::Element() {
	vely = 0;
	sizex = 2;
	sizey = 2;
	orientation = 0;
	spent = 0;
	timeofdeath = 0;

}
void Element::print() {
	images[num].print(left, top, orientation, sizex, sizey);
}
void Element::erase() {
	images[num].erase(left, top, orientation, sizex, sizey);
}
int Element::bottom() {
	return (top + sizey*images[num].height - 1);
}
int Element::right() {
	return (left + sizex*images[num].length - 1);
}
int Element::middlex() {
	return (left + right()) / 2;
}
int Element::middley() {
	return (top + bottom()) / 2;
}
void Element::InitializeElements(HDC * windowPtr, Colormap * colormapptr) {
	//It's a me, Mario!
	for (int i = 0; i < 10; i++)
		images[i].Getptrs(windowPtr, colormapptr);
	images[0].entry = fopen("C:\\Mario\\Mario12x16.txt", "r");
	images[0].height = 16;
	images[0].length = 12;
	images[0].ontop = 1;
	images[0].load();
	//It's a me, Aluisio!
	images[1].entry = fopen("C:\\Mario\\Luigi12x16.txt", "r");
	images[1].height = 16;
	images[1].length = 12;
	images[1].ontop = 1;
	images[1].load();
	//Mario's hungry. Let's make a mushroom!
	images[2].entry = fopen("C:\\Mario\\Mushroom16x16.txt", "r");
	images[2].height = 16;
	images[2].length = 16;
	images[2].ontop = 0;
	images[2].load();
	//I need something to walk on!
	images[3].entry = fopen("C:\\Mario\\Block32x32.txt", "r");
	images[3].height = 32;
	images[3].length = 32;
	images[3].ontop = 0;
	images[3].load();
	//And money to buy Peach a nice dildo...
	images[4].entry = fopen("C:\\Mario\\Coin12x16.txt", "r");
	images[4].height = 16;
	images[4].length = 12;
	images[4].ontop = 0;
	images[4].load();
	//
	images[5].entry = fopen("C:\\Mario\\Coinbox16x16.txt", "r");
	images[5].height = 16;
	images[5].length = 16;
	images[5].ontop = 0;
	images[5].load();
	//
	images[6].entry = fopen("C:\\Mario\\SpentCoinbox16x16.txt", "r");
	images[6].height = 16;
	images[6].length = 16;
	images[6].ontop = 0;
	images[6].load();
	//
	images[7].entry = fopen("C:\\Mario\\Brick16x16.txt", "r");
	images[7].height = 16;
	images[7].length = 16;
	images[7].ontop = 0;
	images[7].load();
	//
	images[8].entry = fopen("C:\\Mario\\Bomb29x29.txt", "r");
	images[8].height = 29;
	images[8].length = 29;
	images[8].ontop = 1;
	images[8].load();
	//
	images[9].entry = fopen("C:\\Mario\\Aim7x7.txt", "r");
	images[9].height = 7;
	images[9].length = 7;
	images[9].ontop = 1;
	images[9].load();
	//
}



void Rope::print() {
	images[0].printrope(x[n], y[n], x[n - 1], y[n - 1]);
}
void Rope::erase() {
	images[0].eraserope(x[n], y[n], x[n - 1], y[n - 1]);
}
void Rope::printall() {
	int auxiliar = n;
	while (n > 0) {
		print();
		--n;
	}
	n = auxiliar;
}
void Rope::eraseall() {
	int auxiliar = n;
	while (n > 0) {
		erase();
		--n;
	}
	n = auxiliar;
}