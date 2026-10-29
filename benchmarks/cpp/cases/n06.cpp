#include <climits>
#include <cstdint>
int main(int argc, char**) {
    std::int64_t total = static_cast<std::int64_t>(INT_MAX) + argc;
    return total > INT_MAX ? 0 : 1;
}
