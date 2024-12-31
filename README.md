# FuzzBenedict

A Python Benedict extension to include fuzzy logic for matching keys (using keypaths)

## Installation

```bash
pip install fuzzbenedict
```

## Usage

```python
from fuzzbenedict import FuzzBenedict

data = {
    "person": {
        "name": "John Doe",
        "address": {
            "city": "New York",
            "zipcode": 10001
        }
    }
}

fb = FuzzBenedict(data)
print(fb.fuzzy_get("pers.name"))  # Test fuzzy match
```

You can also set a custom threshold for the fuzzy matching:

```python
fb = FuzzBenedict(data, threshold=90)
print(fb.fuzzy_get("pers.name"))  # Test fuzzy match
```

Or adjust the threshold at runtime:

```python
fb = FuzzBenedict(data)
fb.threshold=90
print(fb.fuzzy_get("pers.name"))  # Test fuzzy match
```


And set a default factory if the key is not found/matched:

```python
fb = FuzzBenedict(data, default_factory=lambda: None)
print(fb.fuzzy_get("pers.name"))  # Test fuzzy match
```

You can also adjust the behavior of the class:

```python
FuzzBenedict.Config.fuzzy_in_getitem = True
print(fb["pers.name"])
```

## License

MIT

## Author

Christophe Druet - [christophe@stoachup.com](mailto:christophe@stoachup.com)

## Copyright

Copyright (c) 2024 Stoachup SRL - All rights reserved.

