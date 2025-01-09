from persistent import Persistent
from ZODB import FileStorage, DB
import transaction
from datetime import datetime, timedelta

# Base User Class
class User(Persistent):
    def __init__(self, userId, name, email, phone, address):
        self.userId = userId
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

    def register(self, library):
        library.add_user(self)
        transaction.commit()
        print(f"User {self.name} registered.")

    def isLibrarian(self):
        return isinstance(self, Librarian)

    def login(self, userId, library):
        user = next((user for user in library.users if user.userId == userId), None)
        if user:
            print(f"Welcome, {user.name}!")
            return user
        else:
            print("Invalid User ID.")
            return None


# Librarian Class
class Librarian(User):
    def __init__(self, userId, name, email, phone, address, employeeId):
        super().__init__(userId, name, email, phone, address)
        self.employeeId = employeeId

    def addBook(self, library, book):
        library.add_book(book)
        transaction.commit()
        print(f"Book '{book.title}' added.")

    def removeBook(self, library, book):
        library.books.remove(book)
        transaction.commit()
        print(f"Book '{book.title}' removed.")

    def updateBook(self, library, book, **kwargs):
        for key, value in kwargs.items():
            setattr(book, key, value)
        transaction.commit()
        print(f"Book '{book.title}' updated.")

    def manageAccounts(self, library):
        print("Managing accounts...")
        for user in library.users:
            print(f"{user.name} (ID: {user.userId})")

    def viewMembers(self, library):
        print("\nList of all Members:")
        members = [user for user in library.users if isinstance(user, Member)]
        if members:
            for member in members:
                print(f"{member.name} (ID: {member.userId}, Member ID: {member.memberId})")
                # Show loans for each member
                member.viewLoans(library)
        else:
            print("No members found.")

    def viewAllBooks(self, library):
        print("\nList of all Books in the Library:")
        if library.books:
            for book in library.books:
                print(f"Title: {book.title}, Author: {book.author}, Status: {book.status}")
        else:
            print("No books found.")


# Member Class
class Member(User):
    def __init__(self, userId, name, email, phone, address, memberId):
        super().__init__(userId, name, email, phone, address)
        self.memberId = memberId

    def borrowBook(self, library, bookItem):
        if bookItem.isAvailable():
            loan = Loan(len(library.loans) + 1, bookItem, self, datetime.now(), datetime.now() + timedelta(days=14))
            library.loans.append(loan)
            bookItem.status = "loaned"
            transaction.commit()
            print(f"Book '{bookItem.title}' borrowed by {self.name}.")
        else:
            print(f"Book '{bookItem.title}' is not available.")

    def returnBook(self, library, bookItem):
        loan = next((loan for loan in library.loans if loan.bookItem == bookItem and loan.member == self), None)
        if loan:
            library.loans.remove(loan)
            bookItem.status = "available"
            transaction.commit()
            print(f"Book '{bookItem.title}' returned by {self.name}.")
        else:
            print(f"No active loan found for Book '{bookItem.title}'.")

    def reserveBook(self, library, book):
        if book.status == "available":
            book.status = "reserved"
            transaction.commit()
            print(f"Book '{book.title}' reserved by {self.name}.")
        else:
            print(f"Book '{book.title}' cannot be reserved.")

    def viewAllBooks(self, library):
        print("\nList of all Books in the Library:")
        if library.books:
            for book in library.books:
                print(f"Title: {book.title}, Author: {book.author}, Status: {book.status}")
        else:
            print("No books found.")
    
    def viewLoans(self, library):
        print(f"Loans for {self.name}:")
        loans = [loan for loan in library.loans if loan.member == self]
        if loans:
            for loan in loans:
                print(f"Loan ID: {loan.loanId}, Book: {loan.bookItem.barcode}, Borrowed on: {loan.borrowDate}, Due date: {loan.returnDate}")
        else:
            print("No active loans.")


# Loan Class
class Loan(Persistent):
    def __init__(self, loanId, bookItem, member, borrowDate, returnDate):
        self.loanId = loanId
        self.bookItem = bookItem
        self.member = member
        self.borrowDate = borrowDate
        self.returnDate = returnDate

    def calculateFine(self):
        overdue_days = max(0, (datetime.now() - self.returnDate).days)
        return overdue_days * 200  # Fine is 200 da per overdue day


# Book and BookItem Classes
class Book(Persistent):
    def __init__(self, bookId, title, author, publisher, ISBN, status="available"):
        self.bookId = bookId
        self.title = title
        self.author = author
        self.publisher = publisher
        self.ISBN = ISBN
        self.status = status

    def checkAvailability(self):
        return self.status == "available"


class BookItem(Persistent):
    def __init__(self, title, barcode, dueDate, location, status="available"):
        self.title = title
        self.barcode = barcode
        self.dueDate = dueDate
        self.location = location
        self.status = status

    def isAvailable(self):
        return self.status == "available"


# Library and Catalog
class Library(Persistent):
    def __init__(self):
        self.users = []
        self.books = []
        self.loans = []

    def add_user(self, user):
        self.users.append(user)
        self._p_changed = True

    def add_book(self, book):
        self.books.append(book)
        self._p_changed = True


class Catalog(Persistent):
    def searchByTitle(self, library, title):
        return [book for book in library.books if book.title.lower() == title.lower()]

    def searchByAuthor(self, library, author):
        return [book for book in library.books if book.author.lower() == author.lower()]

    def searchByPublisher(self, library, publisher):
        return [book for book in library.books if book.publisher.lower() == publisher.lower()]


# Main Script
def create_user(library, user_type):
    print(f"Enter {user_type} details:")
    userId = input("User ID: ")
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    address = input("Address: ")

    if user_type == "Librarian":
        employeeId = input("Employee ID: ")
        librarian = Librarian(userId, name, email, phone, address, employeeId)
        librarian.register(library)
        print(f"Librarian {name} registered.")
        return librarian
    elif user_type == "Member":
        memberId = input("Member ID: ")
        member = Member(userId, name, email, phone, address, memberId)
        member.register(library)
        print(f"Member {name} registered.")
        return member


def create_book(library):
    print("Enter Book details:")
    bookId = input("Book ID: ")
    title = input("Title: ")
    author = input("Author: ")
    publisher = input("Publisher: ")
    ISBN = input("ISBN: ")

    book = Book(bookId, title, author, publisher, ISBN)
    library.add_book(book)
    print(f"Book '{title}' added to the library.")


def main():
    # Initialize ZODB
    storage = FileStorage.FileStorage("library.fs")
    db = DB(storage)
    connection = db.open()
    root = connection.root()

    if not hasattr(root, "library"):
        root.library = Library()
        transaction.commit()

    library = root.library

    while True:
        print("\nLibrary Management System")
        print("1. Register Librarian")
        print("2. Register Member")
        print("3. Add Book")
        print("4. Search Book")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. View All Members (Librarian Only)")
        print("8. View All Books (Librarian or Member)")
        print("9. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            create_user(library, "Librarian")
        elif choice == '2':
            create_user(library, "Member")
        elif choice == '3':
            create_book(library)
        elif choice == '4':
            catalog = Catalog()
            title = input("Enter book title to search: ")
            books = catalog.searchByTitle(library, title)
            if books:
                for book in books:
                    print(f"Found Book: {book.title}")
            else:
                print("Book not found.")
        elif choice == '5':
            member_id = input("Enter your member ID: ")
            member = next((m for m in library.users if isinstance(m, Member) and m.userId == member_id), None)
            if member:
                barcode = input("Enter book barcode to borrow: ")
                book_item = next((item for item in library.books if item.barcode == barcode and item.isAvailable()), None)
                if book_item:
                    member.borrowBook(library, book_item)
                else:
                    print("Book not available.")
        elif choice == '6':
            member_id = input("Enter your member ID: ")
            member = next((m for m in library.users if isinstance(m, Member) and m.userId == member_id), None)
            if member:
                barcode = input("Enter book barcode to return: ")
                book_item = next((item for item in library.books if item.barcode == barcode), None)
                if book_item:
                    member.returnBook(library, book_item)
                else:
                    print("Book not found.")
        elif choice == '7':
            librarian_id = input("Enter your librarian ID: ")
            librarian = next((l for l in library.users if isinstance(l, Librarian) and l.userId == librarian_id), None)
            if librarian:
                librarian.viewMembers(library)
            else:
                print("Librarian not found or invalid ID.")
        elif choice == '8':
            role = input("Enter your role (Librarian/Member): ").lower()
            if role == "librarian":
                librarian_id = input("Enter your librarian ID: ")
                librarian = next((l for l in library.users if isinstance(l, Librarian) and l.userId == librarian_id), None)
                if librarian:
                    librarian.viewAllBooks(library)
                else:
                    print("Librarian not found.")
            elif role == "member":
                member_id = input("Enter your member ID: ")
                member = next((m for m in library.users if isinstance(m, Member) and m.userId == member_id), None)
                if member:
                    member.viewAllBooks(library)
                else:
                    print("Member not found.")
            else:
                print("Invalid role.")
        elif choice == '9':
            print("Get a better read on the world.")
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    # Close DB
    connection.close()
    db.close()


if __name__ == "__main__":
    main()
