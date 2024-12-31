import pytest
from ez_fuzzbenedict import FuzzBenedict


def test_basic_exact_matching():
    """Test basic exact key matching behavior"""
    d = FuzzBenedict({'hello': 'world'})
    assert d['hello'] == 'world'
    assert d.get('hello') == 'world'

def test_nested_exact_matching():
    """Test nested dictionary exact matching"""
    d = FuzzBenedict({
        'user': {
            'personal_info': {
                'first_name': 'John',
                'last_name': 'Doe'
            }
        }
    })
    assert d['user.personal_info.first_name'] == 'John'
    assert d[['user', 'personal_info', 'first_name']] == 'John'

def test_fuzzy_matching_basic():
    """Test basic fuzzy matching"""
    d = FuzzBenedict({'hello': 'world'})
    assert d.fuzzy_get('helo') == 'world'
    assert d.fuzzy_get('hell') == 'world'

def test_fuzzy_matching_nested():
    """Test fuzzy matching with nested dictionaries"""
    d = FuzzBenedict({
        'user': {
            'personal_info': {
                'first_name': 'John',
                'last_name': 'Doe'
            }
        }
    })
    assert d.fuzzy_get('user.persnal_info.first_name') == 'John'
    assert d.fuzzy_get('user.personal_info.firstname') == 'John'

def test_fuzzy_threshold():
    """Test threshold settings"""
    d = FuzzBenedict({'temperature': 25})
    
    # Default threshold (75)
    assert d.fuzzy_get('temp') == 25
    
    # Modify threshold
    d.threshold = 95
    with pytest.raises(KeyError):
        d.fuzzy_get('tem')
    
    # Reset threshold
    d.threshold = 75

def test_fuzzy_in_getitem():
    """Test the fuzzy_in_getitem configuration"""
    d = FuzzBenedict({'temperature': 25})
    
    # Default behavior (fuzzy_key_enabled = False)
    with pytest.raises(KeyError):
        d['temp']
    
    # Enable fuzzy matching in __getitem__
    d.Config.fuzzy_key_enabled = True
    assert d['temp'] == 25
    
    # Reset configuration
    d.Config.fuzzy_key_enabled = False

def test_no_match_behavior():
    """Test behavior when no match is found"""
    d = FuzzBenedict({'specific_key': 'value'})
    
    # Should raise KeyError when no match and no default_factory
    with pytest.raises(KeyError):
        d.fuzzy_get('completely_different')

def test_multiple_similar_keys():
    """Test behavior with multiple similar keys"""
    d = FuzzBenedict({
        'temperature': 25,
        'temporal': 'time',
        'temporary': 'not permanent'
    })
    
    # Should match the closest one
    assert d.fuzzy_get('temp') == 25
    assert d.fuzzy_get(['temp']) == 25

def test_case_sensitivity():
    """Test case sensitivity in matching"""
    d = FuzzBenedict({'Temperature': 25})
    assert d.fuzzy_get('temperature') == 25
    assert d.fuzzy_get('TEMPERATURE') == 25

def test_empty_dictionary():
    """Test behavior with empty dictionary"""
    d = FuzzBenedict({})
    
    with pytest.raises(KeyError):
        d.fuzzy_get('any_key')

def test_non_hashable_keys():
    """Test behavior with non-hashable keys"""
    d = FuzzBenedict({
        42: 'number',
        True: 'boolean'
    })
    
    # Should work with exact matches
    assert d[42] == 'number'
    assert d[True] == 'boolean'
    
    # Should raise TypeError for fuzzy matching on non-hashable keys
    with pytest.raises(TypeError):
        d.fuzzy_get([42, 34]) 

    with pytest.raises(TypeError):
        d.fuzzy_get({'data': 'value'})

def test_fuzzy_key_enabled():
    """Test fuzzy_key_enabled property"""
    d = FuzzBenedict({'existing': 'value'}, default_factory=lambda: 'non-existent')
    assert d.fuzzy_key_enabled is False
    
    d.fuzzy_key_enabled = True
    assert d.fuzzy_key_enabled is True
    assert d.fuzzy_get('exist') == 'value'
    assert d['exist'] == 'value'

    d.fuzzy_key_enabled = False
    assert d.fuzzy_key_enabled is False
    assert d.fuzzy_get('exist') == 'value'
    assert d['exist'] == 'non-existent'

def test_default_factory_various_types():
    """Test default_factory with various return types"""
    d = FuzzBenedict({'existing': 'value'}, default_factory=lambda: 42)
    
    assert d.fuzzy_get('existing') == 'value'
    assert d.fuzzy_get('non_existent') == 42  # Returns integer

    d2 = FuzzBenedict({'existing': 'value'}, default_factory=lambda: 'default string')
    assert d2.fuzzy_get('non_existent') == 'default string'  # Returns string

def test_default_factory_raises_exception():
    """Test default_factory that raises an exception"""
    d = FuzzBenedict({'existing': 'value'}, default_factory=lambda: 1 / 0)  # Will raise ZeroDivisionError
    
    assert d.fuzzy_get('existing') == 'value'
    with pytest.raises(ZeroDivisionError):
        d.fuzzy_get('non_existent')

def test_no_default_factory():
    """Test behavior when no default_factory is set"""
    d = FuzzBenedict({'existing': 'value'})
    
    assert d.fuzzy_get('existing') == 'value'
    with pytest.raises(KeyError):
        d.fuzzy_get('non_existent')

def test_complex_default_factory():
    """Test default_factory that returns a complex object"""
    d = FuzzBenedict({'existing': 'value'}, default_factory=lambda: {'key': 'default_value'})
    
    assert d.fuzzy_get('existing') == 'value'
    assert d.fuzzy_get('non_existent') == {'key': 'default_value'}  # Returns a dictionary 

def test_fuzzbenedict_eq_not_implemented():
    fb1 = FuzzBenedict({"key": "value"})
    non_fuzzbenedict_obj = {"key": "value"}  # A regular dictionary

    result = fb1.__eq__(non_fuzzbenedict_obj)
    assert result is NotImplemented  # Check that the result is NotImplemented

def test_fuzzbenedict_hash():
    data1 = {
        "person": {
            "name": "John Doe",
            "address": {
                "city": "New York",
                "zipcode": 10001
            }
        }
    }
    data2 = {
        "person": {
            "name": "John Doe",
            "address": {
                "city": "New York",
                "zipcode": 10001
            }
        }
    }
    
    fb1 = FuzzBenedict(data1)
    fb2 = FuzzBenedict(data2)
    
    # Test that the hash of the same instance is consistent
    assert hash(fb1) == hash(fb1)
    
    # Test that two different instances with the same content have the same hash
    assert hash(fb1) == hash(fb2)

    # Test that eq works too
    assert fb1 == fb2

    # Test that the hash changes when the content changes
    fb1["person"]["name"] = "Jane Doe"
    assert hash(fb1) != hash(fb2)



@pytest.fixture
def setup_fuzzbenedict():
    data = {
        "person": {
            "name": "John Doe",
            "address": {
                "city": "New York",
                "zipcode": 10001
            }
        },
        "people": {
            "name": "Jane Doe",
            "address": {
                "city": "Los Angeles",
                "zipcode": 90001
            }
        }
    }
    return FuzzBenedict(data)

def test_exact_match(setup_fuzzbenedict):
    fb = setup_fuzzbenedict
    result = fb._get_closest_key_path("person.name", threshold=75)
    assert result == "person.name"

def test_fuzzy_match(setup_fuzzbenedict):
    fb = setup_fuzzbenedict
    result = fb._get_closest_key_path("persn.name", threshold=75)
    assert result == "person.name"

def test_no_match_below_threshold(setup_fuzzbenedict):
    fb = setup_fuzzbenedict
    result = fb._get_closest_key_path("persn.name", threshold=99)
    assert result is None

def test_partial_match(setup_fuzzbenedict):
    fb = setup_fuzzbenedict
    result = fb._get_closest_key_path("person.addr", threshold=75)
    assert result == "person.address"

def test_nonexistent_key(setup_fuzzbenedict):
    fb = setup_fuzzbenedict
    result = fb._get_closest_key_path("nonexistent.key", threshold=75)
    assert result is None

def test_invalid_query_type(setup_fuzzbenedict):
    fb = setup_fuzzbenedict
    with pytest.raises(TypeError):
        fb._get_closest_key_path(('person', 'address', 10001), threshold=75)

    with pytest.raises(TypeError):
        fb._get_closest_key_path(('people', 'address', 90001.5), threshold=75)

    with pytest.raises(TypeError):
        fb._get_closest_key_path([], threshold=75)

    with pytest.raises(TypeError):
        fb._get_closest_key_path(frozenset(), threshold=75)
