#include <memory>
int main(int argc, char**) {
    auto values = std::make_unique<int[]>(16);
    values[0] = 7;
    if (argc > 0) return 0;
    return 0;
}
