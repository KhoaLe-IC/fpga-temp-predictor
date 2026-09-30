// Shallow boosted-tree floating-point inference for T(t+3).
// First run Training_BoostedTrees.py to create boosted_output/model_boosted.txt.
// Build: g++ -std=c++17 -O2 C_model_BoostedTrees.cpp -o boosted
// Demo: ./boosted boosted_output/model_boosted.txt
// Batch: ./boosted boosted_output/model_boosted.txt --batch < boosted_output/test_inputs.txt
// Row format: hour_utc T(t) T(t-1) T(t-2) T(t-3) T(t-6) T(t-12)
//             T(t-21) T(t-22) T(t-23) T(t-24)
// Output: one forecast in degrees C per row, in the same order.
// Compile with -DBOOSTED_NO_MAIN when integrating into another C++ program.
// This is NOT fixed-point RTL. Do not use -ffast-math for reference comparisons.
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

class BoostedTemperature {
    static constexpr int N_FEATURES = 12;
    struct Node {
        int feature, left, right;
        double threshold, value;
    };
    std::vector<std::vector<Node>> trees;
    double base = 0.0;

public:
    explicit BoostedTemperature(const std::string& filename) {
        std::ifstream f(filename);
        if (!f) throw std::runtime_error("Cannot open model: " + filename + "; run training first.");
        std::string magic;
        int version, feature_count, tree_count;
        if (!(f >> magic >> version >> feature_count >> tree_count >> base)
            || magic != "BOOSTED_TEMP" || version != 1 || feature_count != N_FEATURES
            || tree_count != 32 || !std::isfinite(base))
            throw std::runtime_error("Invalid model header (expected V1, 12 features, 32 trees).");

        for (int k = 0; k < tree_count; ++k) {
            int count;
            if (!(f >> count) || count < 1 || count > 15)
                throw std::runtime_error("Invalid node count for depth <= 3.");
            std::vector<Node> nodes(count);
            std::vector<int> parents(count, 0), depth(count, 0);
            for (int i = 0; i < count; ++i) {
                auto& n = nodes[i];
                if (!(f >> n.feature >> n.threshold >> n.left >> n.right >> n.value)
                    || !std::isfinite(n.threshold) || !std::isfinite(n.value))
                    throw std::runtime_error("Invalid tree node.");
                if (n.feature == -1) {
                    if (n.left != -1 || n.right != -1)
                        throw std::runtime_error("Invalid leaf.");
                } else {
                    // sklearn export uses preorder indices: children > parent.
                    if (n.feature < 0 || n.feature >= N_FEATURES
                        || n.left <= i || n.left >= count || n.right <= i || n.right >= count
                        || n.left == n.right || depth[i] >= 3)
                        throw std::runtime_error("Invalid split or excessive depth.");
                    ++parents[n.left]; ++parents[n.right];
                    depth[n.left] = depth[n.right] = depth[i] + 1;
                }
            }
            for (int i = 1; i < count; ++i)
                if (parents[i] != 1) throw std::runtime_error("Disconnected/shared tree node.");
            trees.push_back(std::move(nodes));
        }
        std::string extra;
        if (f >> extra) throw std::runtime_error("Unexpected data after model.");
    }

    // history[0]=T(t-24), ..., history[24]=T(t).
    // Caller must supply 25 CONSECUTIVE hourly samples; reset after missing data.
    // hour_utc is the hour of the current sample t, not the future target t+3.
    double predict(const std::array<double, 25>& history, int hour_utc) const {
        if (hour_utc < 0 || hour_utc > 23)
            throw std::invalid_argument("hour_utc must be 0..23.");
        for (double t : history)
            if (!std::isfinite(t) || t == -999.0)
                throw std::invalid_argument("Invalid/missing temperature.");
        const auto T = [&](int lag) { return history[24 - lag]; };
        constexpr double PI = 3.141592653589793238462643383279502884;
        const double angle = 2.0 * PI * hour_utc / 24.0;
        const std::array<double, N_FEATURES> raw = {
            T(0)-T(24), T(0)-T(1), T(1)-T(2), T(2)-T(3),
            T(21)-T(22), T(22)-T(23), T(0), T(21),
            T(0)-T(6), T(0)-T(12), std::sin(angle), std::cos(angle)
        };
        // Match the float32 feature values used by sklearn tree inference.
        std::array<float, N_FEATURES> x{};
        for (int i = 0; i < N_FEATURES; ++i) {
            x[i] = static_cast<float>(raw[i]);
            if (!std::isfinite(x[i])) throw std::invalid_argument("Feature overflow.");
        }
        double residual = base;
        for (const auto& tree : trees) {
            int index = 0;
            while (tree[index].feature != -1) {
                const auto& node = tree[index];
                // Equality follows the LEFT branch, exactly as in training.
                index = static_cast<double>(x[node.feature]) <= node.threshold
                      ? node.left : node.right;
            }
            residual += tree[index].value; // learning_rate already folded in leaf
        }
        return T(21) + residual;
    }
};

#ifndef BOOSTED_NO_MAIN
int main(int argc, char** argv) {
    try {
        if (argc > 3 || (argc == 3 && std::string(argv[2]) != "--batch"))
            throw std::runtime_error("Usage: boosted [model_boosted.txt] [--batch]");
        const std::string path = argc >= 2 ? argv[1] : "boosted_output/model_boosted.txt";
        const BoostedTemperature model(path);
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
                // Batch file contains required taps only; continuity has already
                // been checked by Training_BoostedTrees.py before export.
                std::cout << model.predict(history, hour) << '\n';
            }
        } else {
            std::array<double, 25> history{};
            history.fill(20.0); // Synthetic demo: replace with real hourly samples.
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
