import java.util.*;

public class LibraryManagementSystem {
    public static void main(String[] args) {
        // Create library management system
        LibraryManagementSystem system = new LibraryManagementSystem();

        // Create some books
        Book book1 = new Book("9751215115", "Information Tech", "Madhav publication", 1956);
        Book book2 = new Book("9746215484", "Profession ", "Literas_publication", 1970);
        Book book3 = new Book("9754687945", "Mind Sharp", "Sri Ram prasad", 2001);

        // Add books to the system
        system.addBook(book1);
        system.addBook(book2);
        system.addBook(book3);

        // Display all books
        system.displayAllBooks();

        // Create some members
        Member member1 = new Member("B001", "Rahul", "rahul976@example.com");
        Member member2 = new Member("B002", "Tanishq", "Tani@example.com");

        // Add members to the system
        system.addMember(member1);
        system.addMember(member2);

        // Display all members
        system.displayAllMembers();

        // Borrow books
        system.borrowBook(member1, book1);
        system.borrowBook(member1, book2);
        system.borrowBook(member2, book2);
        system.borrowBook(member2, book3);

        // Display borrowed books for each member
        system.displayBorrowedBooks(member1);
        system.displayBorrowedBooks(member2);

        // Return books
        system.returnBook(member1, book1);
        system.returnBook(member2, book3);

        // Display borrowed books for each member after returning
        system.displayBorrowedBooks(member1);
        system.displayBorrowedBooks(member2);
    }

    private List<Book> books;
    private List<Member> members;
    private Map<Member, List<Book>> borrowedBooks;

    public LibraryManagementSystem() {
        books = new ArrayList<>();
        members = new ArrayList<>();
        borrowedBooks = new HashMap<>();
    }

    public void addBook(Book book) {
        books.add(book);
    }

    public void addMember(Member member) {
        members.add(member);
    }

    public void borrowBook(Member member, Book book) {
        if (!books.contains(book)) {
            System.out.println("Error: Book not found in the library.");
            return;
        }
        if (!borrowedBooks.containsKey(member)) {
            borrowedBooks.put(member, new ArrayList<>());
        }
        borrowedBooks.get(member).add(book);
    }

    public void returnBook(Member member, Book book) {
        if (!borrowedBooks.containsKey(member) || !borrowedBooks.get(member).contains(book)) {
            System.out.println("Error: Book not borrowed by the member.");
            return;
        }
        borrowedBooks.get(member).remove(book);
    }

    public void displayAllBooks() {
        System.out.println("All Books:");
        for (Book book : books) {
            System.out.println(book);
        }
        System.out.println();
    }

    public void displayAllMembers() {
        System.out.println("All Members:");
        for (Member member : members) {
            System.out.println(member);
        }
    }
 public void displayBorrowedBooks(Member member) {
        System.out.println(member.getName() + "'s Borrowed Books:");
        List<Book> borrowed = borrowedBooks.getOrDefault(member, Collections.emptyList());
        for (Book book : borrowed) {
            System.out.println(book);
        }
        System.out.println();
    }
}

class Book {
    private String isbn;
    private String title;
    private String author;
    private int year;

    public Book(String isbn, String title, String author, int year) {
        this.isbn = isbn;
        this.title = title;
        this.author = author;
        this.year = year;
    }

    public String getIsbn() {
        return isbn;
    }

    public String getTitle() {
        return title;
    }

    public String getAuthor() {
        return author;
    }

    public int getYear() {
        return year;
    }

    @Override
    public String toString() {
        return "Book [ISBN=" + isbn + ", Title=" + title + ", Author=" + author + ", Year=" + year + "]";
    }
}

class Member {
    private String memberId;
    private String name;
    private String email;

    public Member(String memberId, String name, String email) {
        this.memberId = memberId;
        this.name = name;
        this.email = email;
    }

    public String getMemberId() {
        return memberId;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    @Override
    public String toString() {
        return "Member [ID=" + memberId + ", Name=" + name + ", Email=" + email + "]";
    }
}

