#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>

namespace ols {
inline std::int64_t floor_scale(std::int64_t s) {
    return s / 16384 - ((s < 0 && s % 16384 != 0) ? 1 : 0);
}
inline int saturate(std::int64_t q) {
    return q > 32767 ? 32767 : q < -32768 ? -32768 : static_cast<int>(q);
}
struct Prediction {
    bool valid = false;
    int value = 0;
    std::int64_t sum = 0;
    std::int64_t scaled = 0;
};
// One model per SV chandle; no shared history or static coefficient state.
class Reference {
    std::array<std::int64_t,25> history_{};
    int count_ = 0;
    int a_, b_, c_;
public:
    Reference(int a, int b, int c) : a_(a), b_(b), c_(c) {
        for (int q : {a,b,c})
            if (q < -32768 || q > 32767) throw std::invalid_argument("Coefficient out of range");
    }
    void reset() { history_.fill(0); count_ = 0; }
    Prediction push(int t) {
        if (t < -32768 || t > 32767) throw std::invalid_argument("Sample out of range");
        for (int k=24; k>0; --k) history_[k] = history_[k-1];
        history_[0] = t;
        if (count_ < 25) ++count_;
        if (count_ < 25) return {};
        const auto s = std::int64_t(a_)*(history_[0]-history_[24]) +
                       std::int64_t(b_)*(history_[0]-history_[3]) +
                       (history_[21]+c_)*16384;
        const auto q = floor_scale(s);
        return {true, saturate(q), s, q};
    }
};
inline bool selftest() {
    if (floor_scale(-1)!=-1 || floor_scale(-16384)!=-1 ||
        floor_scale(-16385)!=-2 || floor_scale(16383)!=0 ||
        saturate(32768)!=32767 || saturate(-32769)!=-32768) return false;
    Reference model(8192,3277,0);
    Prediction p;
    for (int n=0; n<25; ++n) {
        int t=0;
        if (n==0) t=4864;   // T(t-24) = 19 C
        if (n==3) t=5376;   // T(t-21) = 21 C
        if (n==21) t=4608;  // T(t-3)  = 18 C
        if (n==24) t=5120;  // T(t)    = 20 C
        p=model.push(t);
        if (n<24 && p.valid) return false;
    }
    if (!p.valid || p.value!=5606) return false;
    model.reset();
    for (int n=0; n<24; ++n) if (model.push(-2560).valid) return false;
    p=model.push(-2560);
    return p.valid && p.value==-2560;
}
} // namespace ols
