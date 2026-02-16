#include <SDL.h>
#include <cmath>
#include <iostream>

struct AudioState {
    float phase = 0.0f;
    float freq = 440.0f;
    float amp = 0.5f; // 볼륨 (0~1)
};

static void audio_callback(void *userdata, Uint8 *stream, int len) {
    auto *state = static_cast<AudioState *>(userdata);

    float *buffer = reinterpret_cast<float *>(stream);
    int frames = len / sizeof(float); // mono라서 frames == float 개수

    const float sample_rate = 44100.0f;
    const float step = 2.0f * float(M_PI) * state->freq / sample_rate;

    for (int i = 0; i < frames; ++i) {
        buffer[i] = state->amp * std::sin(state->phase);
        state->phase += step;
        if (state->phase > 2.0f * float(M_PI))
            state->phase -= 2.0f * float(M_PI);
    }
}

class Bip {
  public:
    Bip(float freq) {
        SDL_AudioSpec want{};
        want.freq = freq * 100;
        want.format = AUDIO_F32SYS;
        want.channels = 1;
        want.samples = 512;
        want.callback = audio_callback;

        state_.freq = freq;
        want.userdata = &state_;

        dev_ = SDL_OpenAudioDevice(nullptr, 0, &want, nullptr, 0);
        if (!dev_) {
            throw std::runtime_error(SDL_GetError());
        }
    };
    ~Bip() { SDL_CloseAudioDevice(dev_); };

    void play() { SDL_PauseAudioDevice(dev_, 0); };

    void stop() { SDL_PauseAudioDevice(dev_, 1); }

  private:
    SDL_AudioDeviceID dev_ = 0;
    AudioState state_{};
};
