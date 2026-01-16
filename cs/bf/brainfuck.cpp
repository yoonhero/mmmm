#include "renderer.h"
#include <SDL.h>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <stdlib.h>
#include <string>
#include <utility>

#define uint8 unsigned char
#define SCREEN_SIZE 256

enum Status { DONE, UPDATE, IDLE };

class BF {
  public:
    static constexpr int TAPE_SIZE = 1024;
    uint8 tape[TAPE_SIZE] = {0};
    int ptr;
    char *source_code;
    char current_char;
    unsigned int loop, i;

    BF(char *code) {
        source_code = code;
        i = 0;
    }

    Status interpret(char input) {
        if (source_code[i] == 0) {
            return DONE;
        }
        Status status = IDLE;
        switch (source_code[i]) {
        case '>':
            ptr = (++ptr) % TAPE_SIZE;
            break;
        case '<':
            ptr = (--ptr + TAPE_SIZE) % TAPE_SIZE;
            break;
        case '+':
            ++tape[ptr];
            break;
        case '-':
            --tape[ptr];
            break;
        case '.':
            // std::putchar(*ptr);
            // std::cout << std::to_string(*ptr) << std::flush;
            status = UPDATE;
            break;
        case ',':
            tape[ptr] = static_cast<uint8>(input);
            break;
        case '[':
            if (tape[ptr] == 0) {
                loop = 1;
                while (loop > 0) {
                    current_char = source_code[++i];
                    if (current_char == '[') {
                        loop++;
                    } else if (current_char == ']') {
                        loop--;
                    }
                }
            }
            break;
        case ']':
            if (tape[ptr]) {
                loop = 1;
                while (loop > 0) {
                    current_char = source_code[--i];
                    if (current_char == '[') {
                        loop--;
                    } else if (current_char == ']') {
                        loop++;
                    }
                }
            }
            break;
        }
        i++;
        return status;
    }
};

void renderScreen(Renderer &renderer, uint8 *screen) {
    for (int i = 0; i < SCREEN_SIZE; ++i) {
        Color color = {screen[i], screen[i], screen[i], 0};
        renderer.renderLattice(i, color);
    }
}

int main(int argc, char *argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cout << SDL_GetError() << "\n";
        return 1;
    }

    uint8 screen[SCREEN_SIZE];
    Renderer renderer(16, 16, 30);

    FILE *fptr = argc > 1 ? fopen(argv[1], "r") : stdin;
    char buf[1024];
    char *bufPtr = buf;
    size_t len = 0;
    int c;
    while ((c = fgetc(fptr)) != EOF) {
        bufPtr[len++] = (char)c;
    }
    buf[len] = '\0';
    std::cout << buf << std::endl;
    BF bf(buf);
    Status status;
    bool running = true;
    int move = 0;
    while (status != DONE && running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            switch (event.type) {
            case SDL_QUIT:
                running = false;
                break;
            case SDL_KEYDOWN:
                switch (event.key.keysym.sym) {
                case SDLK_w:
                    move = 1;
                    break;
                case SDLK_s:
                    move = 2;
                    break;
                case SDLK_a:
                    move = 3;
                    break;
                case SDLK_d:
                    move = 4;
                    break;
                }
            default:
                break;
            }
        }

        status = bf.interpret((char)move);

        if (status != UPDATE) {
            continue;
        }
        memcpy(screen, bf.tape, SCREEN_SIZE * sizeof(uint8));
        renderer.clear();
        renderScreen(renderer, screen);
        renderer.show();
        SDL_Delay(100);
    }

    SDL_Quit();
    std::cout << std::endl;
    return 0;
}