
#include "stdafx.h"
#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <time.h>
#include <string.h>
#include <windows.h>
#include <wingdi.h>
#include <iostream>
#include <math.h>
#include "Elements.h"
#include "Stage.h"
#include <mmsystem.h>
#pragma comment(lib,"Winmm.lib")
#using <mscorlib.dll>

using namespace std;
using namespace System::Threading;
using namespace System;

#define PI 3.1415926536
#define GRAVIDADE 650
#define VELOCIDADEMAXIMA 800
#define VELOCIDADEPULO 550
#define VELOCIDADEMIRA 150
#define VELOCIDADEANDAR 120
#define VELOCIDADECORRER 180
#define USERFORCE 200
#define CORRECAOCORDA 1.5
#define VELOCIDADESOBECORDA 75
#define TAMANHOMINIMOCORDA 25
#define TAMANHOMAXIMOCORDA 400
#define OMEGAMAXIMO 1

int gametime;
int points, maxplayers = 0;

//abreviaturas: R = red, L = blue, B = black, N = brown, Y = yellow, W = white, S = skin
//janela 148x50, letra 8x12. total: janela = 1184x600
//assim que descobrir como referenciar uma classe posterior, mudar points para dentro de game
//0 = mario, 1 = luigi, 2 = mushroom. 3 = block, 4 = coin, 5 = coinbox, 6 = spentcoinbox, 7 = brick, 8 = bomb

class Mario;

int Round(float x)
{
	return(int)(x + 0.5);
}

Stage stage;

class Mario
{
public:
	Element mario;
	Element aim;
	bool memoria;
	int tempocorda, xmemoria, ymemoria;
	Rope rope;
	Image any;
	bool onrope;
	int lastused;
	float aimdegree;
	int lastupdate;
	int playern;
	float velx, vely, realtop, realleft;
	bool alive, alreadyjumped, alreadybombed, alreadyroped;
	Mario()
	{
		tempocorda = 0;
		onrope = 0;
		aimdegree = 0;
		alreadyjumped = 0;
		alreadybombed = 0;
		++maxplayers;
		playern = maxplayers;
		mario.orientation = 0;
		mario.left = 100;
		mario.top = 200;
		aim.sizex = 1;
		aim.sizey = 1;
		aim.top = 20;
		aim.left = 20;
		aim.num = 9;
		mario.spent = 0;
		if (playern == 1)
			mario.num = 0;
		else
			mario.num = 1;
		realleft = mario.left;
		realtop = mario.top;
		velx = 0;
		vely = 0;
		alive = true;
		lastupdate = gametime;
	}
	void physics()
	{
		float deltat = (gametime - lastupdate) / 1000.0;
		int lasttop = mario.top, lastleft = mario.left;
		int k;
		for (int j = mario.top; j <= mario.bottom(); j++)
			for (int i = mario.left; i <= mario.right(); i++)
			{
				stage.map[i][j] = 0;
			}
		//MOVE DOWN
		//VELOCITY
		bool check = 1;
		if (mario.bottom() < 599)
		{
			for (int p = mario.left; p <= mario.right(); p++)
			{
				if (stage.map[p][mario.bottom() + 1] == 1)
					check = 0;
			}
		}
		else
		{
			check = 0;
		}
		if (check == 1 && vely < VELOCIDADEMAXIMA)
		{
			vely += GRAVIDADE * deltat;
		}
		else
		{
			if (vely > 0 && vely < VELOCIDADEMAXIMA)
				vely = 0;
		}
		//POSITION
		if (vely >= 0)
		{
			bool check2 = 1;
			if (Round(realtop + mario.sizey * 16 - 1 + vely * deltat) > 598)
				check2 = 0;
			else
				for (int q = Round(realtop + vely * deltat); q <= Round(realtop + mario.sizey * 16 - 1 + vely * deltat); q++)
					for (int p = mario.left; p <= mario.right(); p++)
					{
						if (stage.map[p][q] == 1)
						{
							check2 = 0;
						}
					}
			if (check2 == 1)
			{
				realtop += vely * deltat;
				mario.top = Round(realtop);
			}
			else
			{
				check2 = 1;
				for (k = Round(vely*deltat); k > 0; k--)
				{
					for (int p = mario.left; p <= mario.right(); p++)
						if (stage.map[p][mario.bottom() + 1] == 1)
						{
							check2 = 0;
						}
					if (mario.bottom() > 598)
					{
						check2 = 0;
					}
					if (check2 == 1)
					{
						++mario.top;
					}
				}
				realtop = mario.top;
			}
		}
		else
		{
			//MOVE UP
			//VELOCITY
			vely += GRAVIDADE * deltat;
			bool check = 1;
			if (mario.top != 0)
			{
				for (int p = mario.left; p <= mario.right(); p++)
					if (stage.map[p][mario.top - 1] == 1)
					{
						check = 0;
					}
			}
			else
			{
				vely = 0;
				check = 0;
			}
			if (check == 1)
			{
				//POSITION
				int check2 = 1;
				if (Round(realtop + vely * deltat) < 0)
					check2 = 0;
				else
					for (int p = mario.left; p <= mario.right(); p++)
					{
						if (stage.map[p][Round(realtop + vely * deltat)] == 1)
						{
							check2 = 0;
						}
					}
				if (check2 == 1)
				{
					realtop += vely * deltat;
					mario.top = Round(realtop);
				}
				else
				{
					check2 = 1;
					for (k = Round(vely*deltat); k < 0; k++)
					{
						for (int p = mario.left; p <= mario.right(); p++)
							if (stage.map[p][mario.top - 1] == 1)
							{
								check2 = 0;
							}
						if (mario.top == 0)
						{
							check2 = 0;
						}
						if (check2 == 1)
						{
							--mario.top;
						}
					}
					realtop = mario.top;
				}
			}
			else
			{
				vely = 0;
			}
		}
		//MOVE RIGHT
		check = 1;
		if (velx >= 0)
		{
			if (mario.right() != 1183)
			{
				for (int p = mario.top; p <= mario.bottom(); p++)
					if (stage.map[mario.right() + 1][p] == 1)
					{
						check = 0;
					}
			}
			else
			{
				velx = 0;
			}
			if (check == 1)
			{
				//POSITION
				int check2 = 1;
				if (Round(realleft + 23 + velx * deltat) > 1183)
					check2 = 0;
				else
					for (int p = mario.top; p <= mario.bottom(); p++)
					{
						if (stage.map[Round(realleft + 23 + velx * deltat)][p] == 1)
						{
							check2 = 0;
						}
					}
				if (check2 == 1)
				{
					realleft += velx * deltat;
					mario.left = Round(realleft);
				}
				else
				{
					check2 = 1;
					for (k = Round(velx*deltat); k > 0; k--)
					{
						for (int p = mario.top; p <= mario.bottom(); p++)
							if (stage.map[mario.right() + 1][p] == 1)
							{
								check2 = 0;
							}
						if (mario.right() == 1183)
						{
							check2 = 0;
						}
						if (check2 == 1)
						{
							++mario.left;
						}
					}
					realleft = mario.left;
				}

			}
			else
			{
				velx = 0;
			}
		}
		else
		{
			//MOVE LEFT
			check = 1;
			if (mario.left != 0)
			{
				for (int p = mario.top; p <= mario.bottom(); p++)
					if (stage.map[mario.left - 1][p])
					{
						check = 0;
					}
			}
			else
			{
				velx = 0;
			}
			if (check == 1)
			{
				//POSITION
				int check2 = 1;
				if (Round(realleft + velx * deltat) < 0)
					check2 = 0;
				else
					for (int p = mario.top; p <= mario.bottom(); p++)
					{
						if (stage.map[Round(realleft + velx * deltat)][p] == 1)
						{
							check2 = 0;
						}
					}
				if (check2 == 1)
				{
					realleft += velx * deltat;
					mario.left = Round(realleft);
				}
				else
				{
					check2 = 1;
					for (k = Round(velx*deltat); k < 0; k++)
					{
						for (int p = mario.top; p <= mario.bottom(); p++)
							if (stage.map[mario.left - 1][p] == 1)
							{
								check2 = 0;
							}
						if (mario.left == 0)
						{
							check2 = 0;
						}
						if (check2 == 1)
						{
							--mario.left;
						}
					}
					realleft = mario.left;
				}
			}
			else
			{
				velx = 0;
			}
		}

		if (mario.bottom() > 597)
			alive = false;
		if (mario.top != lasttop || mario.left != lastleft)
		{
			int auxiliary = mario.top;
			int auxiliarx = mario.left;
			mario.top = lasttop;
			mario.left = lastleft;
			mario.erase();
			mario.top = auxiliary;
			mario.left = auxiliarx;
			mario.print();
		}
		for (int j = mario.top; j <= mario.bottom(); j++)
			for (int i = mario.left; i <= mario.right(); i++)
			{
				stage.map[i][j] = 1;
			}
	}
	void getkey()
	{
		if (GetAsyncKeyState(0x11) && GetAsyncKeyState(0x52))
		{
			stage.reprint();
		}
		if (maxplayers == 1)
		{
			if (GetAsyncKeyState(0x0D) && !alreadybombed)
			{
				alreadybombed = 1;
				if (mario.orientation == 0)
				{
					bool check = 1;
					for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
						for (int i = mario.right() + 1; i <= mario.right() + 19; i++)
							if (stage.map[i][j] == 1)
								check = 0;
					if (check == 1)
					{
						stage.bombs[stage.bombslen].num = 8;
						stage.bombs[stage.bombslen].sizex = 1;
						stage.bombs[stage.bombslen].sizey = 1;
						stage.bombs[stage.bombslen].top = mario.bottom() - 28;
						stage.bombs[stage.bombslen].left = mario.right() + 1;
						stage.bombs[stage.bombslen].timeofdeath = gametime;
						stage.bombs[stage.bombslen++].print();
						for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
							for (int i = mario.right() + 1; i <= mario.right() + 19; i++)
								stage.map[i][j] = 1;
					}
				}
				else
				{
					bool check = 1;
					for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
						for (int i = mario.left - 11; i >= mario.left - 29; i--)
							if (stage.map[i][j] == 1)
								check = 0;
					if (check == 1)
					{
						stage.bombs[stage.bombslen].num = 8;
						stage.bombs[stage.bombslen].sizex = 1;
						stage.bombs[stage.bombslen].sizey = 1;
						stage.bombs[stage.bombslen].top = mario.bottom() - 28;
						stage.bombs[stage.bombslen].left = mario.left - 29;
						stage.bombs[stage.bombslen].timeofdeath = gametime;
						stage.bombs[stage.bombslen++].print();
						for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
							for (int i = mario.left - 11; i >= mario.left - 29; i--)
								stage.map[i][j] = 1;
					}
				}
			}
			else
			{
				if (!(GetAsyncKeyState(0x20) || GetAsyncKeyState(0x0D)))
					alreadybombed = 0;
			}
			if ((GetAsyncKeyState(0x44) || GetAsyncKeyState(0x27)) && !GetAsyncKeyState(0xA0))
			{
				if (mario.orientation == 1)
				{
					mario.erase();
					mario.orientation = 0;
					mario.print();
				}
				velx = VELOCIDADEANDAR;
			}
			else if ((GetAsyncKeyState(0x41) || GetAsyncKeyState(0x25)) && !GetAsyncKeyState(0xA0))
			{
				if (mario.orientation == 0)
				{
					mario.erase();
					mario.orientation = 1;
					mario.print();
				}
				velx = -VELOCIDADEANDAR;
			}
			else if ((GetAsyncKeyState(0x44) || GetAsyncKeyState(0x27)) && GetAsyncKeyState(0xA0))
			{
				if (mario.orientation == 1)
				{
					mario.erase();
					mario.orientation = 0;
					mario.print();
				}
				velx = VELOCIDADECORRER;
			}
			else if ((GetAsyncKeyState(0x41) || GetAsyncKeyState(0x25)) && GetAsyncKeyState(0xA0))
			{
				if (mario.orientation == 0)
				{
					mario.erase();
					mario.orientation = 1;
					mario.print();
				}
				velx = -VELOCIDADECORRER;
			}
			if ((GetAsyncKeyState(0x57) || GetAsyncKeyState(0x26)) && !alreadyjumped)
			{
				alreadyjumped = 1;
				bool check = 0;
				for (int p = mario.left; p <= mario.right(); p++)
				{
					if (stage.map[p][mario.bottom() + 1] == 1)
						check = 1;
				}
				if (check == 1)
				{
					vely = -VELOCIDADEPULO;
				}
				//ativar essa parte do código se quiser liberar escalada
				//			if (check == 0)
				//				if ((stage.map[mario.left - 1][mario.bottom() + 1] == 0 && orientation == 1) || (stage.map[mario.right() + 1][mario.bottom() + 1] != 1 && orientation == 0))
				//					vely = -200;
			}
			else
			{
				if (!(GetAsyncKeyState(0x57) || GetAsyncKeyState(0x26)))
					alreadyjumped = 0;
			}
			if (GetAsyncKeyState(0x51))
			{
				aimdegree += (VELOCIDADEMIRA * PI / 180)*(gametime - lastupdate) / 1000;
				lastused = gametime;
			}
			if (GetAsyncKeyState(0x45))
			{
				aimdegree -= (VELOCIDADEMIRA * PI / 180)*(gametime - lastupdate) / 1000;
				lastused = gametime;
			}
			if (GetAsyncKeyState(0x20))
			{
				if (!alreadyroped){
					alreadyroped = 1;
					bool check = 0;
					for (float i = 1; (i < 30) && Round(i*(aim.left + 3) + (1 - i)*(mario.left + 12)) > 5 &&
						Round(i*(aim.left + 3) + (1 - i)*(mario.left + 12)) < 1160 &&
						Round(i*(aim.top + 3) + (1 - i)*(mario.top + 12)) > 5 &&
						Round(i*(aim.top + 3) + (1 - i)*(mario.top + 12)) < 580; i += 0.01)
						if (stage.map[Round(i*(aim.left + 3) + (1 - i)*(mario.left + 12))][Round(i*(aim.top + 3) + (1 - i)*(mario.top + 12))])
						{
							rope.x[0] = Round(i*(aim.left + 3) + (1 - i)*(mario.left + 12));
							rope.y[0] = Round(i*(aim.top + 3) + (1 - i)*(mario.top + 12));
							rope.x[1] = mario.left + 12;
							rope.y[1] = mario.top + 12;
							check = 1;
							rope.w = 0;
							onrope = 1;
							rope.n = 1;
							rope.print();
							rope.len = sqrt((rope.x[rope.n] - rope.x[rope.n - 1])*(rope.x[rope.n] - rope.x[rope.n - 1]) + (rope.y[rope.n] - rope.y[rope.n - 1])*(rope.y[rope.n] - rope.y[rope.n - 1]));
							if (rope.x[0] < mario.left + 12)
								rope.teta[1] = asin((rope.y[1] - rope.y[0]) / rope.len);
							else
								rope.teta[1] = PI - asin((rope.y[1] - rope.y[0]) / rope.len);
							break;
						}
				}
			}
			else {
				alreadyroped = 0;
			}
		}
	}
	void checkcoin()
	{
		for (int i = 0; i < stage.coinslen; i++)
			if (((mario.right() >= stage.coins[i].right() && mario.left <= stage.coins[i].right()) ||
				(mario.left <= stage.coins[i].left && mario.right() >= stage.coins[i].left) ||
				(mario.right() - 2 <= stage.coins[i].right() && mario.left + 2 >= stage.coins[i].left)) &&
				((mario.bottom() >= stage.coins[i].bottom() && mario.top <= stage.coins[i].bottom()) ||
				(mario.top <= stage.coins[i].top && mario.bottom() >= stage.coins[i].top)) &&
				stage.coins[i].spent == false)
			{
				stage.coins[i].spent = true;
				stage.coins[i].erase();
				mario.print();
				++points;
			}
	}
	void checkmushroom()
	{
		for (int i = 0; i < stage.coinslen; i++)
			if (((mario.right() >= stage.mushrooms[i].right() && mario.left <= stage.mushrooms[i].right()) ||
				(mario.left <= stage.mushrooms[i].left && mario.right() >= stage.mushrooms[i].left) ||
				(mario.right() <= stage.mushrooms[i].right() && mario.left >= stage.mushrooms[i].left)) &&
				((mario.bottom() >= stage.mushrooms[i].bottom() && mario.top <= stage.mushrooms[i].bottom()) ||
				(mario.top <= stage.mushrooms[i].top && mario.bottom() >= stage.mushrooms[i].top)) &&
				stage.mushrooms[i].spent == false)
			{
				stage.mushrooms[i].spent = true;
				stage.mushrooms[i].erase();
				if (mario.sizey == 2)
				{
					for (int j = mario.top; j <= mario.bottom(); j++)
						for (int i = mario.left; i <= mario.right(); i++)
						{
							stage.map[i][j] = 0;
						}
					mario.erase();
					mario.sizey = 3;
					if (!onrope){
					mario.top -= 16;
					mario.left -= 12;
					mario.print();

					}
					else {
						rope.erase();
						mario.top -= 16;
						mario.left -= 12;
						rope.x[rope.n] -= 16;
						rope.y[rope.n] -= 12;
						rope.len = sqrt((rope.x[rope.n] - rope.x[rope.n - 1])*(rope.x[rope.n] - rope.x[rope.n - 1]) + (rope.y[rope.n] - rope.y[rope.n - 1])*(rope.y[rope.n] - rope.y[rope.n - 1]));
					}
					for (int j = mario.top; j <= mario.bottom(); j++)

						for (int i = mario.left; i <= mario.right(); i++)
						{
							stage.map[i][j] = 1;
						}
				}
			}
	}
	void checkbox()
	{
		for (int i = 0; i < stage.coinboxeslen; i++)
			if (((mario.right() - 2 >= stage.coinboxes[i].right() && mario.left + 2 <= stage.coinboxes[i].right()) ||
				(mario.left + 2 <= stage.coinboxes[i].left && mario.right() - 2 >= stage.coinboxes[i].left) ||
				(mario.right() - 2 <= stage.coinboxes[i].right() && mario.left + 2 >= stage.coinboxes[i].left)) &&
				stage.coinboxes[i].spent == false && (stage.coinboxes[i].bottom() - mario.top) == -1 &&
				stage.coinboxes[i].timeofdeath == 0)
			{
				stage.coinboxes[i].timeofdeath = gametime;
				stage.specialcoins[i].num = 4;
				stage.specialcoins[i].left = stage.coinboxes[i].left;
				stage.specialcoins[i].top = stage.coinboxes[i].top - 32;
				stage.specialcoins[i].print();
				stage.coinboxes[i].num = 6;
				stage.coinboxes[i].print();
				++points;
			}
			else if (stage.coinboxes[i].timeofdeath != 0 &&
				gametime > stage.coinboxes[i].timeofdeath + 500 && stage.coinboxes[i].spent == false)
			{
				stage.coinboxes[i].spent = true;
				stage.specialcoins[i].erase();
			}
	}
	void checkbrick()
	{
		for (int i = 0; i < stage.brickslen; i++)
			if (((mario.right() - 2 >= stage.bricks[i].right() && mario.left + 2 <= stage.bricks[i].right()) ||
				(mario.left + 2 <= stage.bricks[i].left && mario.right() - 2 >= stage.bricks[i].left) ||
				(mario.right() - 2 <= stage.bricks[i].right() && mario.left + 2 >= stage.bricks[i].left)) &&
				stage.bricks[i].spent == false && (stage.bricks[i].bottom() - mario.top) == -1)
			{
				stage.bricks[i].spent = true;
				stage.bricks[i].erase();
				vely = 0;
				for (int m = stage.bricks[i].top; m <= stage.bricks[i].bottom(); m++)
				{
					for (int n = stage.bricks[i].left; n <= stage.bricks[i].right(); n++)
					{
						stage.map[n][m] = 0;
					}
				}
			}
	}
	void checkbomb()
	{
		for (int i = 0; i < stage.bombslen; i++)
			if (stage.bombs[i].spent == false && gametime - stage.bombs[i].timeofdeath > 2000)
			{
				if (playern == maxplayers)
					stage.bombs[i].spent = true;
				stage.bombs[i].erase();
				for (int j = stage.bombs[i].top; j <= stage.bombs[i].bottom(); j++)
				{
					for (int k = stage.bombs[i].left; k <= stage.bombs[i].right() - 10; k++)
						stage.map[k][j] = 0;
				}
				for (int t = 0; t < stage.brickslen; t++)
				{
					if ((abs(stage.bricks[t].middlex() - stage.bombs[i].middlex()) < 50) && (abs(stage.bricks[t].middley() - stage.bombs[i].middley()) < 50))
					{
						for (int k = stage.bricks[t].top; k <= stage.bricks[t].bottom(); k++)
							for (int j = stage.bricks[t].left; j <= stage.bricks[t].right(); j++)
								stage.map[j][k] = 0;
						stage.bricks[t].erase();
					}
				}
				if (onrope){
					for (int t = 0; t < rope.n; t++)
					{
						if (((rope.x[t] - stage.bombs[i].middlex()) < 50) && (abs(rope.y[t] - stage.bombs[i].middley()) < 50))
						{
							rope.eraseall();
							onrope = 0;
							realtop = mario.top;
							realleft = mario.left;
							velx = -rope.w *rope.len * sin(rope.teta[rope.n]);
							vely = -rope.w * rope.len * cos(rope.teta[rope.n]);
						}
					}
				}
				for (int t = 0; t < stage.blockslen; t++)
				{
					if ((abs(stage.blocks[t].middlex() - stage.bombs[i].middlex()) < 50) && (abs(stage.blocks[t].middley() - stage.bombs[i].middley()) < 50))
					{
						for (int k = stage.blocks[t].top; k <= stage.blocks[t].bottom(); k++)
							for (int j = stage.blocks[t].left; j <= stage.blocks[t].right(); j++)
								stage.map[j][k] = 0;
						stage.blocks[t].erase();
					}
				}
				//player//
				if ((abs(mario.middlex() - stage.bombs[i].middlex()) < 60) && (abs(mario.middley() - stage.bombs[i].middley()) < 60))
				{
					if (mario.sizey == 2)
					{
						alive = false;
					}
					else
					{
						for (int n = mario.top; n <= mario.bottom(); n++)
							for (int m = mario.left; m <= mario.right(); m++)
								stage.map[m][n] = 0;
						mario.erase();
						mario.sizey = 2;
						mario.print();
						if (onrope){
							rope.eraseall();
							onrope = 0;
							realtop = mario.top;
							realleft = mario.left;
							velx = -rope.w *rope.len * sin(rope.teta[rope.n]);
							vely = -rope.w * rope.len * cos(rope.teta[rope.n]);
						}
						for (int n = mario.top; n <= mario.bottom(); n++)
							for (int m = mario.left; m <= mario.right(); m++)
								stage.map[m][n] = 1;
					}
				}
			}
	}
	void bombphysics()
	{
		float deltat = (gametime - lastupdate) / 1000.0;
		for (int z = 0; z < stage.bombslen; z++)
		{
			int lasttop = stage.bombs[z].top;
			if (stage.bombs[z].spent == false)
			{
				int lasttop = stage.bombs[z].top;
				int k;
				for (int j = stage.bombs[z].top; j <= stage.bombs[z].bottom(); j++)
					for (int i = stage.bombs[z].left; i <= stage.bombs[z].right() - 10; i++)
					{
						stage.map[i][j] = 0;
					}
				//MOVE DOWN
				//VELOCITY
				bool check = 1;
				if (stage.bombs[z].bottom() < 599)
				{
					for (int p = stage.bombs[z].left; p <= stage.bombs[z].right() - 10; p++)
					{
						if (stage.map[p][stage.bombs[z].bottom() + 1] == 1)
							check = 0;
					}
				}
				else
				{
					check = 0;
				}
				if (check == 1 && stage.bombs[z].vely < VELOCIDADEMAXIMA)
				{
					stage.bombs[z].vely += GRAVIDADE * deltat;
				}
				else
				{
					if (stage.bombs[z].vely < VELOCIDADEMAXIMA)
						stage.bombs[z].vely = 0;
				}
				//POSITION
				if (stage.bombs[z].vely >= 0)
				{
					bool check2 = 1;
					if (Round(stage.bombs[z].top + 28 + stage.bombs[z].vely * deltat) > 598)
						check2 = 0;
					else
						for (int p = stage.bombs[z].left; p <= stage.bombs[z].right() - 10; p++)
						{
							if (stage.map[p][Round(stage.bombs[z].top + 28 + stage.bombs[z].vely * deltat)] == 1)
							{
								check2 = 0;
							}
						}
					if (check2 == 1)
					{
						stage.bombs[z].top = Round(stage.bombs[z].top + stage.bombs[z].vely * deltat);
					}
					else
					{
						check2 = 1;
						for (k = Round(stage.bombs[z].vely*deltat); k > 0; k--)
						{
							for (int p = stage.bombs[z].left; p <= stage.bombs[z].right() - 10; p++)
								if (stage.map[p][stage.bombs[z].bottom() + 1] == 1)
								{
									check2 = 0;
								}
							if (stage.bombs[z].bottom() > 598)
							{
								check2 = 0;
							}
							if (check2 == 1)
							{
								++stage.bombs[z].top;
							}
						}
					}
				}
				if (lasttop != stage.bombs[z].top)
				{
					int auxiliar = stage.bombs[z].top;
					stage.bombs[z].top = lasttop;
					stage.bombs[z].erase();
					stage.bombs[z].top = auxiliar;
					stage.bombs[z].print();
				}
				for (int j = stage.bombs[z].top; j <= stage.bombs[z].bottom(); j++)
					for (int i = stage.bombs[z].left; i <= stage.bombs[z].right() - 10; i++)
					{
						stage.map[i][j] = 1;
					}
			}
		}
	}
	void aimengine()
	{
		aim.erase();
		if (gametime - lastused < 4000)
		{
			aim.top = mario.middley() - Round(30 * sin(aimdegree)) - 3;
			aim.left = mario.middlex() + (30 * cos(aimdegree)) - 3;
			aim.print();
		}
	}
	void ropephysics()
	{
		Console::SetCursorPosition(0, 0);
		printf("%d", rope.n);
		for (int j = mario.top; j <= mario.bottom(); j++)
			for (int i = mario.left; i <= mario.right(); i++)
			{
				stage.map[i][j] = 0;
			}
		int newtop, newleft;
		float deltat = (gametime - lastupdate) / 1000.0;
		//1 parte: detectar se há nó desfeito
		rope.eraseall();
		if (rope.n > 1)
		{
			if (rope.side[rope.n] == 0 && rope.teta[rope.n] < rope.teta[rope.n - 1])
			{
				xmemoria = rope.x[rope.n - 1];
				ymemoria = rope.y[rope.n - 1];
				float velocidade = rope.w * rope.len;
				rope.x[rope.n - 1] = rope.x[rope.n];
				rope.y[rope.n - 1] = rope.y[rope.n];
				--rope.n;
				rope.len = sqrt((rope.x[rope.n] - rope.x[rope.n - 1])*(rope.x[rope.n] - rope.x[rope.n - 1]) + (rope.y[rope.n] - rope.y[rope.n - 1])*(rope.y[rope.n] - rope.y[rope.n - 1]));
				rope.w = velocidade / rope.len;
				memoria = 0;
				tempocorda = gametime;
			}
			else if (rope.side[rope.n] == 1 && rope.teta[rope.n] > rope.teta[rope.n - 1])
			{
				xmemoria = rope.x[rope.n - 1];
				ymemoria = rope.y[rope.n - 1];
				float velocidade = rope.w * rope.len;
				rope.x[rope.n - 1] = rope.x[rope.n];
				rope.y[rope.n - 1] = rope.y[rope.n];
				--rope.n;
				rope.len = sqrt((rope.x[rope.n] - rope.x[rope.n - 1])*(rope.x[rope.n] - rope.x[rope.n - 1]) + (rope.y[rope.n] - rope.y[rope.n - 1])*(rope.y[rope.n] - rope.y[rope.n - 1]));
				rope.w = velocidade / rope.len;
				memoria = 1;
				tempocorda = gametime;
			}
		}
		//2 parte: atualizar velocidade
		float intendedteta;
		rope.w += cos(rope.teta[rope.n]) * GRAVIDADE * deltat / (rope.len*CORRECAOCORDA);
		if (rope.w < OMEGAMAXIMO && rope.w > - OMEGAMAXIMO)
			rope.w += rope.userforce*deltat / (rope.len*CORRECAOCORDA);
		intendedteta = rope.teta[rope.n] + rope.w*deltat;
		//3 parte
		float i = rope.teta[rope.n];
		bool check = true;
		bool jafoi = false;
		newtop = Round(rope.y[rope.n - 1] + rope.len*sin(i));
		newleft = Round(rope.x[rope.n - 1] + rope.len*cos(i));
		if (rope.w > 0.005)
			while (i < intendedteta && check == true)
			{
				i += 0.01;
				newtop = Round(rope.y[rope.n - 1] + rope.len*sin(i));
				newleft = Round(rope.x[rope.n - 1] + rope.len*cos(i));
				for (int n = newtop - 12; n <= newtop + mario.sizey * 16 - 13; n++)
					for (int m = newleft - 12; m <= newleft + 11; m++)
						if (stage.map[m][n] == 1 && check == true)
						{
							rope.w = 0;
							i -= 0.01;
							newtop = Round(rope.y[rope.n - 1] + rope.len*sin(i));
							newleft = Round(rope.x[rope.n - 1] + rope.len*cos(i));
							check = false;
						}
				if (check){
					for (double f = 0; f < 0.98; f += 0.001){
						if (stage.map[Round(f*rope.x[rope.n - 1] + (1 - f)*newleft)][Round(f*rope.y[rope.n - 1] + (1 - f)*newtop)]&&!jafoi){
							if (fabs((float)(f*rope.x[rope.n - 1] + (1 - f)*newleft - rope.x[rope.n - 1] > 10)) || fabs(f*rope.y[rope.n - 1] + (1 - f)*newtop - rope.y[rope.n - 1]) > 10){
								if (!(gametime - tempocorda < 1000 && memoria == 1)
									|| (fabs((float)(f*rope.x[rope.n - 1] + (1 - f)*newleft - xmemoria > 10))
									|| fabs(f*rope.y[rope.n - 1] + (1 - f)*newtop - ymemoria) > 10))
								{
									jafoi = 1;
									float velocidade = rope.w * rope.len;
									rope.teta[rope.n] = i;
									rope.side[rope.n + 1] = 0;
									rope.x[rope.n] = Round(f*rope.x[rope.n - 1] + (1 - f)*newleft);
									rope.y[rope.n++] = Round(f*rope.y[rope.n - 1] + (1 - f)*newtop);
									rope.len = sqrt((newleft - rope.x[rope.n - 1])*(newleft - rope.x[rope.n - 1]) + (newtop - rope.y[rope.n - 1])*(newtop - rope.y[rope.n - 1]));
									rope.w = velocidade / rope.len;
									break;
								}
							}
						}
					}
				}
			}
		else if (rope.w < -0.005)
			while (i > intendedteta && check == true)
			{
				i -= 0.01;
				newtop = Round(rope.y[rope.n - 1] + rope.len*sin(i));
				newleft = Round(rope.x[rope.n - 1] + rope.len*cos(i));
				for (int n = newtop - 12; n <= newtop + mario.sizey * 16 - 13; n++)
					for (int m = newleft - 12; m <= newleft + 11; m++)
						if (stage.map[m][n] == 1 && check == true)
						{
							rope.w = 0;
							i += 0.01;
							newtop = Round(rope.y[rope.n - 1] + rope.len*sin(i));
							newleft = Round(rope.x[rope.n - 1] + rope.len*cos(i));
							check = false;
						}
				if (check){
					for (double f = 0; f < 0.98; f += 0.0001){
						if (stage.map[Round(f*rope.x[rope.n - 1] + (1 - f)*newleft)][Round(f*rope.y[rope.n - 1] + (1 - f)*newtop)]&&!jafoi){
							if (fabs(f*rope.x[rope.n - 1] + (1 - f)*newleft - rope.x[rope.n - 1]) > 10 || fabs(f*rope.y[rope.n - 1] + (1 - f)*newtop - rope.y[rope.n - 1]) > 10){
								if (!(gametime - tempocorda < 1000 && memoria == 1)
									|| (fabs((float)(f*rope.x[rope.n - 1] + (1 - f)*newleft - xmemoria > 10))
									|| fabs(f*rope.y[rope.n - 1] + (1 - f)*newtop - ymemoria) > 10))
								{
									jafoi = 1;
									float velocidade = rope.w * rope.len;
									rope.teta[rope.n] = i;
									rope.side[rope.n + 1] = 1;
									rope.x[rope.n] = Round(f*rope.x[rope.n - 1] + (1 - f)*newleft);
									rope.y[rope.n++] = Round(f*rope.y[rope.n - 1] + (1 - f)*newtop);
									rope.len = sqrt((newleft - rope.x[rope.n - 1])*(newleft - rope.x[rope.n - 1]) + (newtop - rope.y[rope.n - 1])*(newtop - rope.y[rope.n - 1]));
									rope.w = velocidade / rope.len;
									break;
								}
							}
						}
					}
				}

			}
		mario.erase();
		mario.top = newtop - 12;
		mario.left = newleft - 12;
		rope.teta[rope.n] = i;
		rope.x[rope.n] = mario.left + 12;
		rope.y[rope.n] = mario.top + 12;
		mario.print();
		rope.printall();							
		for (int j = mario.top; j <= mario.bottom(); j++)
			for (int i = mario.left; i <= mario.right(); i++)
			{
				stage.map[i][j] = 1;
			}
	}
	void ropegetkey()
	{
		if (GetAsyncKeyState(0x11) && GetAsyncKeyState(0x52))
		{
			stage.reprint();
		}
		if (maxplayers == 1)
		{
			if ((GetAsyncKeyState(0x0D)) && !alreadybombed)
			{
				alreadybombed = 1;
				if (mario.orientation == 1)
				{
					bool check = 1;
					for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
						for (int i = mario.right() + 1; i <= mario.right() + 19; i++)
							if (stage.map[i][j] == 1)
								check = 0;
					if (check == 1)
					{
						stage.bombs[stage.bombslen].num = 8;
						stage.bombs[stage.bombslen].sizex = 1;
						stage.bombs[stage.bombslen].sizey = 1;
						stage.bombs[stage.bombslen].top = mario.bottom() - 28;
						stage.bombs[stage.bombslen].left = mario.right() + 1;
						stage.bombs[stage.bombslen].timeofdeath = gametime;
						stage.bombs[stage.bombslen++].print();
						for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
							for (int i = mario.right() + 1; i <= mario.right() + 19; i++)
								stage.map[i][j] = 1;
					}
				}
				else
				{
					bool check = 1;
					for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
						for (int i = mario.left - 11; i >= mario.left - 29; i--)
							if (stage.map[i][j] == 1)
								check = 0;
					if (check == 1)
					{
						stage.bombs[stage.bombslen].num = 8;
						stage.bombs[stage.bombslen].sizex = 1;
						stage.bombs[stage.bombslen].sizey = 1;
						stage.bombs[stage.bombslen].top = mario.bottom() - 28;
						stage.bombs[stage.bombslen].left = mario.left - 29;
						stage.bombs[stage.bombslen].timeofdeath = gametime;
						stage.bombs[stage.bombslen++].print();
						for (int j = mario.bottom() - 28; j <= mario.bottom(); j++)
							for (int i = mario.left - 11; i >= mario.left - 29; i--)
								stage.map[i][j] = 1;
					}
				}
			}
			else
			{
				if (!(GetAsyncKeyState(0x20) || GetAsyncKeyState(0x0D)))
					alreadybombed = 0;
			}
			if ((GetAsyncKeyState(0x44) || GetAsyncKeyState(0x27)))
			{
				if (mario.orientation == 1)
				{
					mario.erase();
					mario.orientation = 0;
					mario.print();
				}
				if (rope.y[rope.n] >= rope.y[rope.n - 1])
					rope.userforce = -USERFORCE;
				else
					rope.userforce = USERFORCE;
			}
			else if ((GetAsyncKeyState(0x41) || GetAsyncKeyState(0x25)))
			{
				if (mario.orientation == 0)
				{
					mario.erase();
					mario.orientation = 1;
					mario.print();
				}
				if (rope.y[rope.n] >= rope.y[rope.n - 1])
					rope.userforce = USERFORCE;
				else
					rope.userforce = -USERFORCE;
			}
			if ((GetAsyncKeyState(0x26) || GetAsyncKeyState(0x57)))
			{
				
				for (int j = mario.top; j <= mario.bottom(); j++)
					for (int i = mario.left; i <= mario.right(); i++)
					{
						stage.map[i][j] = 0;
					}
				float deltat = (gametime - lastupdate) / 1000.0;
				if (rope.len > deltat * VELOCIDADESOBECORDA + TAMANHOMINIMOCORDA)
				{
					float velocidade = rope.w*rope.len;
					rope.erase();
					int newtop = Round(rope.y[rope.n - 1] + rope.len*sin(rope.teta[rope.n]));
					int newleft = Round(rope.x[rope.n - 1] + rope.len*cos(rope.teta[rope.n]));
					float intendedlen = rope.len - deltat * VELOCIDADESOBECORDA;
					float i = rope.len;
					bool check = true;
					for (; (i > intendedlen) && check == true;)
					{
						i -= 1;
						newtop = Round(rope.y[rope.n - 1] + i*sin(rope.teta[rope.n]));
						newleft = Round(rope.x[rope.n - 1] + i*cos(rope.teta[rope.n]));
						for (int n = newtop - 12; n <= newtop + mario.sizey * 16 - 13; n++)
							for (int m = newleft - 12; m <= newleft + 11; m++)
								if (stage.map[m][n] == 1 && check == true)
								{
									i += 1;
									newtop = Round(rope.y[rope.n - 1] + (i)*sin(rope.teta[rope.n]));
									newleft = Round(rope.x[rope.n - 1] + (i)*cos(rope.teta[rope.n]));
									check = false;
								}
					}
					mario.erase();
					rope.len = i;
					rope.w = velocidade / rope.len;
					mario.top = newtop - 12;
					mario.left = newleft - 12;
					rope.x[rope.n] = newleft;
					rope.y[rope.n] = newtop;
					for (int j = mario.top; j <= mario.bottom(); j++)
						for (int i = mario.left; i <= mario.right(); i++)
						{
							stage.map[i][j] = 1;
						}
				}
			}
			if ((GetAsyncKeyState(0x28) || GetAsyncKeyState(0x53)))
			{
				float velocidade = rope.len * rope.w;
				for (int j = mario.top; j <= mario.bottom(); j++)
					for (int i = mario.left; i <= mario.right(); i++)
					{
						stage.map[i][j] = 0;
					}
				float deltat = (gametime - lastupdate) / 1000.0;
				if (rope.len < TAMANHOMAXIMOCORDA - deltat * VELOCIDADESOBECORDA)
				{
					rope.erase();
					int newtop = Round(rope.y[rope.n - 1] + rope.len*sin(rope.teta[rope.n]));
					int newleft = Round(rope.x[rope.n - 1] + rope.len*cos(rope.teta[rope.n]));
					float intendedlen = rope.len + deltat * VELOCIDADESOBECORDA;
					float i = rope.len;
					bool check = true;
					for (; (i < intendedlen) && check == true;)
					{
						i += 1;
						newtop = Round(rope.y[rope.n - 1] + i*sin(rope.teta[rope.n]));
						newleft = Round(rope.x[rope.n - 1] + i*cos(rope.teta[rope.n]));
						for (int n = newtop - 12; n <= newtop + mario.sizey * 16 - 13; n++)
							for (int m = newleft - 12; m <= newleft + 11; m++)
								if (stage.map[m][n] == 1 && check == true)
								{
									i -= 1;
									newtop = Round(rope.y[rope.n - 1] + (i)*sin(rope.teta[rope.n]));
									newleft = Round(rope.x[rope.n - 1] + (i)*cos(rope.teta[rope.n]));
									check = false;
								}
					}
					mario.erase();
					rope.len = i;
					rope.w = velocidade / rope.len;
					mario.top = newtop - 12;
					mario.left = newleft - 12;
					rope.x[rope.n] = newleft;
					rope.y[rope.n] = newtop;
					for (int j = mario.top; j <= mario.bottom(); j++)
						for (int i = mario.left; i <= mario.right(); i++)
						{
							stage.map[i][j] = 1;
						}
				}
			}

			if (GetAsyncKeyState(0x51))
			{
				aimdegree += (VELOCIDADEMIRA * PI / 180)*(gametime - lastupdate) / 1000;
				lastused = gametime;
			}
			if (GetAsyncKeyState(0x45))
			{
				aimdegree -= (VELOCIDADEMIRA * PI / 180)*(gametime - lastupdate) / 1000;
				lastused = gametime;
			}
			if (GetAsyncKeyState(0x20))
			{
				if (!alreadyroped){
					alreadyroped = 1;
					rope.eraseall();
					onrope = 0;
					realtop = mario.top;
					realleft = mario.left;
					velx = -rope.w *rope.len * sin(rope.teta[rope.n]);
					vely = -rope.w * rope.len * cos(rope.teta[rope.n]);
				}
			}
			else {
				alreadyroped = 0;
			}
		}
	}
	void play()
	{
		if (!onrope)
		{
			getkey();
		}
		else
		{
			ropegetkey();
		}
		if (!onrope)
		{
			physics();
		}
		else
		{
			ropephysics();
		}
		bool check = 0;
		if (velx == VELOCIDADEANDAR || velx == VELOCIDADECORRER || velx == -VELOCIDADEANDAR || velx == -VELOCIDADECORRER)
			check = 1;
		for (int p = mario.left; p <= mario.right(); p++)
		{
			if (stage.map[p][mario.bottom() + 1] == 1)
				check = 1;
		}		
		if (check == 1)
			velx = 0;
		rope.userforce = 0;
		checkcoin();
		checkmushroom();
		checkbox();
		checkbrick();
		checkbomb();
		aimengine();
		if (playern == maxplayers)
		{
			bombphysics();
		}
		lastupdate = gametime;
	}
private:
	int sign(int x)
	{
		if (x > 0)
			return 1;
		else if (x < 0)
			return -1;
		else
			return 0;
	}
};

class Game
{
public:
	HWND myconsole = GetConsoleWindow();
	HDC mywindow = GetDC(myconsole);
	Mario player;
	void initialize()
	{
		points = 0;
		stage.Initialize(&mywindow);
		Console::SetCursorPosition(35, 25);
		printf("Se voce consegue ver esta tela, aperte control + R para recarregar o grafico do jogo.");
		stage.print();
		gametime = (int)(((double)clock() * 1000) / CLOCKS_PER_SEC);
		player.lastupdate = gametime;
		//	player2.mario.left = 500;
		PlaySound(TEXT("C:\\Mario\\Sound\\Backtrack.wav"), NULL, SND_LOOP && SND_ASYNC);
		mainloop();
	}
	void mainloop()
	{
		ConsoleKey comando;
		for (; player.alive == true;)
		{
			while (Console::KeyAvailable)
				comando = Console::ReadKey(true).Key;
			if (comando == ConsoleKey::P){
				PlaySound(TEXT("C:\\Mario\\Sound\\Pause.wav"), NULL, SND_ASYNC);
				comando = Console::ReadKey(true).Key;
				while (comando != ConsoleKey::P){
				while (Console::KeyAvailable)
					comando = Console::ReadKey(true).Key;
				}
				PlaySound(TEXT("C:\\Mario\\Sound\\Pause.wav"), NULL, SND_FILENAME);
				PlaySound(TEXT("C:\\Mario\\Sound\\Backtrack.wav"), NULL, SND_LOOP && SND_ASYNC);
				comando = ConsoleKey::A;
				gametime = (int)(((double)clock() * 1000) / CLOCKS_PER_SEC);
				player.lastupdate = gametime;
			}
			gametime = (int)(((double)clock() * 1000) / CLOCKS_PER_SEC);
			myconsole = GetConsoleWindow();
			mywindow = GetDC(myconsole);
			player.play();
			//player2.play();
			Console::SetCursorPosition(70, 0);
			printf("%03d points", points, points);
			Thread::Sleep(50); 
		}
	}
private:
};


int main()
{
	system("color 30");
	Console::CursorVisible = 0;
	Console::SetBufferSize(148, 50);
	Console::SetWindowSize(148, 50);
	Element any;
	Game newgame;
	any.InitializeElements(&newgame.mywindow, &stage.colormap);
	stage.level = 2;
	newgame.initialize();
	return 0;
}