#include <cstddef>
__attribute__((noinline)) void process(bool stop) {
    int* values = new int[16];
    values[0] = 7;
    if (stop) return;
    delete[] values;
}
int main() { process(true); return 0; }
