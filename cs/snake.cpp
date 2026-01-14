// clang++ snake.cpp $(sdl2-config --cflags --libs)
#include <SDL.h>
#include <deque>
#include <iostream>
#include <random>
#include <string>
#include <utility>

#define BLOCK_SIZE 10
#define X_BLOCKS 32
#define Y_BLOCKS 32
#define TOTAL_BLOCKS 32 * 32
#define Pos std::pair<int, int>
#define Snake std::deque<int>
enum Move { UP, DOWN, LEFT, RIGHT };
enum OB { SNAKE, APPLE };

std::minstd_rand rng(42);

int mod(int a, int n) { return (a % n + n) % n; }
int rand() { return mod(rng(), TOTAL_BLOCKS); }

void movePtr2D(int *ptr, Move m) {
    int x = (*ptr) % X_BLOCKS;
    int y = (*ptr) / X_BLOCKS;

    switch (m) {
    case LEFT:
        x--;
        break;
    case RIGHT:
        x++;
        break;
    case UP:
        y--;
        break;
    case DOWN:
        y++;
        break;
    default:
        break;
    }
    x = mod(x, X_BLOCKS);
    y = mod(y, Y_BLOCKS);
    *ptr = y * X_BLOCKS + x;
}

Pos getWindowPos(int ptr) {
    int x = ptr % X_BLOCKS;
    int y = ptr / X_BLOCKS;
    Pos pos = std::make_pair(x * BLOCK_SIZE, y * BLOCK_SIZE);
    return pos;
}

void whereAmI(Pos pos) {
    std::cout << "I'm in " << pos.first << ", " << pos.second << std::endl;
    return;
}

Snake makeSnake() {
    Snake snake;
    snake.push_front(rand());
    return snake;
}

void moveSnake(Snake &snake, Move m) {
    int head = snake.front();
    movePtr2D(&head, m);
    snake.push_front(head);
    snake.pop_back();
}

bool isCollide(Snake &snake) {
    int head = snake.front();
    for (size_t i = 1; i < snake.size(); ++i) {
        if ((head ^ snake[i]) == 0)
            return true;
    }
    return false;
}

void eatApple(Snake &snake, int prev_back) { snake.push_back(prev_back); }

int randomApplePtr(Snake &snake) {
    int applePtr = 0;
    bool end = false;
    while (!end) {
        end = true;
        applePtr = rand();
        for (const int snake_part : snake) {
            end = end && (snake_part != applePtr);
        }
    }
    return applePtr;
}

void clearWindow(SDL_Renderer *renderer) {
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer); // clear the window
    return;
}

void renderRect(SDL_Renderer *renderer, int ptr, OB type) {
    Pos pos = getWindowPos(ptr);
    int x = pos.first;
    int y = pos.second;
    SDL_Rect rect = {x, y, BLOCK_SIZE, BLOCK_SIZE};
    switch (type) {
    case SNAKE:
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
        break;
    case APPLE:
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
        break;
    default:
        break;
    }
    SDL_RenderFillRect(renderer, &rect);
    return;
}

void renderSnake(SDL_Renderer *renderer, Snake &snake) {
    for (const int snake_part : snake) {
        renderRect(renderer, snake_part, SNAKE);
    }
}

int main(void) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cout << SDL_GetError() << "\n";
        return 1;
    }
    int WIDTH = X_BLOCKS * BLOCK_SIZE;
    int HEIGHT = Y_BLOCKS * BLOCK_SIZE;
    SDL_Window *window = SDL_CreateWindow("Hello SDL", SDL_WINDOWPOS_CENTERED,
                                          SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT,
                                          SDL_WINDOW_SHOWN);

    SDL_Renderer *renderer =
        SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    // char board[64][64] = {};
    // board[0][0]++;
    // std::cout << *(int *)&board[0][0] << std::endl;
    Snake snake = makeSnake();
    int applePtr = randomApplePtr(snake);

    bool running = true;
    bool reset = false;
    Move move = RIGHT;

    Uint32 before = 0;
    Uint32 current = 0;
    while (running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            switch (event.type) {
            case SDL_QUIT:
                running = false;
                break;
            case SDL_KEYDOWN:
                switch (event.key.keysym.sym) {
                case SDLK_w:
                    move = UP;
                    break;
                case SDLK_s:
                    move = DOWN;
                    break;
                case SDLK_a:
                    move = LEFT;
                    break;
                case SDLK_d:
                    move = RIGHT;
                    break;
                }
            default:
                break;
            }
        }

        if (reset) {
            snake = makeSnake();
            applePtr = randomApplePtr(snake);
            reset = false;
            continue;
        }

        current = SDL_GetTicks();
        Uint32 delta = current - before;
        if (delta < 250) {
            continue;
        }
        before = current;
        clearWindow(renderer);

        int prev_back = snake.back();
        moveSnake(snake, move);
        if (snake.front() == applePtr) {
            eatApple(snake, prev_back);
            applePtr = randomApplePtr(snake);
        }
        if (isCollide(snake)) {
            reset = true;
            continue;
        }

        renderSnake(renderer, snake);
        renderRect(renderer, applePtr, APPLE);
        SDL_RenderPresent(renderer);
    }

    SDL_Quit();
    return 0;
}
