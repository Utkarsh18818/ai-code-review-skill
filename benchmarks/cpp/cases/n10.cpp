#include <memory>
int main() {
    auto value = std::make_unique<int>(42);
    int observed = *value;
    value.reset();
    return observed == 42 ? 0 : 1;
}
