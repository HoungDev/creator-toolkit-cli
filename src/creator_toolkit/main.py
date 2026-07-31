from creator_toolkit.tag_generator import generate_tags
from creator_toolkit.title_generator import generate_title


def main():
    print("Creator Toolkit CLI")
    print("1. Generate title")
    print("2. Generate tags")

    choice = input("Choose an option: ")

    if choice == "1":
        keyword = input("Enter keyword: ")
        print(generate_title(keyword))

    elif choice == "2":
        print(generate_tags())

    else:
        print("Invalid option")


if __name__ == "__main__":
    main()