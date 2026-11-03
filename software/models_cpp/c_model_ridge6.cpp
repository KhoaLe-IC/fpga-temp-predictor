#include <iostream>
#include <iomanip>

// Các đầu vào là nhiệt độ, đơn vị °C.
double predict_model2(
    double t_now,       // T(t)
    double t_minus_1,   // T(t-1)
    double t_minus_2,   // T(t-2)
    double t_minus_3,   // T(t-3)
    double t_minus_21,  // T(t-21)
    double t_minus_22,  // T(t-22)
    double t_minus_23,  // T(t-23)
    double t_minus_24   // T(t-24)
) {
    constexpr double w1 =  0.758895278214;
    constexpr double w2 =  0.491458178754;
    constexpr double w3 = -0.226643226114;
    constexpr double w4 = -0.029243437324;
    constexpr double w5 =  0.166896383933;
    constexpr double w6 = -0.459862723579;
    constexpr double c  =  0.00105022868928;

    const double x1 = t_now      - t_minus_24;
    const double x2 = t_now      - t_minus_1;
    const double x3 = t_minus_1  - t_minus_2;
    const double x4 = t_minus_2  - t_minus_3;
    const double x5 = t_minus_21 - t_minus_22;
    const double x6 = t_minus_22 - t_minus_23;

    return t_minus_21
         + w1 * x1
         + w2 * x2
         + w3 * x3
         + w4 * x4
         + w5 * x5
         + w6 * x6
         + c;
}

int main() {
    // Dữ liệu minh họa: thay bằng nhiệt độ thực tế của bạn.
    double prediction = predict_model2(
        20.0,  // T(t)
        19.5,  // T(t-1)
        18.8,  // T(t-2)
        18.0,  // T(t-3)
        21.0,  // T(t-21)
        20.5,  // T(t-22)
        20.0,  // T(t-23)
        19.0   // T(t-24)
    );

    std::cout << std::fixed << std::setprecision(6)
              << "Nhiet do du bao sau 3 gio: "
              << prediction << " °C\n";

    return 0;
}