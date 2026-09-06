# server/test_scheme.py

from app.services.scheme_selector import select_scheme

print(select_scheme(100000))
print(select_scheme(10000))
print(select_scheme(10000000))