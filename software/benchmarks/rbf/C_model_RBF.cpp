// Small RBF model: 12 inputs -> 16 Gaussian units -> 1 residual + T(t-21).
// First run Training_RBF.py to create rbf_output/model_rbf.txt.
// Build: g++ -std=c++17 -O2 C_model_RBF.cpp -o rbf
// Demo: ./rbf rbf_output/model_rbf.txt
// Batch: ./rbf rbf_output/model_rbf.txt --batch < rbf_output/test_inputs.txt > cpp_predictions.txt
// Compare cpp_predictions.txt with rbf_output/test_expected.txt using tolerance,
// not exact binary equality: floating-point summation/libm may differ.
// Input row: hour_utc T(t) T(t-1) T(t-2) T(t-3) T(t-6) T(t-12)
//            T(t-21) T(t-22) T(t-23) T(t-24)
// Define RBF_NO_MAIN to embed this class in another C++ program.
// This is a floating-point reference, NOT fixed-point RTL. No external ML library.
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

class RBFTemperature {
    static constexpr int INPUTS = 12, CENTERS = 16;
    std::array<double, INPUTS> mean{}, scale{};
    std::array<std::array<double, INPUTS>, CENTERS> centers{};
    std::array<double, CENTERS> weights{};
    double gamma = 0.0, bias = 0.0;

public:
    explicit RBFTemperature(const std::string& filename) {
        std::ifstream f(filename);
        if (!f) throw std::runtime_error("Cannot open model: " + filename + "; run training first.");
        std::string magic;
        int version, input_count, center_count;
        if (!(f >> magic >> version >> input_count >> center_count >> gamma >> bias)
            || magic != "RBF_TEMP" || version != 1 || input_count != INPUTS
            || center_count != CENTERS || !std::isfinite(gamma) || gamma <= 0
            || !std::isfinite(bias))
            throw std::runtime_error("Invalid model header (expected V1, 12 inputs, 16 centers).");
        auto read_finite = [&f](double& value) {
            if (!(f >> value) || !std::isfinite(value))
                throw std::runtime_error("Invalid/missing model parameter.");
        };
        for (double& value : mean) read_finite(value);
        for (double& value : scale) {
            read_finite(value);
            if (value <= 0) throw std::runtime_error("Scale must be positive.");
        }
        for (auto& center : centers)
            for (double& value : center) read_finite(value);
        for (double& value : weights) read_finite(value);
        std::string extra;
        if (f >> extra) throw std::runtime_error("Unexpected data after model.");
    }

    // history[0] = T(t-24), ..., history[24] = T(t).
    // Caller maintains 25 consecutive hourly samples; reset after a missing hour.
    // hour_utc refers to t, NOT t+3. Replay pauses do not imply missing data.
    double predict(const std::array<double, 25>& history, int hour_utc) const {
        if (hour_utc < 0 || hour_utc > 23)
            throw std::invalid_argument("hour_utc must be 0..23.");
        for (double t : history)
            if (!std::isfinite(t) || t == -999.0)
                throw std::invalid_argument("Invalid/missing temperature.");
        const auto T = [&](int lag) { return history[24-lag]; };
        constexpr double PI = 3.141592653589793238462643383279502884;
        const double angle = 2.0 * PI * hour_utc / 24.0;
        const std::array<double, INPUTS> x = {
            T(0)-T(24), T(0)-T(1), T(1)-T(2), T(2)-T(3),
            T(21)-T(22), T(22)-T(23), T(0), T(21),
            T(0)-T(6), T(0)-T(12), std::sin(angle), std::cos(angle)
        };
        std::array<double, INPUTS> z{};
        for (int i = 0; i < INPUTS; ++i) {
            z[i] = (x[i] - mean[i]) / scale[i];
            if (!std::isfinite(z[i])) throw std::invalid_argument("Feature overflow.");
        }
        double residual = bias;
        for (int j = 0; j < CENTERS; ++j) {
            double distance2 = 0.0;
            for (int i = 0; i < INPUTS; ++i) {
                const double difference = z[i] - centers[j][i];
                distance2 += difference * difference;
            }
            // Uses exp for floating-point reference. FPGA may replace with a LUT,
            // after specifying its domain/rounding and measuring approximation error.
            const double activation = std::exp(-gamma * distance2);
            residual += weights[j] * activation;
        }
        const double prediction = T(21) + residual;
        if (!std::isfinite(prediction)) throw std::runtime_error("Prediction overflow.");
        return prediction;
    }
};

#ifndef RBF_NO_MAIN
int main(int argc, char** argv) {
    try {
        if (argc > 3 || (argc == 3 && std::string(argv[2]) != "--batch"))
            throw std::runtime_error("Usage: rbf [model_rbf.txt] [--batch]");
        const std::string path = argc >= 2 ? argv[1] : "rbf_output/model_rbf.txt";
        const RBFTemperature model(path);
        std::cout << std::setprecision(17);
        if (argc == 3) {
            constexpr int lags[10] = {0, 1, 2, 3, 6, 12, 21, 22, 23, 24};
            std::string line;
            int line_number = 0;
            while (std::getline(std::cin, line)) {
                ++line_number;
                if (line.find_first_not_of(" \t\r") == std::string::npos) continue;
                std::istringstream row(line);
                std::array<double, 25> history{};
                int hour;
                if (!(row >> hour)) throw std::runtime_error("Invalid hour at row " + std::to_string(line_number));
                for (int lag : lags)
                    if (!(row >> history[24-lag]))
                        throw std::runtime_error("Invalid/missing tap at row " + std::to_string(line_number));
                std::string extra;
                if (row >> extra) throw std::runtime_error("Extra field at row " + std::to_string(line_number));
                // Batch file holds the ten required taps only; Training_RBF.py
                // already checked continuity of the full 25-hour window.
                std::cout << model.predict(history, hour) << '\n';
            }
        } else {
            std::array<double, 25> history{};
            history.fill(20.0); // Synthetic example; replace with actual hourly data.
            std::cout << "Example forecast +3h (25 samples at 20 C, current UTC hour 6): "
                      << model.predict(history, 6) << " C\n";
        }
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}
#endif
