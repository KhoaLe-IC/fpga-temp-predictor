// Offline vectors from the same C++ golden model used by live DPI calls.
#include "../dpi/ols_reference.hpp"
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
    try {
        if (argc != 6) throw std::runtime_error("Usage: generate_vectors OUT A_Q B_Q C_Q COUNT");
        const int a = std::stoi(argv[2]), b = std::stoi(argv[3]), c = std::stoi(argv[4]);
        const int count = std::stoi(argv[5]);
        for (int coefficient : {a,b,c})
            if (coefficient < -32768 || coefficient > 32767)
                throw std::runtime_error("Coefficient outside signed 16-bit range");
        if (count < 25) throw std::runtime_error("COUNT must be at least 25");
        std::ofstream out(argv[1]);
        if (!out) throw std::runtime_error("Cannot open output");
        out << a << ' ' << b << ' ' << c << '\n';
        ols::Reference model(a,b,c);
        std::uint32_t state = 0x12345678u;
        for (int n = 0; n < count; ++n) {
            state = state * 1664525u + 1013904223u;
            // Convert to signed 16-bit mathematical value without a narrowing
            // cast from an out-of-range unsigned value.
            int t = static_cast<int>(state >> 16);
            if (t >= 32768) t -= 65536;
            if (n % 97 == 0) t = -32768;
            if (n % 97 == 1) t = 32767;
            const auto prediction = model.push(t);
            out << t << ' ' << (prediction.valid ? 1 : 0) << ' ' << prediction.value << '\n';
        }
        if (!out) throw std::runtime_error("Write failed");
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
