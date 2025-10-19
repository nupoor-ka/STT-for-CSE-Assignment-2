#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(void) {
    /* Config */
    const int MAXR = 40, MAXC = 40;
    int rows = 24, cols = 24;               /* default maze size */
    char maze[MAXR][MAXC];
    int visited[MAXR][MAXC];
    int parentR[MAXR][MAXC], parentC[MAXR][MAXC];

    int i, j, k;
    int startR = 1, startC = 1;
    int endR = 22, endC = 22;
    int choice, sub;
    int trace = 0;
    int seedChoice;

    srand((unsigned)time(NULL));

    /* initialize */
    for (i = 0; i < rows; i++) {
        for (j = 0; j < cols; j++) {
            if (i == 0 || j == 0 || i == rows - 1 || j == cols - 1) {
                maze[i][j] = '#';
            } else {
                maze[i][j] = ((rand() % 100) < 30) ? '#' : '.';
            }
            visited[i][j] = 0;
            parentR[i][j] = -1;
            parentC[i][j] = -1;
        }
    }
    maze[startR][startC] = 'S';
    maze[endR][endC] = 'E';

    /* main loop */
    while (1) {
        printf("\nMaze %d x %d  S=(%d,%d) E=(%d,%d)  trace=%s\n", rows, cols, startR, startC, endR, endC, trace ? "ON":"OFF");
        printf("1 Print  2 Trace toggle  3 Regenerate  4 Edit  5 DFS  6 BFS  7 A*  8 Stats  9 Resize  0 Exit\n");
        printf("Choose: ");
        if (scanf("%d", &choice) != 1) {
            int ch;
            while ((ch=getchar())!=EOF && ch!='\n') {
                ;
            }
            printf("Bad input\n");
            continue;
        }

        if (choice == 0) {
            printf("Exit\n");
            break;
        }

        if (choice == 1) {
            printf("   ");
            for (j = 0; j < cols; j++) {
                printf("%c", '0' + (j % 10));
            }
            printf("\n");
            for (i = 0; i < rows; i++) {
                printf("%2d ", i);
                for (j = 0; j < cols; j++) {
                    printf("%c", maze[i][j]);
                }
                printf("\n");
            }
            continue;
        }

        if (choice == 2) {
            trace = !trace;
            printf("Trace %s\n", trace ? "ON":"OFF");
            continue;
        }

        if (choice == 3) {
            printf("Seed: 1=random 2=enter int: ");
            if (scanf("%d", &seedChoice) != 1) {
                seedChoice = 1;
            }
            if (seedChoice == 2) {
                int s;
                scanf("%d", &s);
                srand((unsigned)s);
            }
            else {
                srand((unsigned)time(NULL) ^ rand());
            }
            for (i = 0; i < rows; i++) {
                for (j = 0; j < cols; j++) {
                    if (i==0||j==0||i==rows-1||j==cols-1) {
                        maze[i][j]='#';
                    } else {
                        maze[i][j] = ((rand()%100) < 35) ? '#' : '.';
                    }
                    visited[i][j]=0;
                    parentR[i][j]=-1;
                    parentC[i][j]=-1;
                }
            }
            maze[startR][startC]='S';
            maze[endR][endC]='E';
            printf("Regenerated\n");
            continue;
        }

        if (choice == 4) {
            printf("Edit menu: 1 toggle cell  2 move S  3 move E  4 clear interior  0 back\n");
            if (scanf("%d",&sub)!=1) {
                sub = 0;
            }
            if (sub == 0) {
                continue;
            }
            if (sub == 1) {
                int r,c;
                printf("r c: ");
                if (scanf("%d %d",&r,&c)!=2) {
                    printf("Bad\n");
                    continue;
                }
                if (r<=0||c<=0||r>=rows-1||c>=cols-1) {
                    printf("Invalid\n");
                    continue;
                }
                if ((r==startR&&c==startC)||(r==endR&&c==endC)) {
                    printf("Can't toggle S/E\n");
                    continue;
                }
                maze[r][c] = (maze[r][c]=='#') ? '.' : '#';
                printf("Toggled (%d,%d) -> %c\n", r, c, maze[r][c]);
            }
            else if (sub==2) {
                int nr,nc;
                printf("new S r c: ");
                if (scanf("%d %d",&nr,&nc)!=2) {
                    printf("Bad\n");
                    continue;
                }
                if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                    printf("Invalid\n");
                    continue;
                }
                maze[startR][startC] = '.';
                startR=nr;
                startC=nc;
                maze[startR][startC]='S';
                printf("Moved S\n");
            }
            else if (sub==3) {
                int nr,nc;
                printf("new E r c: ");
                if (scanf("%d %d",&nr,&nc)!=2) {
                    printf("Bad\n");
                    continue;
                }
                if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                    printf("Invalid\n");
                    continue;
                }
                maze[endR][endC]='.';
                endR=nr;
                endC=nc;
                maze[endR][endC]='E';
                printf("Moved E\n");
            }
            else if (sub==4) {
                for (i=1;i<rows-1;i++) {
                    for (j=1;j<cols-1;j++) {
                        maze[i][j]='.';
                    }
                }
                maze[startR][startC]='S';
                maze[endR][endC]='E';
                printf("Cleared\n");
            }
            else {
                printf("Unknown\n");
            }
            continue;
        }

        if (choice == 5) {
            /* DFS iterative */
            int stackR[10000], stackC[10000], top = -1;
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    visited[i][j]=0;
                    parentR[i][j]=-1;
                    parentC[i][j]=-1;
                }
            }
            int sr=startR, sc=startC;
            visited[sr][sc]=1;
            stackR[++top]=sr;
            stackC[top]=sc;
            int found=0, nodes=0;
            while (top>=0) {
                int cr = stackR[top];
                int cc = stackC[top];
                top--;
                nodes++;
                if (trace) {
                    printf("DFS pop (%d,%d)\n", cr, cc);
                }
                if (cr==endR && cc==endC) {
                    found=1;
                    break;
                }
                int dr[4] = {1,-1,0,0};
                int dc[4] = {0,0,1,-1};
                for (k=0;k<4;k++) {
                    int nr = cr + dr[k], nc = cc + dc[k];
                    if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                        continue;
                    }
                    if (maze[nr][nc]=='#') {
                        continue;
                    }
                    if (visited[nr][nc]) {
                        continue;
                    }
                    visited[nr][nc]=1;
                    parentR[nr][nc]=cr;
                    parentC[nr][nc]=cc;
                    stackR[++top]=nr;
                    stackC[top]=nc;
                    if (trace) {
                        printf(" DFS push (%d,%d)\n", nr, nc);
                    }
                }
            }
            if (found) {
                int pr=endR, pc=endC, path=0;
                while (!(pr==startR && pc==startC) && pr!=-1 && pc!=-1) {
                    if (maze[pr][pc]=='.') {
                        maze[pr][pc]='*';
                    }
                    int tr = parentR[pr][pc], tc = parentC[pr][pc];
                    pr=tr;
                    pc=tc;
                    path++;
                }
                maze[startR][startC]='S';
                maze[endR][endC]='E';
                printf("DFS found path nodes=%d pathlen=%d\n", nodes, path);
            }
            else {
                printf("DFS no path nodes=%d\n", nodes);
            }
            continue;
        }

        if (choice == 6) {
            /* BFS */
            int qR[10000], qC[10000], head=0, tail=0;
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    visited[i][j]=0;
                    parentR[i][j]=-1;
                    parentC[i][j]=-1;
                }
            }
            qR[tail]=startR;
            qC[tail]=startC;
            tail++;
            visited[startR][startC]=1;
            int found=0, nodes=0;
            while (head<tail) {
                int cr=qR[head], cc=qC[head];
                head++;
                nodes++;
                if (trace) {
                    printf("BFS pop (%d,%d)\n", cr, cc);
                }
                if (cr==endR && cc==endC) {
                    found=1;
                    break;
                }
                int dr[4]={0,0,1,-1}, dc[4]={1,-1,0,0};
                for (k=0;k<4;k++) {
                    int nr=cr+dr[k], nc=cc+dc[k];
                    if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                        continue;
                    }
                    if (maze[nr][nc]=='#') {
                        continue;
                    }
                    if (visited[nr][nc]) {
                        continue;
                    }
                    visited[nr][nc]=1;
                    parentR[nr][nc]=cr;
                    parentC[nr][nc]=cc;
                    qR[tail]=nr;
                    qC[tail]=nc;
                    tail++;
                    if (trace) {
                        printf(" BFS push (%d,%d)\n", nr, nc);
                    }
                }
            }
            if (found) {
                int pr=endR, pc=endC, path=0;
                while (!(pr==startR && pc==startC) && pr!=-1 && pc!=-1) {
                    if (maze[pr][pc]=='.') {
                        maze[pr][pc]='+';
                    }
                    int tr=parentR[pr][pc], tc=parentC[pr][pc];
                    pr=tr;
                    pc=tc;
                    path++;
                }
                maze[startR][startC]='S';
                maze[endR][endC]='E';
                printf("BFS found path nodes=%d pathlen=%d\n", nodes, path);
            }
            else {
                printf("BFS no path nodes=%d\n", nodes);
            }
            continue;
        }

        if (choice == 7) {
            /* A* simple open list array (inefficient but explicit) */
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    visited[i][j]=0;
                    parentR[i][j]=-1;
                    parentC[i][j]=-1;
                }
            }
            int openR[10000], openC[10000], openG[10000], openF[10000];
            int openN=0;
            openR[openN]=startR;
            openC[openN]=startC;
            openG[openN]=0;
            openF[openN]=abs(startR-endR)+abs(startC-endC);
            openN++;
            int closed[MAXR][MAXC];
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    closed[i][j]=0;
                }
            }
            int found=0, nodes=0;
            while (openN>0) {
                int best=0;
                for (i=1;i<openN;i++) {
                    if (openF[i]<openF[best]) {
                        best=i;
                    }
                }
                int cr=openR[best], cc=openC[best], cg=openG[best];
                /* remove best by replacing with last */
                openN--;
                openR[best]=openR[openN];
                openC[best]=openC[openN];
                openG[best]=openG[openN];
                openF[best]=openF[openN];
                if (trace) {
                    printf("A* expand (%d,%d) g=%d\n", cr, cc, cg);
                }
                if (cr==endR && cc==endC) {
                    found=1;
                    break;
                }
                closed[cr][cc]=1;
                nodes++;
                int dr[4]={1,-1,0,0}, dc[4]={0,0,1,-1};
                for (k=0;k<4;k++) {
                    int nr=cr+dr[k], nc=cc+dc[k];
                    if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                        continue;
                    }
                    if (maze[nr][nc]=='#') {
                        continue;
                    }
                    if (closed[nr][nc]) {
                        continue;
                    }
                    int ng = cg+1;
                    int h = abs(nr-endR)+abs(nc-endC);
                    int nf = ng + h;
                    int inOpen=-1;
                    for (i=0;i<openN;i++) {
                        if (openR[i]==nr && openC[i]==nc) {
                            inOpen=i;
                            break;
                        }
                    }
                    if (inOpen>=0) {
                        if (ng < openG[inOpen]) {
                            openG[inOpen]=ng;
                            openF[inOpen]=nf;
                            parentR[nr][nc]=cr;
                            parentC[nr][nc]=cc;
                        }
                    }
                    else {
                        openR[openN]=nr;
                        openC[openN]=nc;
                        openG[openN]=ng;
                        openF[openN]=nf;
                        parentR[nr][nc]=cr;
                        parentC[nr][nc]=cc;
                        openN++;
                        if (trace) {
                            printf(" A* add (%d,%d) g=%d f=%d\n", nr, nc, ng, nf);
                        }
                    }
                }
            }
            if (found) {
                int pr=endR, pc=endC, path=0;
                while (!(pr==startR && pc==startC) && pr!=-1 && pc!=-1) {
                    if (maze[pr][pc]=='.') {
                        maze[pr][pc]='A';
                    }
                    int tr=parentR[pr][pc], tc=parentC[pr][pc];
                    pr=tr;
                    pc=tc;
                    path++;
                }
                maze[startR][startC]='S';
                maze[endR][endC]='E';
                printf("A* found path nodes=%d pathlen=%d\n", nodes, path);
            }
            else {
                printf("A* no path nodes=%d\n", nodes);
            }
            continue;
        }

        if (choice == 8) {
            int walls=0, empt=0;
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    if (maze[i][j]=='#') {
                        walls++;
                    } else {
                        empt++;
                    }
                }
            }
            printf("Cells %d walls %d empty %d density %.3f\n", rows*cols, walls, empt, (double)walls/(rows*cols));
            /* reachable count (BFS) */
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    visited[i][j]=0;
                }
            }
            int qR[10000], qC[10000], h=0, t=0;
            qR[t]=startR;
            qC[t]=startC;
            t++;
            visited[startR][startC]=1;
            int reach=0;
            while (h<t) {
                int cr=qR[h], cc=qC[h];
                h++;
                reach++;
                int dr[4]={1,-1,0,0}, dc[4]={0,0,1,-1};
                for (k=0;k<4;k++) {
                    int nr=cr+dr[k], nc=cc+dc[k];
                    if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                        continue;
                    }
                    if (maze[nr][nc]=='#') {
                        continue;
                    }
                    if (visited[nr][nc]) {
                        continue;
                    }
                    visited[nr][nc]=1;
                    qR[t]=nr;
                    qC[t]=nc;
                    t++;
                }
            }
            printf("Reachable from S: %d\n", reach);
            /* simple heuristic longest depth (DFS without revisit) */
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    visited[i][j]=0;
                }
            }
            int stkR[10000], stkC[10000], it[10000], sp=-1, maxD=0, depth=0;
            sp++;
            stkR[sp]=startR;
            stkC[sp]=startC;
            it[sp]=0;
            visited[startR][startC]=1;
            depth=1;
            while (sp>=0) {
                int cr=stkR[sp], cc=stkC[sp], itv=it[sp];
                if (itv>3) {
                    sp--;
                    depth--;
                    continue;
                }
                it[sp] = itv+1;
                int dr[4]={1,-1,0,0}, dc[4]={0,0,1,-1};
                int nr=cr+dr[itv], nc=cc+dc[itv];
                if (nr<=0||nc<=0||nr>=rows-1||nc>=cols-1) {
                    continue;
                }
                if (maze[nr][nc]=='#') {
                    continue;
                }
                if (visited[nr][nc]) {
                    continue;
                }
                visited[nr][nc]=1;
                sp++;
                stkR[sp]=nr;
                stkC[sp]=nc;
                it[sp]=0;
                depth++;
                if (depth>maxD) {
                    maxD=depth;
                }
            }
            printf("Heuristic max depth: %d\n", maxD);
            continue;
        }

        if (choice == 9) {
            int nr, nc;
            printf("New rows cols (10..%d): ", MAXR-1);
            if (scanf("%d %d",&nr,&nc)!=2) {
                printf("Bad\n");
                continue;
            }
            if (nr<10||nc<10||nr>MAXR||nc>MAXC) {
                printf("Out of range\n");
                continue;
            }
            rows=nr;
            cols=nc;
            startR=1;
            startC=1;
            endR=rows-2;
            endC=cols-2;
            for (i=0;i<rows;i++) {
                for (j=0;j<cols;j++) {
                    if (i==0||j==0||i==rows-1||j==cols-1) {
                        maze[i][j]='#';
                    } else {
                        maze[i][j] = ((rand()%100) < 35) ? '#' : '.';
                    }
                    visited[i][j]=0;
                    parentR[i][j]=-1;
                    parentC[i][j]=-1;
                }
            }
            maze[startR][startC]='S';
            maze[endR][endC]='E';
            printf("Resized to %d x %d\n", rows, cols);
            continue;
        }

        printf("Invalid option\n");
    }

    return 0;
}