#include <SDL.h>

// #define uint8 uint8_t
struct Color {
    uint8_t r, g, b, a;
};

class Renderer {
  public:
    Renderer(int x_blocks, int y_blocks, int block_size);
    ~Renderer();

    void clear();
    void renderLattice(int loc, Color color);
    void show();

  private:
    SDL_Renderer *renderer_ = nullptr;
    SDL_Window *window = nullptr;
    int x_blocks, y_blocks, block_size;
};