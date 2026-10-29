#include <cstdlib>
#include <memory>
int main() {
    std::unique_ptr<void, decltype(&std::free)> data(std::malloc(16), &std::free);
    if (!data) return 2;
    data.reset();
    data.reset();
    return 0;
}
