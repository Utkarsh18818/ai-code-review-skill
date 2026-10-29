#include <array>
int main(int argc, char**) {
    std::array<int, 5> values{};
    int index = argc + 3;
    if (index < 0 || index >= static_cast<int>(values.size())) return 0;
    values[index] = 9;
    return values[index] == 9 ? 0 : 1;
}
