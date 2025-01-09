# Online Library Database Management System

This repository showcases an **Online Library Database Management System** built using an **Object-Oriented Database (OODB)** model, specifically implemented with **Zope Object Database (ZODB)**. The focus is on leveraging the strengths of OODBs to handle library resources and their relationships efficiently.

## Object-Oriented Database (OODB)

The project adopts an OODB approach to provide direct integration with object-oriented programming principles. Instead of traditional relational tables, data is modeled as interconnected objects, aligning closely with the structure of the library system. Key highlights include:

- **Object Representation**: Core entities such as `Book`, `User`, `Librarian`, and `Loan` are modeled as Python objects. Attributes and methods encapsulate their behavior, such as:
  - `Book`: Includes attributes like `bookId`, `title`, `author`, and a method `checkAvailability()`.
  - `User`: Attributes such as `userId` and `email`, with methods like `register()` and `login()`.
- **Direct Relationships**: Relationships between objects, such as `One-to-Many` (a user borrowing multiple books), are maintained via direct references, eliminating the need for foreign keys.

## Zope Object Database (ZODB)

### Key Features of ZODB in This Project
- **Native Integration**: ZODB allows Python objects to be stored and retrieved without conversion. Classes like `Book` and `User` inherit from `persistent.Persistent` to enable persistence.
- **Storage**: Data is stored in a `library.fs` file, accessed via ZODB’s root object. Operations like adding new objects or modifying existing ones are handled seamlessly.
- **Querying**: Instead of SQL or OQL, queries are performed using Python constructs like list comprehensions and filters. For example:
  ```python
  # Searching for a book by title
  [book for book in library.books if book.title == "Desired Title"]
