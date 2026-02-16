#include "renderer.h"
#include "sound.h"
#include <SDL.h>
#include <SDL_audio.h>
#include <fstream>
#include <iostream>
#include <iterator>
#include <queue>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <time.h>
#include <utility>

#define uint8 unsigned char
#define SCREEN_SIZE 8 * 8
#define inputBuf std::queue<uint8>

enum Status { DONE, UPDATE, IDLE, WAIT_INPUT, BIP };

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

static long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

int main(int argc, char *argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0 || SDL_Init(SDL_INIT_AUDIO) != 0) {
        std::cout << SDL_GetError() << "\n";
        return 1;
    }

    uint8 screen[SCREEN_SIZE];
    Renderer renderer(8, 8, 60);

    std::unique_ptr<Bip> sound;
    try {
        sound = std::make_unique<Bip>(660.0f);
    } catch (const std::exception &e) {
        std::cerr << e.what() << "\n";
        return 1;
    }

    std::string code = filter_bf_tokens(read_all_code(argc, argv));
    // std::cout << code.data() << "\n";
    BF bf(code.data(), SCREEN_SIZE);

    const long frame_ms = 1000 / 3; // there's big time lag on 56~63. 10fps
                                    // cannot stabilize well through.
    long prevTick = now_ms();

    bool running = true;
    while (running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT)
                running = false;
            if (event.type == SDL_KEYDOWN) {
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
                }
            }
        }

        if (!bf.step()) {
            std::cout << "end" << "\n";
            break;
        }

        if (bf.status == BIP) {
            sound->play();
        }

        // debugging
        // int upto = 17 + 5;
        // if (bf.ptr >= SCREEN_SIZE && bf.ptr < SCREEN_SIZE + upto) {
        //     for (int i = 0; i < upto; i++) {
        //         if (i == 2 || i == 4 || i == 5 || i == 10 || i == 14 ||
        //             i == 15 || i == 16 || i == 17)
        //             std::cout << "| ";
        //         if (i + SCREEN_SIZE == bf.ptr) {
        //             std::cout << ">";
        //         }
        //         std::cout << std::to_string(bf.tape[SCREEN_SIZE + i]) << " ";
        //     }
        //     std::cout << "\n";
        // }

        if (bf.status == UPDATE) {
            memcpy(screen, bf.tape, SCREEN_SIZE * sizeof(uint8));
            renderer.clear();
            renderScreen(renderer, screen);
            renderer.show();
            long now = now_ms();
            long elapsed = now - prevTick;
            if (elapsed < frame_ms)
                SDL_Delay(frame_ms - elapsed);
            prevTick = now_ms();
            sound->stop();
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
            // status = WAIT_INPUT;
            // inputs.push(0);
            // return true;
            tape[ptr] = 0;
        } else {
            tape[ptr] = inputs.front();
            inputs.pop();
        }
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
    case '!':
        status = BIP;
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
        const uint pixel = screen[i];
        Color color = {0};
        if (pixel > 127) {
            color.r = (pixel - 128) * 2;
        } else {
            color.g = pixel * 2;
        }
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
    case '!':
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
