#include <memory>
void process(bool stop) {
    auto values = std::make_unique<int[]>(16);
    values[0] = 7;
    if (stop) return;
}
int main() { process(true); return 0; }
