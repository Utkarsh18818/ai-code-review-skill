int main() {
    int* pointer = nullptr;
    {
        int value = 42;
        pointer = &value;
    }
    volatile int observed = *pointer;
    return observed == 42 ? 0 : 1;
}
