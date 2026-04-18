def check_number():
    # Ask the user for input
    user_choice = input("Please enter 1 or 2: ")

    # Check the input and print the corresponding message
    if user_choice == '1':
        print("nice")
    elif user_choice == '2':
        print("nice nice")
    else:
        print("sadly badly")

# --- Run the Script ---
if __name__ == "__main__":
    check_number()