#ifndef STAGE_H
#define STAGE_H
#include "stdafx.h"
#include "Elements.hpp"
class Stage{
	//0 = mario, 1 = luigi, 2 = mushroom. 3 = block, 4 = coin, 5 = coinbox, 6 = spentcoinbox, 7 = brick, 8 = bomb
public:
	HDC * mywindow;
	bool map[1184][600];
	Colormap colormap;
	Element blocks[666], coins[666], mushrooms[666], coinboxes[666], bricks[666], bombs[666], specialcoins[666];
	int blockslen, coinslen, mushroomslen, coinboxeslen, brickslen, bombslen;
	int level;
	void Initialize(HDC * windowpTr);
	void print();
	void reprint();
};


#endif