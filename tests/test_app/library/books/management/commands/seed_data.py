"""
Management command to seed the database with sample data for testing the jazzmin admin interface.

Usage:
    python manage.py seed_data                    # Default amounts
    python manage.py seed_data --small            # Small dataset
    python manage.py seed_data --large            # Large dataset
    python manage.py seed_data --authors 20       # Custom amounts
"""

from random import choice, randint, sample

from django.contrib.auth.models import Group, User
from django.core.management import BaseCommand
from django.db import transaction

from ....factories import (
    AuthorFactory,
    BookFactory,
    BookLoanFactory,
    GenreFactory,
    GroupFactory,
    LibraryFactory,
    UserFactory,
)
from ....loans.models import BookLoan, Library
from ...models import Author, Book, Genre


class Command(BaseCommand):
    """
    Seed the database with sample data for testing.
    """

    help = "Seed the database with sample library data"

    def add_arguments(self, parser):
        # Preset sizes
        parser.add_argument(
            "--small",
            action="store_true",
            help="Create a small dataset (5 authors, 20 books)",
        )
        parser.add_argument(
            "--large",
            action="store_true",
            help="Create a large dataset (50 authors, 200 books)",
        )

        # Custom amounts
        parser.add_argument(
            "--libraries",
            type=int,
            default=None,
            help="Number of libraries to create",
        )
        parser.add_argument(
            "--authors",
            type=int,
            default=None,
            help="Number of authors to create",
        )
        parser.add_argument(
            "--books-per-author",
            type=int,
            default=None,
            help="Number of books per author",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=None,
            help="Number of regular users to create",
        )
        parser.add_argument(
            "--groups",
            type=int,
            default=None,
            help="Number of groups to create",
        )
        parser.add_argument(
            "--genres",
            type=int,
            default=None,
            help="Number of genres to create",
        )

        # Options
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing data before seeding",
        )
        parser.add_argument(
            "--no-superuser",
            action="store_true",
            help="Don't create test superuser",
        )

    def handle(self, *args, **options):
        # Determine dataset size
        if options["small"]:
            libraries = 1
            authors = 5
            books_per_author = 4
            users = 3
            groups = 3
            genres = 8
        elif options["large"]:
            libraries = 5
            authors = 50
            books_per_author = 4
            users = 20
            groups = 10
            genres = 25
        else:
            # Default medium size
            libraries = 2
            authors = 15
            books_per_author = 5
            users = 5
            groups = 5
            genres = 15

        # Override with custom values if provided
        libraries = options.get("libraries") or libraries
        authors = options.get("authors") or authors
        books_per_author = options.get("books_per_author") or books_per_author
        users = options.get("users") or users
        groups = options.get("groups") or groups
        genres = options.get("genres") or genres

        # Clear existing data if requested
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            with transaction.atomic():
                for Model in [Group, User, Library, Author, Book, BookLoan, Genre]:
                    count = Model.objects.count()
                    Model.objects.all().delete()
                    self.stdout.write(f"  Deleted {count} {Model._meta.verbose_name_plural}")

        # Start seeding
        self.stdout.write(self.style.SUCCESS("\nSeeding database with sample data...\n"))

        with transaction.atomic():
            # Create superuser
            if not options["no_superuser"]:
                if not User.objects.filter(username="test@test.com").exists():
                    superuser = UserFactory(
                        username="test@test.com",
                        email="test@test.com",
                        password="test",
                        is_superuser=True,
                        is_staff=True,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created superuser: {superuser.username} (password: test)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("  Superuser 'test@test.com' already exists")
                    )

            # Create genres
            self.stdout.write(f"\nCreating {genres} genres...")
            genre_names = [
                "Science Fiction",
                "Fantasy",
                "Mystery",
                "Thriller",
                "Romance",
                "Historical Fiction",
                "Horror",
                "Biography",
                "Self-Help",
                "Business",
                "Cooking",
                "Travel",
                "Young Adult",
                "Children's",
                "Poetry",
                "Drama",
                "Comedy",
                "Adventure",
                "Crime",
                "Non-Fiction",
                "Philosophy",
                "Psychology",
                "History",
                "Science",
                "Technology",
            ]

            created_genres = []
            for i in range(min(genres, len(genre_names))):
                genre, created = Genre.objects.get_or_create(name=genre_names[i])
                created_genres.append(genre)
                if created:
                    self.stdout.write(f"  ✓ {genre.name}")

            # Fill remaining with random names if needed
            if genres > len(genre_names):
                for _ in range(genres - len(genre_names)):
                    genre = GenreFactory()
                    created_genres.append(genre)
                    self.stdout.write(f"  ✓ {genre.name}")

            # Create groups
            self.stdout.write(f"\nCreating {groups} groups...")
            created_groups = GroupFactory.create_batch(groups)
            for group in created_groups:
                self.stdout.write(f"  ✓ {group.name}")

            # Create users
            self.stdout.write(f"\nCreating {users} users...")
            created_users = []
            for i in range(users):
                user = UserFactory(is_staff=i < users // 2)  # Half are staff
                created_users.append(user)
                # Assign random groups
                user.groups.set(sample(created_groups, k=randint(0, min(3, len(created_groups)))))
                self.stdout.write(
                    f"  ✓ {user.username} ({'staff' if user.is_staff else 'user'})"
                )

            # Create libraries
            self.stdout.write(f"\nCreating {libraries} libraries...")
            created_libraries = []
            for _ in range(libraries):
                library = LibraryFactory()
                created_libraries.append(library)
                self.stdout.write(f"  ✓ {library.name} at {library.address}")

            # Create authors and books
            self.stdout.write(f"\nCreating {authors} authors with {books_per_author} books each...")
            total_books = 0
            total_loans = 0

            for i, author in enumerate(AuthorFactory.create_batch(authors), 1):
                self.stdout.write(f"  Author {i}/{authors}: {author}")

                # Create books for this author
                for j in range(books_per_author):
                    library = choice(created_libraries)
                    book = BookFactory(author=author, library=library)

                    # Assign random genres
                    book.genre.set(sample(created_genres, k=randint(1, min(3, len(created_genres)))))

                    total_books += 1

                    # Create random book loans (70% of books have loans)
                    if randint(1, 100) <= 70:
                        borrower = choice(created_users) if created_users else None
                        loan = BookLoanFactory(book=book, borrower=borrower)
                        total_loans += 1

            self.stdout.write(self.style.SUCCESS(f"\n✓ Created {total_books} books"))
            self.stdout.write(self.style.SUCCESS(f"✓ Created {total_loans} book loans"))

        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        self.stdout.write("\nData Summary:")
        self.stdout.write(f"  Libraries:  {Library.objects.count()}")
        self.stdout.write(f"  Authors:    {Author.objects.count()}")
        self.stdout.write(f"  Books:      {Book.objects.count()}")
        self.stdout.write(f"  Genres:     {Genre.objects.count()}")
        self.stdout.write(f"  Book Loans: {BookLoan.objects.count()}")
        self.stdout.write(f"  Users:      {User.objects.count()}")
        self.stdout.write(f"  Groups:     {Group.objects.count()}")

        if not options["no_superuser"]:
            self.stdout.write(self.style.SUCCESS("\nLogin credentials:"))
            self.stdout.write(self.style.SUCCESS("  URL:      http://localhost:8000/admin/"))
            self.stdout.write(self.style.SUCCESS("  Username: test@test.com"))
            self.stdout.write(self.style.SUCCESS("  Password: test"))

        self.stdout.write(self.style.SUCCESS("\nRun 'make test_app' to start the test server!"))
        self.stdout.write("")
