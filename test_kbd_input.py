# test_input.py
while True:
    choice = input("Enter a number between 1 and 9 to zoom in, 0 to zoom out, or q to exit: ")
    if choice == 'q':
        print("Exiting...")
        break
    elif choice == '0':
        print("Zooming out to view all plots...")
    elif choice.isdigit() and 1 <= int(choice) <= 9:
        print(f"Zooming in to view plot {choice}...")
    else:
        print("Invalid input. Please enter a number between 0 and 9.")