#include <iostream>
#include <iomanip>

// Các đầu vào là nhiệt độ, đơn vị °C.
double predict_model1(
    double t_now,       // T(t)
    double t_minus_3,   // T(t-3)
    double t_minus_21,  // T(t-21)
    double t_minus_24   // T(t-24)
) {
    constexpr double a = 0.745487043853;
    constexpr double b = 0.00914944498689;
    constexpr double c = 0.00112958165554;

    return t_minus_21
         + a * (t_now - t_minus_24)
         + b * (t_now - t_minus_3)
         + c;
}

int main() {
    // Dữ liệu minh họa: thay bằng nhiệt độ thực tế của bạn.
    double prediction = predict_model1(
        20.0,  // T(t)
        18.0,  // T(t-3)
        21.0,  // T(t-21)
        19.0   // T(t-24)
    );

    std::cout << std::fixed << std::setprecision(6)
              << "Nhiet do du bao sau 3 gio: "
              << prediction << " °C\n";

    return 0;
}