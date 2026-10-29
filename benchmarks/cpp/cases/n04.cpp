int main() {
    int observed = 0;
    {
        int value = 42;
        observed = value;
    }
    return observed == 42 ? 0 : 1;
}
