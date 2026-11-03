#pragma once
// DPI scalar mappings: chandle -> void*, int -> int, longint -> long long.
#ifdef __cplusplus
extern "C" {
#endif
int ols_ref_selftest(void);
void* ols_ref_create(int a, int b, int c);
void ols_ref_reset(void* handle);
int ols_ref_push(void* handle, int temperature, int* prediction,
                 long long* sum, long long* scaled);
void ols_ref_destroy(void* handle);
#ifdef __cplusplus
}
#endif
