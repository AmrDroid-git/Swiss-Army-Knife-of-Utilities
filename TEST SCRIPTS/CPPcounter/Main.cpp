#include <iostream>
#include <thread>
#include <chrono>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: ./main <number>" << std::endl;
        return 1;
    }

    try {
        int count = std::stoi(argv[1]);

        if (count < 0) {
            std::cout << "Please provide a non-negative number." << std::endl;
            return 0;
        }

        while (count >= 0) {
            std::cout << count << std::endl;

            if (count > 0) {
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }

            count--;
        }

        std::cout << "Countdown complete!" << std::endl;

    } catch (...) {
        std::cout << "Error: invalid number." << std::endl;
        return 1;
    }

    return 0;
}