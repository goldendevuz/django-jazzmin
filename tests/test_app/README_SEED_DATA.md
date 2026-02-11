# Seeding Sample Data for Testing

The test app includes a comprehensive data seeding command to populate the database with realistic library data for testing the jazzmin admin interface.

## Quick Start

### Using Make (Recommended)

```bash
# Seed with default (medium) dataset
make seed_data

# Seed with small dataset (fast, for quick testing)
make seed_small

# Seed with large dataset (comprehensive testing)
make seed_large
```

### Using Django Management Command

```bash
# Default medium dataset
uv run python tests/test_app/manage.py seed_data --clear

# Small dataset (5 authors, 20 books)
uv run python tests/test_app/manage.py seed_data --small --clear

# Large dataset (50 authors, 200 books)
uv run python tests/test_app/manage.py seed_data --large --clear

# Custom amounts
uv run python tests/test_app/manage.py seed_data \
    --authors 25 \
    --books-per-author 3 \
    --users 10 \
    --clear
```

## Dataset Sizes

### Small (`--small`)
- 1 library
- 5 authors
- 20 books (4 per author)
- 8 genres
- 3 users
- 3 groups
- ~16 book loans

**Use for:** Quick testing, development

### Medium (default)
- 2 libraries
- 15 authors
- 75 books (5 per author)
- 15 genres
- 5 users
- 5 groups
- ~52 book loans

**Use for:** General testing, screenshots, demos

### Large (`--large`)
- 5 libraries
- 50 authors
- 200 books (4 per author)
- 25 genres
- 20 users
- 10 groups
- ~140 book loans

**Use for:** Performance testing, pagination, search

## Command Options

### Preset Sizes
- `--small` - Create small dataset
- `--large` - Create large dataset

### Custom Amounts
- `--libraries N` - Number of libraries
- `--authors N` - Number of authors
- `--books-per-author N` - Books per author
- `--users N` - Number of regular users
- `--groups N` - Number of user groups
- `--genres N` - Number of book genres

### Options
- `--clear` - **Delete all existing data first** (recommended)
- `--no-superuser` - Don't create test superuser

## Generated Data

The command creates:

### Superuser (unless `--no-superuser`)
- **Username:** test@test.com
- **Password:** test
- **Email:** test@test.com
- **Permissions:** Full admin access

### Genres
Real book genres like:
- Science Fiction
- Fantasy
- Mystery
- Thriller
- Romance
- Historical Fiction
- And more...

### Authors
- Random names (using Faker)
- Realistic birth dates
- Some with death dates

### Books
- Random titles
- Assigned to authors and libraries
- 1-3 random genres per book
- ISBN numbers
- Publication dates
- Page counts
- Brief summaries

### Libraries
- Random company names
- Random addresses
- Each with a librarian (user)

### Users
- Random names and emails
- Half are staff, half are regular users
- Random group assignments
- Password: "test" for all

### Book Loans
- 70% of books have active loans
- Random borrowers
- Random loan status (Available, On loan, Reserved, Maintenance)
- Realistic due dates

## Examples

### Quick Test Setup
```bash
# Clear everything and create small dataset
make seed_small

# Start test server
make test_app

# Login at http://localhost:8000/admin/
# Username: test@test.com
# Password: test
```

### Performance Testing
```bash
# Create large dataset to test pagination, filters, search
make seed_large

# Or custom large dataset
uv run python tests/test_app/manage.py seed_data \
    --authors 100 \
    --books-per-author 5 \
    --users 50 \
    --clear
```

### Custom Scenario
```bash
# Create specific scenario: many authors, few books each
uv run python tests/test_app/manage.py seed_data \
    --libraries 3 \
    --authors 50 \
    --books-per-author 2 \
    --genres 30 \
    --users 15 \
    --groups 8 \
    --clear
```

### Add Data Without Clearing
```bash
# Add more data without deleting existing
uv run python tests/test_app/manage.py seed_data \
    --authors 10 \
    --books-per-author 3
# Note: No --clear flag
```

## What Gets Created

Example output from `make seed_small`:

```
Clearing existing data...
  Deleted 3 Groups
  Deleted 5 Users
  Deleted 1 Libraries
  Deleted 5 Authors
  Deleted 20 Books
  Deleted 16 Book Loans
  Deleted 8 Genres

Seeding database with sample data...

✓ Created superuser: test@test.com (password: test)

Creating 8 genres...
  ✓ Science Fiction
  ✓ Fantasy
  ✓ Mystery
  ...

Creating 3 groups...
  ✓ Biomedical engineer
  ✓ Museum/gallery conservator
  ✓ Minerals surveyor

Creating 3 users...
  ✓ David Lucas (staff)
  ✓ Theresa Lang (user)
  ✓ Megan Edwards (user)

Creating 1 libraries...
  ✓ Alvarez-Adams at USNS Moss, FPO AE 06849

Creating 5 authors with 4 books each...
  Author 1/5: Jared, Pierce
  Author 2/5: Gregory, Baker
  ...

✓ Created 20 books
✓ Created 16 book loans

============================================================
Database seeding complete!
============================================================

Data Summary:
  Libraries:  1
  Authors:    5
  Books:      20
  Genres:     8
  Book Loans: 16
  Users:      5
  Groups:     3

Login credentials:
  URL:      http://localhost:8000/admin/
  Username: test@test.com
  Password: test

Run 'make test_app' to start the test server!
```

## Testing the Bootstrap 5 Migration

After seeding data, you can thoroughly test the Bootstrap 5 migration:

1. **Seed data:**
   ```bash
   make seed_data
   ```

2. **Start test server:**
   ```bash
   make test_app
   ```

3. **Test pages with real data:**
   - Login page
   - Dashboard (shows recent actions)
   - Book list (pagination, sorting, filters)
   - Book detail (forms, related objects)
   - Author list and detail
   - User management
   - Group management

4. **Test features:**
   - Search functionality
   - Filters (genre, author, etc.)
   - Pagination (with large dataset)
   - Related object popups
   - Inline formsets (book loans)
   - Many-to-many widgets (genres)
   - Date/time widgets
   - Theme switcher
   - Dark/light mode

## Existing `reset` Command

There's also an existing `reset` command that does similar seeding:

```bash
uv run python tests/test_app/manage.py reset
```

**Differences:**
- `reset` - Simple, fixed amounts, less verbose
- `seed_data` - Configurable, verbose output, more options

Both are useful! Use `reset` for quick resets, `seed_data` for customizable scenarios.

## Troubleshooting

### "UNIQUE constraint failed"
Run with `--clear` to delete existing data first:
```bash
make seed_data  # Already includes --clear
```

### "No such table"
Run migrations first:
```bash
uv run python tests/test_app/manage.py migrate
make seed_data
```

### "Command not found"
Make sure you're in the project root and using uv:
```bash
cd /path/to/django-jazzmin
uv run python tests/test_app/manage.py seed_data --help
```

## Tips

1. **Always use `--clear`** when seeding to avoid duplicates
2. **Use `--small`** for quick iterations during development
3. **Use `--large`** when testing performance or pagination
4. **Customize amounts** for specific test scenarios
5. **Use Make commands** for convenience (`make seed_small`, etc.)

## Next Steps

After seeding data:
1. Start the test app: `make test_app`
2. Login with `test@test.com` / `test`
3. Follow `TESTING_GUIDE.md` for comprehensive testing
4. Test the Bootstrap 5 migration features!
