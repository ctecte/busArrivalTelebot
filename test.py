import shelve

with shelve.open('busDB') as db:
    print(db)
