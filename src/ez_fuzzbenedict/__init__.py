#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Christophe Druet'
__copyright__ = 'Copyright (c) 2024 Stoachup SRL - All rights reserved.'
__credits__ = ['Christophe Druet']
__license__ = 'MIT'
__version__ = '0.1.1'
__maintainer__ = 'Christophe Druet'
__email__ = 'christophe@stoachup.com'
__status__ = 'Dev'

from functools import lru_cache
from typing import Callable, Hashable, List, Optional, Tuple
from rapidfuzz import process, utils
from benedict import benedict

KeyPath = str
KeyList = List[str] | Tuple[str]
Key = KeyPath | KeyList


class FuzzBenedict(benedict):
    """
    A subclass of benedict that adds fuzzy matching capabilities for key retrieval.
    
    Attributes:
        default_factory (Optional[Callable]): A callable to generate default values if a key is not found.
        _threshold (int): The minimum similarity score for fuzzy matches.
    """
    
    class Config:
        """
        Configuration class for FuzzBenedict.
        
        Attributes:
            fuzzy_key_enabled (bool): If True, enables fuzzy matching in __getitem__.
            fuzzy_threshold (int): Minimum similarity score for fuzzy matches.
        """
        fuzzy_key_enabled = False  # If True, fuzzy matching is embedded in __getitem__
        fuzzy_threshold = 75      # Minimum similarity score for fuzzy matches

    def __init__(self, 
                 *args, 
                 default_factory: Optional[Callable] = None, 
                 threshold: Optional[int] = None, 
                 **kwargs):
        """
        Initializes the FuzzBenedict instance.
        
        Args:
            *args: Positional arguments passed to the parent benedict class.
            default_factory (Optional[Callable]): A callable to generate default values if a key is not found.
            threshold (Optional[int]): The threshold for fuzzy matching.
            **kwargs: Keyword arguments passed to the parent benedict class.
        """
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory
        self.Config.fuzzy_threshold = threshold or self.Config.fuzzy_threshold

    def __hash__(self):
        """
        Returns a hash value for the FuzzBenedict instance.
        
        Returns:
            int: The hash value based on the internal dictionary.
        """
        return hash(frozenset(self.items()))  # Use frozenset to make it hashable

    def __eq__(self, other):
        """
        Compares this FuzzBenedict instance with another for equality.
        
        Args:
            other (object): The other object to compare.
        
        Returns:
            bool: True if equal, False otherwise.
        """
        if not isinstance(other, FuzzBenedict):
            return NotImplemented
        return dict(self) == dict(other)  # Compare the internal dictionaries
        
    @property
    def threshold(self):
        """
        Gets the current threshold for fuzzy matching.
        
        Returns:
            int: The current threshold value.
        """
        return self.Config.fuzzy_threshold

    @threshold.setter
    def threshold(self, value):
        """
        Sets the threshold for fuzzy matching.
        
        Args:
            value (int): The new threshold value.
        """
        self.Config.fuzzy_threshold = value

    @property
    def fuzzy_key_enabled(self):
        """
        Gets the current fuzzy keypath enabled status.
        
        Returns:
            bool: The current fuzzy keypath enabled status.
        """
        return self.Config.fuzzy_key_enabled
    
    @fuzzy_key_enabled.setter
    def fuzzy_key_enabled(self, value):
        """
        Sets the fuzzy keypath enabled status.
        
        Args:
            value (bool): The new fuzzy keypath enabled status.
        """
        self.Config.fuzzy_key_enabled = value

    def __getitem__(self, key: Key):
        """
        Retrieves an item by key, with optional fuzzy matching.
        
        Args:
            key (Key): The key to retrieve.
        
        Returns:
            The value associated with the key, or a default value if not found.
        
        Raises:
            KeyError: If the key is not found and no default factory is set.
        """
        if self.fuzzy_key_enabled:
            # Fuzzy matching embedded in __getitem__
            return self.fuzzy_get(key)
        try:
            return super().__getitem__(key)  # Exact keypath behavior
        except KeyError:
            if self.default_factory is not None:
                return self.default_factory()
            raise  # Re-raise the KeyError if default_factory is not set

    def fuzzy_get(self, key: Key, with_threshold: Optional[int] = None):
        """
        Explicit fuzzy matching method to retrieve an item by key.
        
        Args:
            key (Key): The key to retrieve.
            with_threshold (Optional[int]): An optional threshold for this specific retrieval.
        
        Returns:
            The value associated with the closest match to the key.
        """
        return self._get_with_fuzzy_matching(key, threshold=with_threshold or self.threshold)

    def _get_with_fuzzy_matching(self, key: Key, threshold: int):
        """
        Performs fuzzy matching on the key path and returns the closest match.
        
        Args:
            key (Key): The key to retrieve.
            threshold (int): The threshold for fuzzy matching.
        
        Returns:
            The value associated with the closest match to the key.
        
        Raises:
            KeyError: If no match is found and no default factory is set.
        """
        if key in self:
            return super().__getitem__(key)

        # Fuzzy match the key
        if isinstance(key, list):
            key = tuple(key)
        closest_key_path = self._get_closest_key_path(key, threshold=threshold)
        if closest_key_path is not None:
            return super().__getitem__(closest_key_path)
        elif self.default_factory is not None:
            return self.default_factory()
        else:
            raise KeyError(f"No exact or approximate match found for key path: {key}")

    # @lru_cache(maxsize=128)
    def _get_closest_key_path(self, query: str | Tuple[str], threshold: int):
        """
        Fuzzy match a key path by splitting it into parts and finding the closest matches.
        
        Args:
            query (Hashable): The key to match.
            threshold (int): The threshold for fuzzy matching.
        
        Returns:
            str: The closest matching key path, or None if no match is found.
        """
        if isinstance(query, str):
            parts = query.split(self.keypath_separator)
        elif isinstance(query, tuple):
            parts = list(query)
        else:
            raise TypeError(f"Query ({query}) must be a string or a tuple ({type(query)}).")

        current_dict = self
        matched_parts = []

        for part in parts:
            if not isinstance(current_dict, dict): # pragma: no cover
                return None
            keys = [ str(k) for k in current_dict.keys() ]
            match, score, _ = process.extractOne(part, keys, processor=utils.default_process)
            if score < threshold:
                return None  # No match above threshold
            matched_parts.append(match)
            current_dict = current_dict[match]

        return ".".join(matched_parts)


if __name__ == "__main__": # pragma: no cover
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
