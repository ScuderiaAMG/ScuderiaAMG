// // #include <stdio.h>

// // int main() {
// //     printf("Hello, VS Code!\n");
// //     return 0;
// // }

// #include <stdio.h>
// #include <stdlib.h>
// int printHUST()
// {
//     printf("%3s,%7.2s,%.4s,%-5.3s\n","HUST","HUST","HUST","HUST");
//     float x = 357.987;
//     printf("%f,%10f,%10.2f,%.2f,%-10.2f\n",x,x,x,x,x);
//     return 0;
// }


// int sum(int a, int b)
// {
//     return a + b;
// }

// //写一个c语言链表实例

// struct Node {
//     int data;
//     struct Node* next;
// };
// struct Node* createNode(int data) {
//     struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
//     newNode->data = data;
//     newNode->next = NULL;
//     return newNode;
// }
// void printList(struct Node* head) {
//     struct Node* current = head;
//     while (current != NULL) {
//         printf("%d -> ", current->data);
//         current = current->next;
//     }
//     printf("NULL\n");
// }
// int main() {
//     struct Node* head = createNode(1);
//     head->next = createNode(2);
//     head->next->next = createNode(3);
//     printList(head);
//     return 0;
// }
//用注释的形态，生成以上代码的通俗解析和语法解析
// 这段代码包含了一个简单的C语言程序，主要功能是创建一个链表并打印它的内容。以下是对代码的通俗解析和语法解析：
// 1. 包含头文件：
// #include <stdio.h>：包含标准输入输出库，用于使用printf函数。
// #include <stdlib.h>：包含标准库，用于使用malloc函数来动态分配内存。
// 2. 定义结构体：
// struct Node：定义了一个结构体Node，表示链表的节点。它包含
//一个整数数据成员data和一个指向下一个节点的指针next。
// 3. 创建节点函数：
// struct Node* createNode(int data)：这是一个函数，接受一个整数参数data，并返回一个指向Node结构体的指针。
//函数内部使用malloc动态分配内存来创建一个新的节点，并将传入的数据赋值给节点的data成员，同时将next指针初始化为NULL。
// 4. 打印链表函数：
//void printList(struct Node* head)：这是一个函数，接受一个指向Node结构体的指针head，表示链表的头节点。
//函数内部使用一个循环遍历链表，打印每个节点的数据，并在最后打印NULL表示链表的结束。
// 5. 主函数：
//int main()：这是程序的入口点。函数内部首先创建了一个链表，包含三个节点，分别存储整数1、2和3。
//然后调用printList函数来打印链表的内容。最后返回0表示程序正常结束。
// 总结：这段代码展示了如何定义一个链表结构体，创建节点并打印链表的内容。通过使用动态内存分配和指针，程序实现了链表的基本操作。

//接下来帮我用c语言实现谷歌小恐龙，使用图形化界面并画出小恐龙所需元素
// 实现谷歌小恐龙游戏需要使用图形库来创建图形化界面。以下是一个使用SDL2库实现的简单版本的谷歌小恐龙游戏的示例代码。请确保你已经安装了SDL2库，并链接到你的项目中。
#include <SDL2/SDL.h>
#include <stdio.h>
#include <stdbool.h>

const int SCREEN_WIDTH = 800;
const int SCREEN_HEIGHT = 600;
const int DINO_WIDTH = 50;
const int DINO_HEIGHT = 50;
const int GRAVITY = 1;

typedef struct {
    int x, y;
    int velocityY;
    bool isJumping;
} Dino;
void initDino(Dino* dino) {
    dino->x = 100;
    dino->y = SCREEN_HEIGHT - DINO_HEIGHT;
    dino->velocityY = 0;
    dino->isJumping = false;
}
void handleEvents(SDL_Event* e, Dino* dino) {
    if (e->type == SDL_KEYDOWN && e->key.keysym.sym == SDLK_SPACE && !dino->isJumping) {
        dino->velocityY = -15; // Jump strength
        dino->isJumping = true;
    }
}
void updateDino(Dino* dino) {
    if (dino->isJumping) {
        dino->velocityY += GRAVITY; // Apply gravity
        dino->y += dino->velocityY; // Update position
        if (dino->y >= SCREEN_HEIGHT - DINO_HEIGHT) {
            dino->y = SCREEN_HEIGHT - DINO_HEIGHT; // Reset to ground level
            dino->isJumping = false; // End jump
        }
    }
}
void renderDino(SDL_Renderer* renderer, Dino* dino) {
    SDL_Rect dinoRect = {dino->x, dino->y, DINO_WIDTH, DINO_HEIGHT};
    SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); // Red color
    SDL_RenderFillRect(renderer, &dinoRect);
}

int main(int argc, char* args[]) {
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window* window = SDL_CreateWindow("Google Dino Game", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    
    Dino dino;
    initDino(&dino);
    
    bool quit = false;
    SDL_Event e;
    
    while (!quit) {
        while (SDL_PollEvent(&e) != 0) {
            if (e.type == SDL_QUIT) {
                quit = true;
            }
            handleEvents(&e, &dino);
        }
        
        updateDino(&dino);
        
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255); // White background
        SDL_RenderClear(renderer);
        
        renderDino(renderer, &dino);
        
        SDL_RenderPresent(renderer);
    }
    
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    
    return 0;
}
// 这段代码实现了一个简单的谷歌小恐龙游戏，使用了SDL2库来创建图形化界面。以下是对代码的通俗解析和语法解析：
// 1. 包含头文件：
// #include <SDL2/SDL.h>：包含SDL2库的头文件，用于使用SDL的功能。
// #include <stdio.h>：包含标准输入输出库，用于使用printf函数。
// #include <stdbool.h>：包含布尔类型库，用于使用bool类型。
// 2. 定义常量：
// 定义了一些常量，如屏幕宽度、屏幕高度、恐龙的宽度和高度，以及重力值。
// 3. 定义结构体：
// typedef struct { ... } Dino：定义了一个结构体Dino，表示小恐龙的属性，包括位置、垂直速度和是否正在跳跃。
// 4. 初始化恐龙函数：
//void initDino(Dino* dino)：这是一个函数，接受一个指向Dino结构体的指针，并初始化恐龙的位置、速度和跳跃状态。
// 5. 处理事件函数：
//void handleEvents(SDL_Event* e, Dino* dino)：这是一个函数，接受一个指向SDL_Event结构体的指针和一个指向Dino结构体的指针。函数内部检查是否按下了空格键，如果按下且恐龙不在跳跃状态，则设置垂直速度以使恐龙跳跃，并将跳跃状态设置为true。
// 6. 更新恐龙函数：
//void updateDino(Dino* dino)：这是一个函数，接受一个指向Dino结构体的指针。函数内部检查恐龙是否在跳跃状态，如果是，则应用重力影响垂直速度，并更新恐龙的位置。如果恐龙落回地面，则重置位置并结束跳跃状态。
// 7. 渲染恐龙函数：
//void renderDino(SDL_Renderer* renderer, Dino* dino)：这是一个函数，接受一个指向SDL_Renderer结构体的指针和一个指向Dino结构体的指针。函数内部创建一个矩形表示恐龙，并使用红色填充该矩形来渲染恐龙。
// 8. 主函数：
//int main(int argc, char* args[])：这是程序的入口点。函数内部初始化SDL库，创建窗口和渲染器，初始化恐龙结构体，并进入游戏循环。在游戏循环中，处理事件、更新恐龙状态、清除屏幕、渲染恐龙并显示更新。最后清理资源并退出程序。
// 总结：这段代码展示了如何使用SDL2库创建一个简单的谷歌小恐龙游戏。通过定义结构体、处理事件、更新状态和渲染图形，程序实现了基本的游戏功能。
