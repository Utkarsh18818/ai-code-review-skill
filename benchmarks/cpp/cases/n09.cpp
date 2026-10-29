#include <climits>
int main(int argc, char**) {
    int total = INT_MAX + argc;
    return total > 0 ? 0 : 1;
}
