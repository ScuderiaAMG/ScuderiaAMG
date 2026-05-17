#include <windows.h>
#include <commctrl.h>
#include <stdio.h>
#include <string.h>

#define MAX_MENU 20
#define MAX_ROLE 5
#define MAX_USER 10

typedef struct { int id, parentId; char name[64], action[128]; } MenuItem;
typedef struct { int id; char name[32]; } Role;
typedef struct { int id; char name[32], password[32]; int roleId; } User;
typedef struct { int menuId, roleId, visible, enabled; } Permission;

MenuItem menus[] = {
    {1,0,"系统管理",""},{2,1,"用户管理","管理所有用户账号信息"},
    {3,1,"角色管理","管理系统角色与权限分配"},{4,1,"系统日志","查看系统操作日志"},
    {5,0,"数据管理",""},{6,5,"数据导入","从外部文件导入数据"},
    {7,5,"数据导出","将数据导出到文件"},{8,5,"数据备份","备份数据库到安全位置"},
    {9,0,"报表中心",""},{10,9,"日报表","生成每日运营报表"},
    {11,9,"月报表","生成每月汇总报表"},{12,0,"个人设置",""},
    {13,12,"修改密码","修改当前用户登录密码"},{14,12,"个人信息","查看和编辑个人资料"},
};
Role roles[] = {{0,"系统管理员"},{1,"操作员"},{2,"普通用户"}};
User users[] = {
    {0,"admin","admin123",0},{1,"operator","oper123",1},{2,"user","user123",2},
};
Permission permissions[] = {
    {1,0,1,0},{2,0,1,1},{3,0,1,1},{4,0,1,1},{5,0,1,0},{6,0,1,1},{7,0,1,1},{8,0,1,1},
    {9,0,1,0},{10,0,1,1},{11,0,1,1},{12,0,1,0},{13,0,1,1},{14,0,1,1},
    {1,1,1,0},{2,1,0,0},{3,1,0,0},{4,1,0,0},{5,1,1,0},{6,1,1,1},{7,1,1,1},{8,1,1,1},
    {9,1,1,0},{10,1,1,1},{11,1,1,1},{12,1,1,0},{13,1,1,1},{14,1,1,1},
    {1,2,1,0},{2,2,0,0},{3,2,0,0},{4,2,0,0},{5,2,1,0},{6,2,0,0},{7,2,0,0},{8,2,0,0},
    {9,2,1,0},{10,2,1,1},{11,2,1,1},{12,2,1,0},{13,2,1,1},{14,2,1,1},
};
int menuCount = sizeof(menus)/sizeof(menus[0]);
int roleCount = sizeof(roles)/sizeof(roles[0]);
int userCount = sizeof(users)/sizeof(users[0]);
int permCount = sizeof(permissions)/sizeof(permissions[0]);

int currentUserId = -1;
int loggingOut = 0;
HWND hTreeView, hStatus, hMainWnd, hLoginWnd, hLogoutBtn;
HWND hUserCombo, hPwdEdit, hLoginBtn, hLoginMsg;
HFONT hLoginFont = NULL;
HINSTANCE g_hInst;

int hasPermission(int userId, int menuId) {
    User *u = NULL; int i;
    for(i=0;i<userCount;i++) if(users[i].id==userId){u=&users[i];break;}
    if(!u) return 0;
    for(i=0;i<permCount;i++)
        if(permissions[i].roleId==u->roleId && permissions[i].menuId==menuId)
            return permissions[i].enabled;
    return 0;
}
int isVisible(int userId, int menuId) {
    User *u = NULL; int i;
    for(i=0;i<userCount;i++) if(users[i].id==userId){u=&users[i];break;}
    if(!u) return 0;
    for(i=0;i<permCount;i++)
        if(permissions[i].roleId==u->roleId && permissions[i].menuId==menuId)
            return permissions[i].visible;
    return 0;
}
HTREEITEM insertTreeItem(HWND hTree, HTREEITEM parent, MenuItem *menu) {
    TVINSERTSTRUCT tvis;
    tvis.hParent = parent; tvis.hInsertAfter = TVI_LAST;
    tvis.item.mask = TVIF_TEXT | TVIF_PARAM;
    tvis.item.pszText = menu->name; tvis.item.lParam = menu->id;
    return (HTREEITEM)SendMessage(hTree, TVM_INSERTITEM, 0, (LPARAM)&tvis);
}
void buildMenuTree(HWND hTree, int userId, HTREEITEM parent, int parentId) {
    int i;
    for(i=0;i<menuCount;i++)
        if(menus[i].parentId==parentId && isVisible(userId,menus[i].id)){
            HTREEITEM node = insertTreeItem(hTree, parent, &menus[i]);
            buildMenuTree(hTree, userId, node, menus[i].id);
        }
}
void showMenuAction(HWND hParent, MenuItem *menu, int authorized) {
    if(authorized){
        char title[128],msg[512];
        wsprintf(title,"%s - 操作窗口",menu->name);
        wsprintf(msg,"正在执行菜单操作\r\n\r\n菜单项: %s\r\n功能描述: %s\r\n\r\n操作成功完成！",
            menu->name,menu->action);
        MessageBox(hParent,msg,title,MB_OK|MB_ICONINFORMATION);
    }else{
        char msg[256];
        wsprintf(msg,"您没有「%s」的操作权限！\r\n\r\n当前角色无权执行此操作，请联系系统管理员。",menu->name);
        MessageBox(hParent,msg,"权限不足",MB_OK|MB_ICONWARNING);
    }
}

LRESULT CALLBACK loginWndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch(msg){
    case WM_CREATE:{
        HINSTANCE hInst = ((LPCREATESTRUCT)lParam)->hInstance;
        CreateWindow("STATIC","用户菜单权限管理系统",WS_CHILD|WS_VISIBLE|SS_CENTER,
            50,20,300,30,hWnd,(HMENU)301,hInst,NULL);
        CreateWindow("STATIC","用户名:",WS_CHILD|WS_VISIBLE,
            70,65,60,25,hWnd,(HMENU)302,hInst,NULL);
        hUserCombo = CreateWindow("COMBOBOX",NULL,
            WS_CHILD|WS_VISIBLE|CBS_DROPDOWNLIST|WS_VSCROLL,
            135,62,165,100,hWnd,(HMENU)201,hInst,NULL);
        int i; for(i=0;i<userCount;i++)
            SendMessage(hUserCombo,CB_ADDSTRING,0,(LPARAM)users[i].name);
        SendMessage(hUserCombo,CB_SETCURSEL,0,0);
        CreateWindow("STATIC","密  码:",WS_CHILD|WS_VISIBLE,
            70,100,60,25,hWnd,(HMENU)303,hInst,NULL);
        hPwdEdit = CreateWindow("EDIT",NULL,
            WS_CHILD|WS_VISIBLE|WS_BORDER|ES_PASSWORD,
            135,97,165,25,hWnd,(HMENU)202,hInst,NULL);
        hLoginMsg = CreateWindow("STATIC","",
            WS_CHILD|WS_VISIBLE|SS_CENTER,
            70,135,230,20,hWnd,(HMENU)304,hInst,NULL);
        hLoginBtn = CreateWindow("BUTTON","登 录",
            WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON,
            120,165,150,35,hWnd,(HMENU)203,hInst,NULL);
        hLoginFont = CreateFont(16,0,0,0,FW_BOLD,0,0,0,
            DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,
            DEFAULT_QUALITY,DEFAULT_PITCH,"微软雅黑");
        SendMessage(GetDlgItem(hWnd,301),WM_SETFONT,(WPARAM)hLoginFont,TRUE);
        return 0;
    }
    case WM_COMMAND:
        if(LOWORD(wParam)==203){
            char userName[64],password[64];
            GetWindowText(hUserCombo,userName,sizeof(userName));
            GetWindowText(hPwdEdit,password,sizeof(password));
            int i,found=0;
            for(i=0;i<userCount;i++)
                if(strcmp(users[i].name,userName)==0 && strcmp(users[i].password,password)==0){
                    currentUserId=users[i].id; found=1; break;
                }
            if(found){
                DestroyWindow(hWnd);
                hMainWnd = CreateWindow("MenuMainWnd","用户菜单权限管理系统",
                    WS_OVERLAPPEDWINDOW, CW_USEDEFAULT,CW_USEDEFAULT,700,500,
                    NULL,NULL,g_hInst,NULL);
                ShowWindow(hMainWnd,SW_SHOW); UpdateWindow(hMainWnd);
            }else{
                SetWindowText(hLoginMsg,"用户名或密码错误！");
                SetWindowText(hPwdEdit,"");
                SetFocus(hPwdEdit);
            }
        }
        break;
    case WM_DESTROY:
        if(hLoginFont) DeleteObject(hLoginFont);
        if(currentUserId==-1) PostQuitMessage(0);
        break;
    }
    return DefWindowProc(hWnd,msg,wParam,lParam);
}

LRESULT CALLBACK mainWndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch(msg){
    case WM_CREATE:{
        RECT rc; GetClientRect(hWnd,&rc);
        hTreeView = CreateWindow(WC_TREEVIEW,NULL,
            WS_CHILD|WS_VISIBLE|TVS_HASLINES|TVS_HASBUTTONS|TVS_LINESATROOT|WS_BORDER,
            10,10,rc.right-20,rc.bottom-50,hWnd,(HMENU)101,GetModuleHandle(NULL),NULL);
        buildMenuTree(hTreeView,currentUserId,NULL,0);
        HTREEITEM root = TreeView_GetRoot(hTreeView);
        if(root) SendMessage(hTreeView,TVM_EXPAND,TVE_EXPAND,(LPARAM)root);
        hStatus = CreateWindow(STATUSCLASSNAME,"",
            WS_CHILD|WS_VISIBLE|SBARS_SIZEGRIP,0,0,0,0,hWnd,(HMENU)102,GetModuleHandle(NULL),NULL);
        User *u = NULL; Role *r = NULL; int i;
        for(i=0;i<userCount;i++) if(users[i].id==currentUserId){u=&users[i];break;}
        for(i=0;i<roleCount;i++) if(u && roles[i].id==u->roleId){r=&roles[i];break;}
        char st[256]; wsprintf(st,"当前用户: %s | 角色: %s",u?u->name:"?",r?r->name:"?");
        SendMessage(hStatus,SB_SETTEXT,0,(LPARAM)st);
        hLogoutBtn = CreateWindow("BUTTON","注 销",
            WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON,
            rc.right-110,rc.bottom-48,100,26,hWnd,(HMENU)205,GetModuleHandle(NULL),NULL);
        break;
    }
    case WM_SIZE:{
        RECT rc; GetClientRect(hWnd,&rc);
        SetWindowPos(hTreeView,NULL,10,10,rc.right-20,rc.bottom-50,SWP_NOZORDER);
        SetWindowPos(hLogoutBtn,NULL,rc.right-110,rc.bottom-48,100,26,SWP_NOZORDER);
        SendMessage(hStatus,WM_SIZE,0,0);
        break;
    }
    case WM_NOTIFY:{
        LPNMHDR nmhdr = (LPNMHDR)lParam;
        if(nmhdr->idFrom==101 && nmhdr->code==NM_DBLCLK){
            HTREEITEM hSel = TreeView_GetSelection(hTreeView);
            if(hSel){
                TVITEM item; char buf[64];
                item.hItem=hSel; item.mask=TVIF_PARAM|TVIF_TEXT;
                item.pszText=buf; item.cchTextMax=64;
                SendMessage(hTreeView,TVM_GETITEM,0,(LPARAM)&item);
                int menuId=item.lParam; MenuItem *menu=NULL; int i;
                for(i=0;i<menuCount;i++) if(menus[i].id==menuId){menu=&menus[i];break;}
                if(menu && menu->parentId!=0)
                    showMenuAction(hWnd,menu,hasPermission(currentUserId,menuId));
            }
        }
        break;
    }
    case WM_COMMAND:
        if(LOWORD(wParam)==205){
            loggingOut=1;
            DestroyWindow(hWnd);
        }
        break;
    case WM_DESTROY:
        if(loggingOut){
            loggingOut=0;
            currentUserId=-1;
            hLoginWnd=CreateWindow("LoginWnd","用户登录",
                WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU,
                (GetSystemMetrics(SM_CXSCREEN)-400)/2,
                (GetSystemMetrics(SM_CYSCREEN)-270)/2,400,270,
                NULL,NULL,g_hInst,NULL);
            ShowWindow(hLoginWnd,SW_SHOW);
            UpdateWindow(hLoginWnd);
        }else{
            PostQuitMessage(0);
        }
        break;
    }
    return DefWindowProc(hWnd,msg,wParam,lParam);
}

int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR cmdLine, int nShow) {
    g_hInst = hInst;
    INITCOMMONCONTROLSEX icex;
    icex.dwSize=sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC=ICC_TREEVIEW_CLASSES|ICC_BAR_CLASSES;
    InitCommonControlsEx(&icex);

    WNDCLASS wc={0};
    wc.lpfnWndProc=mainWndProc; wc.hInstance=hInst;
    wc.hCursor=LoadCursor(NULL,IDC_ARROW);
    wc.hbrBackground=(HBRUSH)(COLOR_BTNFACE+1);
    wc.lpszClassName="MenuMainWnd"; RegisterClass(&wc);

    wc.lpfnWndProc=loginWndProc;
    wc.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);
    wc.lpszClassName="LoginWnd"; RegisterClass(&wc);

    hLoginWnd = CreateWindow("LoginWnd","用户登录",
        WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU,
        (GetSystemMetrics(SM_CXSCREEN)-400)/2,
        (GetSystemMetrics(SM_CYSCREEN)-270)/2,400,270,
        NULL,NULL,hInst,NULL);
    ShowWindow(hLoginWnd,nShow); UpdateWindow(hLoginWnd);

    MSG msg;
    while(GetMessage(&msg,NULL,0,0)){
        TranslateMessage(&msg); DispatchMessage(&msg);
    }
    return msg.wParam;
}
