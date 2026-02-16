#include "renderer.h"
#include <SDL.h>
#include <stdexcept>

Renderer::Renderer(int x_blocks, int y_blocks, int block_size)
    : x_blocks(x_blocks), y_blocks(y_blocks), block_size(block_size) {
    int width = x_blocks * block_size;
    int height = y_blocks * block_size;
    window = SDL_CreateWindow("Toy Project", SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, width, height,
                              SDL_WINDOW_SHOWN);
    if (!window) {
        throw std::runtime_error("Window does not created");
    }
    renderer_ = SDL_CreateRenderer(
        window, -1, SDL_RENDERER_ACCELERATED); // gigachad do not handle error
    if (!renderer_) {
        throw std::runtime_error("Renderer does not initialize");
    }
}

Renderer::~Renderer() {
    if (renderer_) {
        SDL_DestroyRenderer(renderer_);
        SDL_DestroyWindow(window);
        renderer_ = nullptr;
        window = nullptr;
    }
}

void Renderer::clear() {
    SDL_SetRenderDrawColor(renderer_, 0, 0, 0, 255);
    SDL_RenderClear(renderer_);
    return;
}

void Renderer::renderLattice(int loc, Color color) {
    int x = (loc % x_blocks) * block_size;
    int y = (loc / x_blocks) * block_size;
    SDL_Rect rect = {x, y, block_size, block_size};
    SDL_SetRenderDrawColor(renderer_, color.r, color.g, color.b, color.a);
    SDL_RenderFillRect(renderer_, &rect);
    return;
}

void Renderer::show() { SDL_RenderPresent(renderer_); }