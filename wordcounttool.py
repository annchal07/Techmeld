def count_words(text):
  
    words = text.split()
    return len(words)

def main():
    
    choice = input("Do you want to enter text (1) or read from a file (2)? ")

    if choice == '1':
        text = input("Enter your text: ")
    elif choice == '2':
        filename = input("Enter the filename: ")
        try:
            with open(filename, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("File not found. Please check the filename and try again.")
            return
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    
    word_count = count_words(text)
    print(f"The total number of words is: {word_count}")

if __name__ == "__main__":
    main()
