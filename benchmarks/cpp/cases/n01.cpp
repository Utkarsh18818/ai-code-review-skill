#include <memory>
int main() {
    int* value = new int(42);
    delete value;
    volatile int observed = *value;
    return observed == 42 ? 0 : 1;
}
