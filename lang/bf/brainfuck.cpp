#include "renderer.h"
#include "sound.h"
#include <SDL.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <memory>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

#define STB_TRUETYPE_IMPLEMENTATION
#include "third_party/stb_truetype.h"

using uint8 = unsigned char;

constexpr int SCREEN_W = 8;
constexpr int SCREEN_H = 8;
constexpr int SCREEN_SIZE = SCREEN_W * SCREEN_H;

constexpr int SCREEN_CELL_SCALE = 4;
constexpr int SCREEN_DRAW_W = SCREEN_W * SCREEN_CELL_SCALE;
constexpr int SCREEN_DRAW_H = SCREEN_H * SCREEN_CELL_SCALE;

constexpr int CODE_RADIUS = 10;
constexpr int CODE_WINDOW = (CODE_RADIUS * 2) + 1;
constexpr int SLOT_H = 8;
constexpr int CODE_STRIP_W = SCREEN_DRAW_W;

constexpr int HUD_GAP = 2;
constexpr int BUTTON_GAP = 2;
constexpr int BUTTON_H = 5;
constexpr int BUTTON_COUNT = 3;
constexpr int TOTAL_W = SCREEN_DRAW_W;
constexpr int TOTAL_H = SCREEN_DRAW_H + HUD_GAP + SLOT_H + BUTTON_GAP + BUTTON_H;

constexpr int SCREEN_X = (TOTAL_W - SCREEN_DRAW_W) / 2;
constexpr int SCREEN_Y = 0;
constexpr int CODE_X = (TOTAL_W - CODE_STRIP_W) / 2;
constexpr int CODE_Y = SCREEN_DRAW_H + HUD_GAP;
constexpr int BUTTON_Y = CODE_Y + SLOT_H + BUTTON_GAP;
constexpr int BUTTON_W = (TOTAL_W - BUTTON_GAP * (BUTTON_COUNT + 1)) / BUTTON_COUNT;
constexpr int BUTTON_START_X = BUTTON_GAP;
constexpr int BUTTON_SHIFT_X = BUTTON_START_X + BUTTON_W + BUTTON_GAP;
constexpr int BUTTON_RESET_X = BUTTON_SHIFT_X + BUTTON_W + BUTTON_GAP;
constexpr int BUTTON_RESET_W = TOTAL_W - BUTTON_RESET_X - BUTTON_GAP;

constexpr int BLOCK_SIZE = 12;
constexpr int MIN_STEPS_PER_CURSOR_TICK = 10;
constexpr int MAX_STEPS_PER_CURSOR_TICK = 8192;
constexpr int MAX_STEPS_PER_LOOP = 32768;
constexpr long GRID_FRAME_MS = 1000 / 1;
constexpr double CURSOR_FRAME_MS = 1000.0 / 144.0;
constexpr long GRID_FLOOR_FRAME_MS = 2000; // 0.5 FPS floor
constexpr long OUTPUT_TARGET_MS = 667;      // ~1.5 FPS floor for '.' generation
constexpr double OUTPUT_ESTIMATE_ALPHA = 0.2;
constexpr long COMMAND_RENDER_MIN_MS = 7;  // ~144 FPS
constexpr long COMMAND_RENDER_MAX_MS = 500;
constexpr long COMMAND_SEARCH_WINDOW_MS = 3000;

enum Status { DONE, UPDATE, IDLE, WAIT_INPUT, BIP };

class BF {
  public:
    static constexpr int TAPE_SIZE = 1024;
    uint8 tape[TAPE_SIZE] = {0};
    int ptr = 0;
    Status status = IDLE;

    BF(const std::string &code, unsigned int start_ptr)
        : code_(code), ptr(static_cast<int>(start_ptr)), jump_(code.size(), -1) {
        buildJumpTable();
    }

    void input(uint8 in) { inputs_.push(in); }
    bool step();

    size_t instructionPointer() const { return ip_; }
    const std::string &code() const { return code_; }

  private:
    std::string code_;
    size_t ip_ = 0;
    std::vector<int> jump_;
    std::queue<uint8> inputs_;

    void buildJumpTable();
};

struct GlyphTexture {
    SDL_Texture *texture = nullptr;
    int w = 0;
    int h = 0;
};

class RetroFontCache {
  public:
    ~RetroFontCache() { reset(); }

    bool load(SDL_Renderer *renderer, const char *font_path, float pixel_height);
    void draw(SDL_Renderer *renderer, char ch, const SDL_Rect &dst, Color color) const;
    void reset();

  private:
    bool buildGlyph(SDL_Renderer *renderer, char ch);
    const GlyphTexture *getGlyph(char ch) const;

    stbtt_fontinfo info_{};
    std::vector<unsigned char> font_data_;
    std::array<GlyphTexture, 128> glyphs_{};
    float scale_ = 1.0f;
    bool loaded_ = false;
};

static long now_ms() { return static_cast<long>(SDL_GetTicks64()); }

static std::string read_all_code();
static bool is_bf_token(char ch);
static std::string filter_bf_tokens(const std::string &raw);

static void fillBlockRect(Renderer &renderer, int x, int y, int w, int h, Color color);
static bool pointInBlockRect(int x, int y, int rx, int ry, int rw, int rh);
static void renderScreen(Renderer &renderer, const uint8 *screen);
static Color commandColor(char command);
static void renderCommandWindow(Renderer &renderer, const std::string &code, size_t ip,
                                const RetroFontCache &font, long now);
static void drawTextCentered(Renderer &renderer, const RetroFontCache &font, const char *text,
                             int x, int y, int w, int h, Color color);
static void renderButtons(Renderer &renderer, const RetroFontCache &font, bool paused);
static bool loadRetroFont(RetroFontCache &font, SDL_Renderer *renderer);
static int estimateOpsToNextOutputLinear(const std::string &code, size_t ip);

int main() {
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO) != 0) {
        std::cout << SDL_GetError() << "\n";
        return 1;
    }

    Renderer renderer(TOTAL_W, TOTAL_H, BLOCK_SIZE);
    renderer.setTitle("Brainfuck SNAKE - Retro Font HUD");

    RetroFontCache command_font;
    if (!loadRetroFont(command_font, renderer.nativeRenderer())) {
        SDL_Quit();
        return 1;
    }

    std::unique_ptr<Bip> sound;
    try {
        sound = std::make_unique<Bip>(660.0f);
    } catch (const std::exception &e) {
        std::cerr << e.what() << "\n";
        SDL_Quit();
        return 1;
    }

    const std::string code = filter_bf_tokens(read_all_code());
    if (code.empty()) {
        std::cerr << "No brainfuck tokens found in input.\n";
        SDL_Quit();
        return 1;
    }

    BF bf(code, SCREEN_SIZE);
    std::array<uint8, SCREEN_SIZE> screen = {};
    std::array<uint8, SCREEN_SIZE> pending_screen = {};
    std::memcpy(screen.data(), bf.tape, SCREEN_SIZE * sizeof(uint8));
    std::memcpy(pending_screen.data(), screen.data(), SCREEN_SIZE * sizeof(uint8));
    size_t display_ip = bf.instructionPointer();

    const long start_now = now_ms();
    double next_cursor_tick = static_cast<double>(start_now);
    long last_grid_tick = start_now - GRID_FRAME_MS;
    long pending_since_tick = -1;
    bool has_pending_grid_frame = false;
    bool force_render = true;
    bool command_dirty = true;
    long next_command_render_tick = start_now;
    long command_render_interval_ms = COMMAND_RENDER_MIN_MS;
    long command_search_lo = COMMAND_RENDER_MIN_MS;
    long command_search_hi = COMMAND_RENDER_MAX_MS;
    long command_search_window_start = start_now;
    bool command_search_had_pending = false;
    bool command_search_violation = false;
    int dynamic_steps_per_cursor_tick = MIN_STEPS_PER_CURSOR_TICK;
    size_t ops_since_output = 0;
    const int initial_ops_estimate = estimateOpsToNextOutputLinear(code, bf.instructionPointer());
    double avg_ops_to_output = static_cast<double>(std::max(1, initial_ops_estimate));
    long last_output_tick = start_now;
    bool paused = false;
    bool step_once_requested = false;
    bool running = true;
    while (running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
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
                case SDLK_LSHIFT:
                case SDLK_RSHIFT:
                    if (paused) {
                        step_once_requested = true;
                        force_render = true;
                    }
                    break;
                default:
                    break;
                }
            }
            if (event.type == SDL_MOUSEBUTTONDOWN && event.button.button == SDL_BUTTON_LEFT) {
                const int bx = event.button.x / renderer.blockSize();
                const int by = event.button.y / renderer.blockSize();
                if (pointInBlockRect(bx, by, BUTTON_START_X, BUTTON_Y, BUTTON_W, BUTTON_H)) {
                    paused = !paused;
                    force_render = true;
                    command_dirty = true;
                } else if (pointInBlockRect(bx, by, BUTTON_SHIFT_X, BUTTON_Y, BUTTON_W,
                                            BUTTON_H)) {
                    if (paused) {
                        step_once_requested = true;
                        force_render = true;
                        command_dirty = true;
                    }
                } else if (pointInBlockRect(bx, by, BUTTON_RESET_X, BUTTON_Y, BUTTON_RESET_W,
                                            BUTTON_H)) {
                    bf = BF(code, SCREEN_SIZE);
                    std::memcpy(screen.data(), bf.tape, SCREEN_SIZE * sizeof(uint8));
                    std::memcpy(pending_screen.data(), screen.data(),
                                SCREEN_SIZE * sizeof(uint8));
                    display_ip = bf.instructionPointer();
                    has_pending_grid_frame = false;
                    pending_since_tick = -1;
                    const long reset_now = now_ms();
                    next_cursor_tick = static_cast<double>(reset_now);
                    last_grid_tick = reset_now - GRID_FRAME_MS;
                    command_search_window_start = reset_now;
                    command_search_had_pending = false;
                    command_search_violation = false;
                    force_render = true;
                    command_dirty = true;
                    next_command_render_tick = reset_now;
                    dynamic_steps_per_cursor_tick = MIN_STEPS_PER_CURSOR_TICK;
                    ops_since_output = 0;
                    avg_ops_to_output =
                        static_cast<double>(std::max(1, estimateOpsToNextOutputLinear(
                                                         code, bf.instructionPointer())));
                    last_output_tick = reset_now;
                    step_once_requested = false;
                    sound->stop();
                }
            }
        }

        const long now = now_ms();
        bool finished = false;
        bool cursor_advanced = false;
        bool dot_render_requested = false;
        if (!paused) {
            const long elapsed_since_output = std::max(0L, now - last_output_tick);
            const long budget_left_ms = std::max(1L, OUTPUT_TARGET_MS - elapsed_since_output);
            const int ticks_left = std::max(
                1, static_cast<int>(std::ceil(static_cast<double>(budget_left_ms) / CURSOR_FRAME_MS)));
            const double remain_from_history =
                std::max(1.0, avg_ops_to_output - static_cast<double>(ops_since_output));
            const int linear_to_dot = estimateOpsToNextOutputLinear(code, bf.instructionPointer());
            double estimated_remaining_ops =
                std::max(remain_from_history, static_cast<double>(std::max(1, linear_to_dot)));
            if (elapsed_since_output >= OUTPUT_TARGET_MS && !has_pending_grid_frame) {
                estimated_remaining_ops = std::max(
                    estimated_remaining_ops, static_cast<double>(std::max(1, linear_to_dot)));
            }
            const int target_steps = static_cast<int>(
                std::ceil(estimated_remaining_ops / static_cast<double>(ticks_left)));
            dynamic_steps_per_cursor_tick =
                std::clamp(target_steps, MIN_STEPS_PER_CURSOR_TICK, MAX_STEPS_PER_CURSOR_TICK);

            int catchup_ticks = 0;
            int loop_steps = 0;
            bool saw_dot_update = false;
            while (now >= static_cast<long>(next_cursor_tick) && catchup_ticks < 4 && running) {
                bool saw_bip = false;
                for (int step_count = 0;
                     step_count < dynamic_steps_per_cursor_tick && loop_steps < MAX_STEPS_PER_LOOP;
                     ++step_count) {
                    if (!bf.step()) {
                        finished = true;
                        running = false;
                        break;
                    }
                    ++ops_since_output;
                    ++loop_steps;
                    saw_bip = saw_bip || (bf.status == BIP);
                    if (bf.status == UPDATE) {
                        const size_t observed_ops = std::max<size_t>(1, ops_since_output);
                        avg_ops_to_output =
                            ((1.0 - OUTPUT_ESTIMATE_ALPHA) * avg_ops_to_output) +
                            (OUTPUT_ESTIMATE_ALPHA * static_cast<double>(observed_ops));
                        ops_since_output = 0;
                        last_output_tick = now;
                        if (!has_pending_grid_frame) {
                            pending_since_tick = now;
                        }
                        std::memcpy(pending_screen.data(), bf.tape, SCREEN_SIZE * sizeof(uint8));
                        has_pending_grid_frame = true;
                        command_search_had_pending = true;
                        dot_render_requested = true;
                        saw_dot_update = true;
                        break;
                    }
                }
                display_ip = bf.instructionPointer();
                if (saw_bip) {
                    sound->play();
                } else {
                    sound->stop();
                }
                cursor_advanced = true;
                next_cursor_tick += CURSOR_FRAME_MS;
                catchup_ticks++;
                if (finished) {
                    break;
                }
                if (loop_steps >= MAX_STEPS_PER_LOOP) {
                    break;
                }
                if (saw_dot_update) {
                    // Do not consume further updates before rendering this dot frame.
                    break;
                }
            }
            if (catchup_ticks == 0 && now > static_cast<long>(next_cursor_tick + 1000.0)) {
                next_cursor_tick = static_cast<double>(now);
            }
        } else if (paused) {
            bool did_manual_step = false;
            if (step_once_requested && running) {
                bool saw_bip = false;
                if (!bf.step()) {
                    finished = true;
                    running = false;
                } else {
                    ++ops_since_output;
                    saw_bip = (bf.status == BIP);
                    display_ip = bf.instructionPointer();
                    cursor_advanced = true;
                    if (bf.status == UPDATE) {
                        const size_t observed_ops = std::max<size_t>(1, ops_since_output);
                        avg_ops_to_output =
                            ((1.0 - OUTPUT_ESTIMATE_ALPHA) * avg_ops_to_output) +
                            (OUTPUT_ESTIMATE_ALPHA * static_cast<double>(observed_ops));
                        ops_since_output = 0;
                        last_output_tick = now;
                        if (!has_pending_grid_frame) {
                            pending_since_tick = now;
                        }
                        std::memcpy(pending_screen.data(), bf.tape, SCREEN_SIZE * sizeof(uint8));
                        has_pending_grid_frame = true;
                        command_search_had_pending = true;
                        dot_render_requested = true;
                    }
                }
                if (saw_bip) {
                    sound->play();
                } else {
                    sound->stop();
                }
                did_manual_step = true;
                step_once_requested = false;
            }
            if (!did_manual_step) {
                sound->stop();
            }
            if (now >= static_cast<long>(next_cursor_tick)) {
                next_cursor_tick = static_cast<double>(now);
            }
        }

        if (cursor_advanced) {
            command_dirty = true;
        }

        if (has_pending_grid_frame && pending_since_tick >= 0 &&
            (now - pending_since_tick) > GRID_FLOOR_FRAME_MS) {
            command_search_violation = true;
        }

        bool grid_applied = false;
        if (has_pending_grid_frame &&
            (dot_render_requested || (now - last_grid_tick) >= GRID_FRAME_MS)) {
            std::memcpy(screen.data(), pending_screen.data(), SCREEN_SIZE * sizeof(uint8));
            has_pending_grid_frame = false;
            pending_since_tick = -1;
            last_grid_tick = now;
            grid_applied = true;
        }

        if ((now - command_search_window_start) >= COMMAND_SEARCH_WINDOW_MS) {
            if (command_search_had_pending) {
                const long current_interval =
                    std::clamp(command_render_interval_ms, COMMAND_RENDER_MIN_MS,
                               COMMAND_RENDER_MAX_MS);
                if (command_search_violation) {
                    // Violation: search slower half.
                    command_search_lo = current_interval;
                    command_search_hi = COMMAND_RENDER_MAX_MS;
                } else {
                    // Healthy: search faster half.
                    command_search_lo = COMMAND_RENDER_MIN_MS;
                    command_search_hi = current_interval;
                }

                long mid = command_search_lo + ((command_search_hi - command_search_lo) / 2);
                mid = std::clamp(mid, COMMAND_RENDER_MIN_MS, COMMAND_RENDER_MAX_MS);
                if (mid == current_interval) {
                    if (command_search_violation && current_interval < COMMAND_RENDER_MAX_MS) {
                        mid = current_interval + 1;
                    } else if (!command_search_violation &&
                               current_interval > COMMAND_RENDER_MIN_MS) {
                        mid = current_interval - 1;
                    }
                }
                command_render_interval_ms = mid;
            }
            command_search_window_start = now;
            command_search_had_pending = false;
            command_search_violation = false;
        }

        const bool command_render_due =
            command_dirty && (now >= static_cast<long>(next_command_render_tick));
        const bool should_render = force_render || grid_applied || finished || command_render_due;
        if (!should_render) {
            SDL_Delay(1);
            continue;
        }

        renderer.clear();
        renderScreen(renderer, screen.data());

        renderCommandWindow(renderer, code, display_ip, command_font, now_ms());
        renderButtons(renderer, command_font, paused);
        renderer.show();

        if (command_dirty) {
            command_dirty = false;
            next_command_render_tick = now + command_render_interval_ms;
        }
        force_render = false;

        if (finished) {
            std::cout << "end\n";
        }
    }

    SDL_Quit();
    return 0;
}

bool RetroFontCache::load(SDL_Renderer *renderer, const char *font_path, float pixel_height) {
    reset();

    std::ifstream in(font_path, std::ios::binary);
    if (!in) {
        return false;
    }
    font_data_ = std::vector<unsigned char>(std::istreambuf_iterator<char>(in), {});
    if (font_data_.empty()) {
        return false;
    }
    if (!stbtt_InitFont(&info_, font_data_.data(),
                        stbtt_GetFontOffsetForIndex(font_data_.data(), 0))) {
        return false;
    }

    scale_ = stbtt_ScaleForPixelHeight(&info_, pixel_height);
    if (scale_ <= 0.0f) {
        return false;
    }

    const std::string supported = "><+-.,[]! ?";
    const std::string labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    std::string all = supported + labels;
    for (char ch : all) {
        if (!buildGlyph(renderer, ch)) {
            return false;
        }
    }
    loaded_ = true;
    return true;
}

bool RetroFontCache::buildGlyph(SDL_Renderer *renderer, char ch) {
    const unsigned char idx = static_cast<unsigned char>(ch);
    if (idx >= glyphs_.size()) {
        return false;
    }
    if (ch == ' ') {
        return true;
    }
    if (glyphs_[idx].texture) {
        return true;
    }

    int w = 0;
    int h = 0;
    int xoff = 0;
    int yoff = 0;
    unsigned char *bitmap =
        stbtt_GetCodepointBitmap(&info_, 0.0f, scale_, ch, &w, &h, &xoff, &yoff);
    if (!bitmap || w <= 0 || h <= 0) {
        if (bitmap) {
            stbtt_FreeBitmap(bitmap, nullptr);
        }
        return false;
    }

    std::vector<uint8_t> pixels(static_cast<size_t>(w) * static_cast<size_t>(h) * 4, 0);
    for (int i = 0; i < w * h; ++i) {
        const size_t o = static_cast<size_t>(i) * 4;
        pixels[o + 0] = 255;
        pixels[o + 1] = 255;
        pixels[o + 2] = 255;
        pixels[o + 3] = bitmap[i];
    }

    // RGBA byte-array upload path (endianness-safe).
    SDL_Texture *texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                                             SDL_TEXTUREACCESS_STATIC, w, h);
    if (!texture) {
        stbtt_FreeBitmap(bitmap, nullptr);
        return false;
    }
    SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_BLEND);
    if (SDL_UpdateTexture(texture, nullptr, pixels.data(), w * 4) != 0) {
        SDL_DestroyTexture(texture);
        stbtt_FreeBitmap(bitmap, nullptr);
        return false;
    }

    glyphs_[idx].texture = texture;
    glyphs_[idx].w = w;
    glyphs_[idx].h = h;
    stbtt_FreeBitmap(bitmap, nullptr);
    return true;
}

void RetroFontCache::draw(SDL_Renderer *renderer, char ch, const SDL_Rect &dst, Color color) const {
    if (!loaded_ || dst.w <= 0 || dst.h <= 0) {
        return;
    }

    const GlyphTexture *glyph = getGlyph(ch);
    if (!glyph || !glyph->texture) {
        return;
    }

    const float sx = static_cast<float>(dst.w) / static_cast<float>(glyph->w);
    const float sy = static_cast<float>(dst.h) / static_cast<float>(glyph->h);
    const float scale = std::max(0.01f, std::min(sx, sy));
    const int draw_w = std::max(1, static_cast<int>(glyph->w * scale));
    const int draw_h = std::max(1, static_cast<int>(glyph->h * scale));

    SDL_Rect draw_rect = {dst.x + (dst.w - draw_w) / 2, dst.y + (dst.h - draw_h) / 2, draw_w,
                          draw_h};
    SDL_SetTextureColorMod(glyph->texture, color.r, color.g, color.b);
    SDL_SetTextureAlphaMod(glyph->texture, color.a);
    SDL_RenderCopy(renderer, glyph->texture, nullptr, &draw_rect);
}

const GlyphTexture *RetroFontCache::getGlyph(char ch) const {
    const unsigned char idx = static_cast<unsigned char>(ch);
    if (idx < glyphs_.size() && glyphs_[idx].texture) {
        return &glyphs_[idx];
    }
    const unsigned char fallback = static_cast<unsigned char>('?');
    if (fallback < glyphs_.size() && glyphs_[fallback].texture) {
        return &glyphs_[fallback];
    }
    return nullptr;
}

void RetroFontCache::reset() {
    for (GlyphTexture &glyph : glyphs_) {
        if (glyph.texture) {
            SDL_DestroyTexture(glyph.texture);
            glyph.texture = nullptr;
        }
        glyph.w = 0;
        glyph.h = 0;
    }
    font_data_.clear();
    loaded_ = false;
}

bool BF::step() {
    if (ip_ >= code_.size()) {
        status = DONE;
        return false;
    }

    status = IDLE;
    switch (code_[ip_]) {
    case '>':
        ptr = (ptr + 1) % TAPE_SIZE;
        break;
    case '<':
        ptr = (ptr - 1 + TAPE_SIZE) % TAPE_SIZE;
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
        if (inputs_.empty()) {
            tape[ptr] = 0;
        } else {
            tape[ptr] = inputs_.front();
            inputs_.pop();
        }
        break;
    case '[':
        if (tape[ptr] == 0 && jump_[ip_] >= 0) {
            ip_ = static_cast<size_t>(jump_[ip_]);
        }
        break;
    case ']':
        if (tape[ptr] != 0 && jump_[ip_] >= 0) {
            ip_ = static_cast<size_t>(jump_[ip_]);
        }
        break;
    case '!':
        status = BIP;
        break;
    default:
        status = DONE;
        return false;
    }
    ++ip_;
    return true;
}

void BF::buildJumpTable() {
    std::vector<size_t> stack;
    stack.reserve(code_.size() / 8);
    for (size_t idx = 0; idx < code_.size(); ++idx) {
        if (code_[idx] == '[') {
            stack.push_back(idx);
            continue;
        }
        if (code_[idx] == ']') {
            if (stack.empty()) {
                continue;
            }
            const size_t open = stack.back();
            stack.pop_back();
            jump_[open] = static_cast<int>(idx);
            jump_[idx] = static_cast<int>(open);
        }
    }
}

static void fillBlockRect(Renderer &renderer, int x, int y, int w, int h, Color color) {
    SDL_Renderer *raw = renderer.nativeRenderer();
    const int bs = renderer.blockSize();
    SDL_Rect rect = {x * bs, y * bs, w * bs, h * bs};
    SDL_SetRenderDrawColor(raw, color.r, color.g, color.b, color.a);
    SDL_RenderFillRect(raw, &rect);
}

static bool pointInBlockRect(int x, int y, int rx, int ry, int rw, int rh) {
    return x >= rx && x < (rx + rw) && y >= ry && y < (ry + rh);
}

static void renderScreen(Renderer &renderer, const uint8 *screen) {
    for (int i = 0; i < SCREEN_SIZE; ++i) {
        const uint8 pixel = screen[i];
        Color color = {0, 0, 0, 255};
        if (pixel > 127) {
            color.r = static_cast<uint8>((pixel - 128) * 2);
        } else {
            color.g = static_cast<uint8>(pixel * 2);
        }

        const int cell_x = i % SCREEN_W;
        const int cell_y = i / SCREEN_W;
        const int draw_x = SCREEN_X + cell_x * SCREEN_CELL_SCALE;
        const int draw_y = SCREEN_Y + cell_y * SCREEN_CELL_SCALE;
        fillBlockRect(renderer, draw_x, draw_y, SCREEN_CELL_SCALE, SCREEN_CELL_SCALE, color);
    }
}

static Color commandColor(char command) {
    switch (command) {
    case '>':
    case '<':
        return {46, 144, 255, 255};
    case '[':
    case ']':
        return {66, 214, 66, 255};
    case '+':
    case '-':
    case '.':
    case ',':
    case '!':
        return {230, 230, 230, 255};
    default:
        return {185, 185, 185, 255};
    }
}

static void renderCommandWindow(Renderer &renderer, const std::string &code, size_t ip_raw,
                                const RetroFontCache &font, long now) {
    (void)now;
    const Color panel_bg = {10, 10, 10, 255};
    fillBlockRect(renderer, CODE_X, CODE_Y, CODE_STRIP_W, SLOT_H, panel_bg);

    const int ip = static_cast<int>(ip_raw);
    const int bs = renderer.blockSize();
    SDL_Renderer *raw = renderer.nativeRenderer();
    const int side_slot_w = 1;
    const int focus_slot_w = std::max(1, CODE_STRIP_W - side_slot_w * (CODE_WINDOW - 1));
    int slot_x = CODE_X;

    for (int slot = 0; slot < CODE_WINDOW; ++slot) {
        const int code_idx = ip + slot - CODE_RADIUS;
        char command = ' ';
        if (code_idx >= 0 && code_idx < static_cast<int>(code.size())) {
            command = code[static_cast<size_t>(code_idx)];
        }

        const bool focused = slot == CODE_RADIUS;
        Color fg = commandColor(command);
        const int cur_slot_w = focused ? focus_slot_w : side_slot_w;

        SDL_Rect slot_rect = {slot_x * bs + 2, CODE_Y * bs + 2, std::max(1, cur_slot_w * bs - 4),
                              std::max(1, SLOT_H * bs - 4)};
        if (focused) {
            // Keep the focused glyph very large but clipped to its own slot.
            slot_rect = {slot_x * bs + 1, CODE_Y * bs + 1, std::max(1, cur_slot_w * bs - 2),
                         std::max(1, SLOT_H * bs - 2)};
        }
        SDL_Rect clip_rect = {slot_x * bs, CODE_Y * bs, std::max(1, cur_slot_w * bs),
                              std::max(1, SLOT_H * bs)};
        SDL_RenderSetClipRect(raw, &clip_rect);
        font.draw(raw, command, slot_rect, fg);
        SDL_RenderSetClipRect(raw, nullptr);
        slot_x += cur_slot_w;
    }
}

static void drawTextCentered(Renderer &renderer, const RetroFontCache &font, const char *text,
                             int x, int y, int w, int h, Color color) {
    if (!text || !*text) {
        return;
    }
    const int len = static_cast<int>(std::strlen(text));
    if (len <= 0) {
        return;
    }

    SDL_Renderer *raw = renderer.nativeRenderer();
    const int bs = renderer.blockSize();
    const int px = x * bs;
    const int py = y * bs;
    const int pw = w * bs;
    const int ph = h * bs;
    const int pad = 4;
    const int avail_w = std::max(1, pw - pad * 2);
    const int avail_h = std::max(1, ph - pad * 2);
    const int cell_w = std::max(1, avail_w / len);
    const int draw_w = std::max(1, cell_w - 1);
    const int total_w = cell_w * len;
    const int start_x = px + (pw - total_w) / 2;
    const int start_y = py + (ph - avail_h) / 2;

    for (int i = 0; i < len; ++i) {
        SDL_Rect glyph_rect = {start_x + i * cell_w, start_y, draw_w, avail_h};
        font.draw(raw, text[i], glyph_rect, color);
    }
}

static void renderButtons(Renderer &renderer, const RetroFontCache &font, bool paused) {
    const Color panel = {0, 0, 0, 255};
    const Color fill = {20, 20, 20, 255};
    const Color disabled_fg = {88, 88, 88, 255};
    fillBlockRect(renderer, 0, BUTTON_Y - 1, TOTAL_W, BUTTON_H + 1, panel);

    auto draw_button = [&](int x, int w, const char *label, bool active, bool enabled,
                           Color base_text) {
        Color btn_fill = fill;
        Color text = enabled ? base_text : disabled_fg;
        if (active) {
            btn_fill = {230, 230, 230, 255};
            text = {0, 0, 0, 255};
        }
        fillBlockRect(renderer, x, BUTTON_Y, w, BUTTON_H, btn_fill);
        drawTextCentered(renderer, font, label, x, BUTTON_Y, w, BUTTON_H, text);
    };

    draw_button(BUTTON_START_X, BUTTON_W, paused ? "START" : "STOP", !paused, true,
                {46, 144, 255, 255});
    draw_button(BUTTON_SHIFT_X, BUTTON_W, "STEP", false, paused, {66, 214, 66, 255});
    draw_button(BUTTON_RESET_X, BUTTON_RESET_W, "RESET", false, true, {235, 235, 235, 255});
}

static bool loadRetroFont(RetroFontCache &font, SDL_Renderer *renderer) {
    constexpr const char *FONT_CANDIDATES[] = {"Retro Gaming.ttf", "./Retro Gaming.ttf",
                                               ".\\Retro Gaming.ttf"};
    const float font_pixels = static_cast<float>(SLOT_H * BLOCK_SIZE - 4);
    for (const char *path : FONT_CANDIDATES) {
        if (font.load(renderer, path, font_pixels)) {
            return true;
        }
    }
    std::cerr << "Failed to load Retro Gaming.ttf\n";
    return false;
}

static std::string read_all_code() {
    constexpr const char *kProgramPath = "snake.bf";
    std::ifstream in(kProgramPath, std::ios::binary);
    if (!in) {
        throw std::runtime_error("failed to open snake.bf");
    }
    return std::string(std::istreambuf_iterator<char>(in), {});
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
    default:
        return false;
    }
}

static std::string filter_bf_tokens(const std::string &raw) {
    std::string out;
    out.reserve(raw.size());
    for (char ch : raw) {
        if (is_bf_token(ch)) {
            out.push_back(ch);
        }
    }
    return out;
}

static int estimateOpsToNextOutputLinear(const std::string &code, size_t ip) {
    if (code.empty()) {
        return 1;
    }
    const size_t bounded_ip = std::min(ip, code.size());
    for (size_t i = bounded_ip; i < code.size(); ++i) {
        if (code[i] == '.') {
            return static_cast<int>((i - bounded_ip) + 1);
        }
    }
    // Fallback for loops/back-jumps: use full code span as coarse upper bound.
    return static_cast<int>(std::max<size_t>(1, code.size()));
}
