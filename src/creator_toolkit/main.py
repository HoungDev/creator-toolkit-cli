from creator_toolkit.title_generator import generate_title


def main():
    keyword = input("Enter keyword: ")
    print()
    print(generate_title(keyword))


if __name__ == "__main__":
    main()