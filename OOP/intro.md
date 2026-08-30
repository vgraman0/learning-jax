# 1. Introduction to Object-Oriented Programming (OOP)

## 1.1 What is OOP in Python

- *Classes*: Define reusable pieces of code that encapsulate data and behavior in a single entity.

`.__init__()` (Object Initializer): defines and sets the initial values for the object's attributes.
```python
class Employee:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

> Note: Python class names are written in CapitalizedWords notation (PascalCase)

```python
# dog.py
class Dog:
    species = "canis familiaris"
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

