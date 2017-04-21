#include "stdafx.h"
#include "Stage.hpp"
#define SKY RGB(101, 156, 239)


void Stage::Initialize(HDC * windowpTr) {

	mywindow = windowpTr;
	blockslen = 0;
	coinslen = 0;
	mushroomslen = 0;
	coinboxeslen = 0;
	brickslen = 0;
	bombslen = 0;
	for (int j = 1; j < 599; j++) {
		for (int i = 1; i < 1183; i++) {
			map[i][j] = 0;
		}
	}
	for (int i = 0; i < 1184; i++) {
		map[i][0] = 1;
		map[i][599] = 1;
	}
	for (int i = 0; i < 600; i++) {
		map[0][i] = 1;
		map[1183][i] = 1;
	}

	char read;
	FILE *entry;
	if (level == 1)
		entry = fopen("C:\\Mario\\stage1.txt", "r");
	else
		entry = fopen("C:\\Mario\\stage2.txt", "r");
	for (int j = 0; j < 18; j++) {
		for (int i = 0; i < 37; i++) {
			fscanf(entry, "%c", &read);
			if (read == '0') {
				blocks[blockslen].num = 3;
				blocks[blockslen].sizex = 1;
				blocks[blockslen].sizey = 1;
				blocks[blockslen].left = 32 * i;
				blocks[blockslen++].top = 32 * j + 24;
				for (int m = 0; m < 32; m++) {
					for (int n = 0; n < 32; n++) {
						map[32 * i + m][32 * j + n + 24] = 1;
					}
				}
			}
			if (read == 'C') {
				coins[coinslen].num = 4;
				coins[coinslen].left = 32 * i + 4;
				coins[coinslen++].top = 32 * j + 24;
			}
			if (read == 'D') {
				coinboxes[coinboxeslen].num = 5;
				coinboxes[coinboxeslen].left = 32 * i;
				coinboxes[coinboxeslen++].top = 32 * j + 24;
				for (int m = 0; m < 32; m++) {
					for (int n = 0; n < 32; n++) {
						map[32 * i + m][32 * j + n + 24] = 1;
					}
				}
			}
			if (read == 'E') {
				coinboxes[coinboxeslen].num = 6;
				coinboxes[coinboxeslen].spent = true;
				coinboxes[coinboxeslen].left = 32 * i;
				coinboxes[coinboxeslen++].top = 32 * j + 24;
				for (int m = 0; m < 32; m++) {
					for (int n = 0; n < 32; n++) {
						map[32 * i + m][32 * j + n + 24] = 1;
					}
				}
			}
			if (read == 'F') {
				bricks[brickslen].num = 7;
				bricks[brickslen].left = 32 * i;
				bricks[brickslen++].top = 32 * j + 24;
				for (int m = 0; m < 32; m++) {
					for (int n = 0; n < 32; n++) {
						map[32 * i + m][32 * j + n + 24] = 1;
					}
				}
			}
			if (read == 'M') {
				mushrooms[mushroomslen].num = 2;
				mushrooms[mushroomslen].left = 32 * i;
				mushrooms[mushroomslen++].top = 32 * j + 24;
			}
		}
		fscanf(entry, "%c", &read);
	}
}
void Stage::print() {
	for (int i = 0; i < 1184; i++)
		for (int j = 0; j < 600; j++)
			colormap.map[i][j] = SKY;
	for (int i = 0; i < blockslen; i++) {
		blocks[i].print();
	}
	for (int i = 0; i < coinslen; i++) {
		coins[i].print();
	}
	for (int i = 0; i < mushroomslen; i++) {
		mushrooms[i].print();
	}
	for (int i = 0; i < coinboxeslen; i++) {
		coinboxes[i].print();
	}
	for (int i = 0; i < brickslen; i++) {
		bricks[i].print();
	}
	for (int i = 0; i < 1184; i++)
		for (int j = 0; j < 600; j++)
			if (colormap.map[i][j] == SKY)
				SetPixelV((*mywindow), i, j, SKY);
}

void Stage::reprint() {
	for (int i = 0; i < 1184; i++)
		for (int j = 0; j < 600; j++)
			SetPixelV((*mywindow), i, j, colormap.map[i][j]);
}