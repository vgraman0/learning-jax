# 2. Data Attributes

## 2.1 Attaching Data to Classes and Instances

1. *Class attributes*: A variable defined in the class body directly. The data is common to the class and all instances.
2. *Instance attributes*: A variable defined in an isntance method using the `self` argument and dot notation. Belong to a specific instance of a given class.

### Class attributes
```python
class ObjectCounter:
    num_instances = 0
    def __init__(self):
        type(self).num_instances += 1
```

Overriding the original class attribute by creating a new instance attribute.
```python
class ObjectCounter:
    num_instances = 0
    def __init__(self):
        self.num_instances += 1
```
- At initialization, it uses the class attribute value since self.num_instances doesn't exist yet (which is why it doesn't throw an `AttributeError`).

### Instance attributes

See `car.py`.

### `.__dict__` Attribute
Classes and instances have a special attribute called `.__dict__`. This holds the dictionary with the writable members of the underlying class.

```python
class SampleClass:
    class_attr = 100

    def __init__(self, instance_attr):
        self.instance_attr = instance+attr

    def method(self):
        print(f"Class attribute: {self.class_attr}")
        print(f"Instance attribute: {self.instance_attr}")
```

### Dynamic Class and Instance Attributes

Suppose you have data in a CSV file. This will have several that cannot be determined without reading the file.

We use the `setattr` function to add fields as an attribute to objects.

```python 
class Record:
    pass

john = {
    "name": "John Doe",
    "position": "Python Developer",
    "department": "Engineering",
    "salary": 80000,
    "hire_date": "2020-01-01",
    "is_manager": False,
}

john_record = Record()
for field, value in john.items():
    setattr(john_record, field, value)
```

