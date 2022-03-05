from Python.Brave import Brave

menu = """
1) Start BraveBatBot
2) Configure
3) Exit"""


if __name__ == "__main__":

    myBrave = Brave(True)
    while True:
        print(menu)
        choice = input("Enter your choice: ")
        if choice == "1":
            myBrave.start_brave_bat_bot()
        elif choice == "2":
            myBrave.configure()
        elif choice == "3":
            break
        else:
            print("Invalid choice")