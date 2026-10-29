int main(int argc, char**) {
    int* values = new int[16];
    values[0] = 7;
    if (argc > 0) {
        values = nullptr;
        return 0;
    }
    delete[] values;
    return 0;
}
