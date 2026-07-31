from creator_toolkit.tag_generator import generate_tags
from creator_toolkit.title_generator import generate_title
from creator_toolkit.rename_images import rename_images

def main():
    print("Creator Toolkit CLI")
    print("1. Generate title")
    print("2. Generate tags")
    print("3. Rename images")
    choice = input("Choose an option: ")

    if choice == "1":
        keyword = input("Enter keyword: ")
        print(generate_title(keyword))

    elif choice == "2":
        print(generate_tags())
    elif choice == "3":
        folder = input("Enter folder path: ")
        rename_images(folder)
    else:
        print("Invalid option")


if __name__ == "__main__":
    main()