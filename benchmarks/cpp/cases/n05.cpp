#include <cstdlib>
int main() {
    void* data = std::malloc(16);
    if (!data) return 2;
    std::free(data);
    std::free(data);
    return 0;
}
