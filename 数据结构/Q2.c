#include <windows.h>
#include <commctrl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define INF 999999
#define MAX_NODES 60
#define MAX_EDGES 300
#define MAX_WP 10

typedef struct { double x, y; } Point;
typedef struct { int from, to, weight; } Edge;

int N = 55;
int adj[MAX_NODES][MAX_NODES];
Point pos[MAX_NODES];
Edge edges[MAX_EDGES];
int edgeCount = 0;
int parent[MAX_NODES];

int find(int x) {
    while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
    return x;
}
void unite(int a, int b) { int ra = find(a), rb = find(b); if (ra != rb) parent[rb] = ra; }

void generateRoadNetwork() {
    int i, j, cols = 10, rows = (N + cols - 1) / cols;
    srand((unsigned)time(NULL));
    for (i = 0; i < N; i++) {
        int r = i / cols, c = i % cols;
        pos[i].x = 60 + c * 72 + (rand() % 30 - 15);
        pos[i].y = 40 + r * 72 + (rand() % 30 - 15);
    }
    for (i = 0; i < N; i++)
        for (j = 0; j < N; j++)
            adj[i][j] = (i == j) ? 0 : INF;
    for (i = 0; i < N; i++) parent[i] = i;

    int attempts = 0;
    while (attempts < N * 8) {
        i = rand() % N; j = rand() % N;
        if (i != j && adj[i][j] == INF) {
            double dx = pos[i].x - pos[j].x, dy = pos[i].y - pos[j].y;
            double dist = sqrt(dx * dx + dy * dy);
            if (dist < 120.0 || (attempts < N * 3)) {
                int w = (int)(dist / 8) + (rand() % 20) + 1;
                adj[i][j] = adj[j][i] = w;
                edges[edgeCount].from = i; edges[edgeCount].to = j;
                edges[edgeCount].weight = w; edgeCount++;
                unite(i, j);
            }
        }
        attempts++;
    }
    for (i = 1; i < N; i++) {
        if (find(i) != find(0)) {
            int w = (int)(sqrt((pos[i].x-pos[0].x)*(pos[i].x-pos[0].x) +
                               (pos[i].y-pos[0].y)*(pos[i].y-pos[0].y)) / 8) + 1;
            adj[i][0] = adj[0][i] = w;
            edges[edgeCount].from = i; edges[edgeCount].to = 0;
            edges[edgeCount].weight = w; edgeCount++;
            unite(i, 0);
        }
    }
}

int dist[MAX_NODES], prev[MAX_NODES], visited[MAX_NODES];
void dijkstra(int start, int end, int *outPath, int *outLen) {
    int i, j;
    for (i = 0; i < N; i++) { dist[i] = INF; visited[i] = 0; prev[i] = -1; }
    dist[start] = 0;
    for (i = 0; i < N; i++) {
        int u = -1, minD = INF;
        for (j = 0; j < N; j++)
            if (!visited[j] && dist[j] < minD) { minD = dist[j]; u = j; }
        if (u == -1 || u == end) break;
        visited[u] = 1;
        for (j = 0; j < N; j++)
            if (!visited[j] && adj[u][j] < INF && dist[u] + adj[u][j] < dist[j]) {
                dist[j] = dist[u] + adj[u][j]; prev[j] = u;
            }
    }
    if (dist[end] == INF) { *outLen = 0; return; }
    int path[MAX_NODES], idx = 0, cur = end;
    while (cur != -1) { path[idx++] = cur; cur = prev[cur]; }
    for (i = 0; i < idx; i++) outPath[i] = path[idx - 1 - i];
    *outLen = idx;
}

int resultPath[MAX_NODES * 4];
int resultLen = 0;
int resultWeight = 0;
int startNode = 0, endNode = 10;
int waypoints[MAX_WP], wpCount = 0;

HWND hGraphWnd, hStartCombo, hEndCombo, hWpCombo, hWpList, hResultText, hCalcBtn;

void fillCombo(HWND combo) {
    SendMessage(combo, CB_RESETCONTENT, 0, 0);
    int i; char buf[16];
    for (i = 0; i < N; i++) {
        wsprintf(buf, "节点 %d", i);
        SendMessage(combo, CB_ADDSTRING, 0, (LPARAM)buf);
    }
    SendMessage(combo, CB_SETCURSEL, 0, 0);
}

void computeFullPath() {
    resultLen = 0; resultWeight = 0;
    int current = startNode, i;
    int allTargets[MAX_WP + 2];
    allTargets[0] = startNode;
    for (i = 0; i < wpCount; i++) allTargets[i + 1] = waypoints[i];
    allTargets[wpCount + 1] = endNode;
    for (i = 0; i < wpCount + 1; i++) {
        int segPath[MAX_NODES], segLen;
        dijkstra(allTargets[i], allTargets[i + 1], segPath, &segLen);
        if (segLen == 0) { resultLen = 0; resultWeight = 0; return; }
        int startIdx = (i == 0) ? 0 : 1;
        int j;
        for (j = startIdx; j < segLen; j++) {
            resultPath[resultLen++] = segPath[j];
            if (j > 0) resultWeight += adj[segPath[j - 1]][segPath[j]];
        }
    }
    InvalidateRect(hGraphWnd, NULL, TRUE);
    {
        char buf[512], tmp[128];
        if (resultLen == 0) {
            wsprintf(buf, "无法到达目标节点");
        } else {
            wsprintf(buf, "最短路径 (总权重=%d):\r\n", resultWeight);
            for (i = 0; i < resultLen; i++) {
                wsprintf(tmp, "%d", resultPath[i]);
                strcat(buf, tmp);
                if (i < resultLen - 1) strcat(buf, " → ");
            }
        }
        SetWindowText(hResultText, buf);
    }
}

void drawGraph(HDC hdc, RECT *rc) {
    int i, j;
    HDC memDC = CreateCompatibleDC(hdc);
    HBITMAP memBmp = CreateCompatibleBitmap(hdc, rc->right, rc->bottom);
    HBITMAP oldBmp = (HBITMAP)SelectObject(memDC, memBmp);

    HBRUSH bgBrush = CreateSolidBrush(RGB(250, 250, 245));
    FillRect(memDC, rc, bgBrush);
    DeleteObject(bgBrush);

    HPEN edgePen = CreatePen(PS_SOLID, 1, RGB(180, 180, 180));
    HPEN pathPen = CreatePen(PS_SOLID, 3, RGB(220, 30, 30));
    HPEN oldPen = (HPEN)SelectObject(memDC, edgePen);

    int onPath[MAX_NODES] = {0};
    for (i = 0; i < resultLen; i++) onPath[resultPath[i]] = 1;

    for (i = 0; i < edgeCount; i++) {
        int a = edges[i].from, b = edges[i].to;
        int onP = 0, k;
        for (k = 0; k < resultLen - 1; k++)
            if ((resultPath[k] == a && resultPath[k + 1] == b) ||
                (resultPath[k] == b && resultPath[k + 1] == a)) { onP = 1; break; }
        if (onP) SelectObject(memDC, pathPen);
        else SelectObject(memDC, edgePen);
        MoveToEx(memDC, (int)pos[a].x, (int)pos[a].y, NULL);
        LineTo(memDC, (int)pos[b].x, (int)pos[b].y);
        int mx = (int)((pos[a].x + pos[b].x) / 2);
        int my = (int)((pos[a].y + pos[b].y) / 2);
        char wbuf[8]; wsprintf(wbuf, "%d", edges[i].weight);
        SetBkMode(memDC, TRANSPARENT);
        SetTextColor(memDC, RGB(100, 100, 100));
        TextOut(memDC, mx, my, wbuf, strlen(wbuf));
    }
    DeleteObject(edgePen); DeleteObject(pathPen);

    for (i = 0; i < N; i++) {
        HBRUSH brush;
        int isResult = onPath[i], isStart = (i == startNode),
            isEnd = (i == endNode), isWp = 0;
        for (j = 0; j < wpCount; j++) if (waypoints[j] == i) { isWp = 1; break; }
        if (isStart) brush = CreateSolidBrush(RGB(0, 160, 0));
        else if (isEnd) brush = CreateSolidBrush(RGB(0, 80, 200));
        else if (isWp) brush = CreateSolidBrush(RGB(200, 120, 0));
        else if (isResult) brush = CreateSolidBrush(RGB(240, 60, 60));
        else brush = CreateSolidBrush(RGB(120, 120, 120));

        HBRUSH oldBr = (HBRUSH)SelectObject(memDC, brush);
        int r = (isStart || isEnd || isWp) ? 8 : 5;
        Ellipse(memDC, (int)pos[i].x - r, (int)pos[i].y - r,
                (int)pos[i].x + r, (int)pos[i].y + r);
        SelectObject(memDC, oldBr);
        DeleteObject(brush);

        char lbl[8]; wsprintf(lbl, "%d", i);
        SetBkMode(memDC, TRANSPARENT);
        SetTextColor(memDC, RGB(40, 40, 40));
        TextOut(memDC, (int)pos[i].x - 8, (int)pos[i].y + 8, lbl, strlen(lbl));
    }

    BitBlt(hdc, 0, 0, rc->right, rc->bottom, memDC, 0, 0, SRCCOPY);
    SelectObject(memDC, oldBmp);
    DeleteObject(memBmp);
    DeleteDC(memDC);
}

LRESULT CALLBACK graphWndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        RECT rc; GetClientRect(hWnd, &rc);
        drawGraph(hdc, &rc);
        EndPaint(hWnd, &ps);
        return 0;
    }
    }
    return DefWindowProc(hWnd, msg, wParam, lParam);
}

LRESULT CALLBACK mainWndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_CREATE: {
        HINSTANCE hInst = ((LPCREATESTRUCT)lParam)->hInstance;
        RECT rc; GetClientRect(hWnd, &rc);

        hGraphWnd = CreateWindow("GraphWnd", NULL,
            WS_CHILD | WS_VISIBLE | WS_BORDER,
            0, 0, rc.right, rc.bottom - 160, hWnd, (HMENU)301, hInst, NULL);

        int panelY = rc.bottom - 155;
        CreateWindow("STATIC", "起点:", WS_CHILD | WS_VISIBLE,
            10, panelY, 40, 22, hWnd, (HMENU)302, hInst, NULL);
        hStartCombo = CreateWindow("COMBOBOX", NULL,
            WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST | WS_VSCROLL,
            50, panelY, 90, 200, hWnd, (HMENU)201, hInst, NULL);

        CreateWindow("STATIC", "终点:", WS_CHILD | WS_VISIBLE,
            155, panelY, 40, 22, hWnd, (HMENU)303, hInst, NULL);
        hEndCombo = CreateWindow("COMBOBOX", NULL,
            WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST | WS_VSCROLL,
            195, panelY, 90, 200, hWnd, (HMENU)202, hInst, NULL);

        CreateWindow("STATIC", "途径点:", WS_CHILD | WS_VISIBLE,
            300, panelY, 50, 22, hWnd, (HMENU)304, hInst, NULL);
        hWpCombo = CreateWindow("COMBOBOX", NULL,
            WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST | WS_VSCROLL,
            350, panelY, 90, 200, hWnd, (HMENU)203, hInst, NULL);

        CreateWindow("BUTTON", "添加", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            450, panelY - 2, 50, 24, hWnd, (HMENU)401, hInst, NULL);
        CreateWindow("BUTTON", "移除", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            505, panelY - 2, 50, 24, hWnd, (HMENU)402, hInst, NULL);

        int listY = panelY + 28;
        hWpList = CreateWindow("LISTBOX", NULL,
            WS_CHILD | WS_VISIBLE | WS_BORDER | WS_VSCROLL | LBS_NOTIFY,
            350, listY, 205, 50, hWnd, (HMENU)204, hInst, NULL);

        hCalcBtn = CreateWindow("BUTTON", "计算最短路径",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            10, listY, 160, 50, hWnd, (HMENU)403, hInst, NULL);

        hResultText = CreateWindow("EDIT", "",
            WS_CHILD | WS_VISIBLE | WS_BORDER | ES_MULTILINE | ES_READONLY | WS_VSCROLL,
            10, listY + 55, 540, 55, hWnd, (HMENU)305, hInst, NULL);

        fillCombo(hStartCombo); fillCombo(hEndCombo); fillCombo(hWpCombo);
        SendMessage(hStartCombo, CB_SETCURSEL, startNode, 0);
        SendMessage(hEndCombo, CB_SETCURSEL, endNode, 0);

        HFONT hFont = CreateFont(11, 0, 0, 0, FW_BOLD, 0, 0, 0,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            DEFAULT_QUALITY, DEFAULT_PITCH, "微软雅黑");
        SendMessage(hCalcBtn, WM_SETFONT, (WPARAM)hFont, TRUE);
        break;
    }
    case WM_SIZE: {
        RECT rc; GetClientRect(hWnd, &rc);
        SetWindowPos(hGraphWnd, NULL, 0, 0, rc.right, rc.bottom - 160, SWP_NOZORDER);
        InvalidateRect(hGraphWnd, NULL, TRUE);
        break;
    }
    case WM_COMMAND:
        if (LOWORD(wParam) == 401 && wpCount < MAX_WP) {
            int sel = SendMessage(hWpCombo, CB_GETCURSEL, 0, 0);
            if (sel >= 0) {
                waypoints[wpCount++] = sel;
                char buf[32]; wsprintf(buf, "途径点%d: 节点 %d", wpCount, sel);
                SendMessage(hWpList, LB_ADDSTRING, 0, (LPARAM)buf);
            }
        } else if (LOWORD(wParam) == 402) {
            int sel = SendMessage(hWpList, LB_GETCURSEL, 0, 0);
            if (sel >= 0) {
                int i;
                for (i = sel; i < wpCount - 1; i++) waypoints[i] = waypoints[i + 1];
                wpCount--;
                SendMessage(hWpList, LB_RESETCONTENT, 0, 0);
                for (i = 0; i < wpCount; i++) {
                    char buf[32];
                    wsprintf(buf, "途径点%d: 节点 %d", i + 1, waypoints[i]);
                    SendMessage(hWpList, LB_ADDSTRING, 0, (LPARAM)buf);
                }
            }
        } else if (LOWORD(wParam) == 403) {
            startNode = SendMessage(hStartCombo, CB_GETCURSEL, 0, 0);
            endNode = SendMessage(hEndCombo, CB_GETCURSEL, 0, 0);
            if (startNode == endNode) {
                SetWindowText(hResultText, "起点和终点不能相同！");
                resultLen = 0;
            } else {
                computeFullPath();
            }
            InvalidateRect(hGraphWnd, NULL, TRUE);
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    }
    return DefWindowProc(hWnd, msg, wParam, lParam);
}

int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR cmdLine, int nShow) {
    INITCOMMONCONTROLSEX icex;
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icex);

    generateRoadNetwork();

    WNDCLASS wc = {0};
    wc.lpfnWndProc = graphWndProc;
    wc.hInstance = hInst;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = "GraphWnd";
    RegisterClass(&wc);

    wc.lpfnWndProc = mainWndProc;
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    wc.lpszClassName = "ShortestPathMain";
    RegisterClass(&wc);

    HWND hWnd = CreateWindow("ShortestPathMain", "路网最短路径计算系统",
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 800, 700,
        NULL, NULL, hInst, NULL);
    ShowWindow(hWnd, nShow);
    UpdateWindow(hWnd);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return msg.wParam;
}
