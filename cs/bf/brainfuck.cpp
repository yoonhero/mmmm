#include "renderer.h"
#include <SDL.h>
#include <fstream>
#include <iostream>
#include <iterator>
#include <queue>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <utility>

#define uint8 unsigned char
#define SCREEN_SIZE 8 * 8
#define inputBuf std::queue<uint8>

enum Status { DONE, UPDATE, IDLE, WAIT_INPUT };

class BF {
  public:
    static constexpr int TAPE_SIZE = 1024;
    uint8 tape[TAPE_SIZE] = {0};
    int ptr;
    char current_char;
    Status status;
    inputBuf inputs;

    BF(const char *code, unsigned int startPtr)
        : source_code(code), ptr(startPtr), i(0), status(IDLE) {}
    void input(uint8 in);
    bool step();

  private:
    const char *source_code;
    unsigned int loop, i;
};

static void renderScreen(Renderer &renderer, uint8 *screen);
static std::string read_all_code(int argc, char *argv[]);
static bool is_bf_token(char ch);
static std::string filter_bf_tokens(const std::string &raw);

int main(int argc, char *argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cout << SDL_GetError() << "\n";
        return 1;
    }

    uint8 screen[SCREEN_SIZE];
    Renderer renderer(8, 8, 60);

    std::string code = filter_bf_tokens(read_all_code(argc, argv));
    // std::cout << code.data() << "\n";
    BF bf(code.data(), SCREEN_SIZE);

    bool running = true;
    while (running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            switch (event.type) {
            case SDL_QUIT:
                running = false;
                break;
            case SDL_KEYDOWN:
                // if (bf.status != WAIT_INPUT)
                //     continue;
                switch (event.key.keysym.sym) {
                case SDLK_w:
                    bf.input(1);
                    break;
                case SDLK_s:
                    bf.input(3);
                    break;
                case SDLK_a:
                    bf.input(2);
                    break;
                case SDLK_d:
                    bf.input(4);
                    break;
                default:
                    bf.input(0);
                    break;
                }
            default:
                break;
            }
        }

        if (!bf.step()) {
            std::cout << "end" << "\n";
            break;
        }

        if (bf.status == UPDATE) {
            memcpy(screen, bf.tape, SCREEN_SIZE * sizeof(uint8));
            renderer.clear();
            renderScreen(renderer, screen);
            renderer.show();
            SDL_Delay(100);
        }
    }

    SDL_Quit();
    return 0;
}

bool BF::step() {
    if (source_code[i] == 0) {
        status = DONE;
        return false;
    }
    status = IDLE;
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
        status = UPDATE;
        break;
    case ',':
        if (inputs.empty()) {
            status = WAIT_INPUT;
            return true;
        }
        tape[ptr] = inputs.front();
        inputs.pop();
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
    default:
        return false;
    }
    i++;
    return true;
}

void BF::input(uint8 in) { inputs.push(in); }

static void renderScreen(Renderer &renderer, uint8 *screen) {
    for (int i = 0; i < SCREEN_SIZE; ++i) {
        Color color = {screen[i], screen[i], screen[i], 0};
        renderer.renderLattice(i, color);
    }
}

static std::string read_all_code(int argc, char *argv[]) {
    if (argc > 1) {
        std::ifstream in(argv[1], std::ios::binary);
        if (!in)
            throw std::runtime_error("failed to open file");
        return std::string(std::istreambuf_iterator<char>(in), {});
    }
    return std::string(std::istreambuf_iterator<char>(std::cin), {});
}

static bool is_bf_token(char ch) {
    switch (ch) {
    case '>':
    case '<':
    case '+':
    case '-':
    case '.':
    case ',':
    case '[':
    case ']':
        return true;
    }
    return false;
}

static std::string filter_bf_tokens(const std::string &raw) {
    std::string out;
    out.reserve(raw.size());
    for (char ch : raw) {
        if (is_bf_token(ch))
            out.push_back(ch);
    }
    return out;
}
