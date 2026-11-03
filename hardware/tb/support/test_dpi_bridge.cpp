#include "../dpi/ols_dpi.h"
#include <iostream>

// Exercise API status/lifetime/state isolation without requiring a simulator.
int main() {
    int prediction=0;
    long long sum=0, scaled=0;
    if (ols_ref_selftest()!=1 || ols_ref_create(32768,0,0)!=nullptr ||
        ols_ref_push(nullptr,0,&prediction,&sum,&scaled)!=-1) return 1;
    void* first=ols_ref_create(0,0,0);
    void* second=ols_ref_create(0,0,256);
    if (!first || !second) return 1;
    // Invalid arguments must not advance the accepted-sample history.
    if (ols_ref_push(first,32768,&prediction,&sum,&scaled)!=-1 ||
        ols_ref_push(first,0,nullptr,&sum,&scaled)!=-1) return 1;
    for (int n=0; n<25; ++n) {
        if (ols_ref_push(first,5120,&prediction,&sum,&scaled)!=(n>=24)) return 1;
        if (n>=24 && prediction!=5120) return 1;
        if (ols_ref_push(second,-2560,&prediction,&sum,&scaled)!=(n>=24)) return 1;
        if (n>=24 && prediction!=-2304) return 1;
    }
    ols_ref_reset(first);
    if (ols_ref_push(first,0,&prediction,&sum,&scaled)!=0) return 1;
    if (ols_ref_push(second,-2560,&prediction,&sum,&scaled)!=1 || prediction!=-2304) return 1;
    ols_ref_destroy(first); ols_ref_destroy(second); ols_ref_destroy(nullptr);
    ols_ref_reset(nullptr);
    std::cout << "PASS: C++ DPI bridge status, reset, and independent contexts\n";
}
