#include "ols_dpi.h"
#include "ols_reference.hpp"

static_assert(sizeof(int)==4 && sizeof(long long)==8, "DPI int/longint ABI width mismatch");

extern "C" int ols_ref_selftest() {
    try { return ols::selftest() ? 1 : 0; } catch (...) { return 0; }
}
extern "C" void* ols_ref_create(int a, int b, int c) {
    try { return new ols::Reference(a,b,c); } catch (...) { return nullptr; }
}
extern "C" void ols_ref_reset(void* handle) {
    if (handle) static_cast<ols::Reference*>(handle)->reset();
}
extern "C" int ols_ref_push(void* handle, int temperature, int* prediction,
                            long long* sum, long long* scaled) {
    if (!handle || !prediction || !sum || !scaled) return -1;
    try {
        const auto p=static_cast<ols::Reference*>(handle)->push(temperature);
        *prediction=p.value; *sum=p.sum; *scaled=p.scaled;
        return p.valid ? 1 : 0;
    } catch (...) { return -1; } // Never let a C++ exception cross the DPI ABI.
}
extern "C" void ols_ref_destroy(void* handle) {
    delete static_cast<ols::Reference*>(handle);
}
