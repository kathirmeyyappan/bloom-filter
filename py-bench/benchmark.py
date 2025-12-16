#!/usr/bin/env python3
"""Benchmark comparing bloom_filter (Python) vs kathir_bloom_filter (Rust)."""

from kathir_bloom_filter import BloomFilter as KathirBloomFilter
from bloom_filter import BloomFilter
from rbloom import Bloom as RbloomFilter
from bloom_filter2 import BloomFilter as BloomFilter2
from pybloom_live import BloomFilter as PybloomFilter
from fastbloom_rs import BloomFilter as FastbloomFilter
import random
import string
import time

random.seed(42)


def generate_data(data_type: str, n: int, seed: int = 42):
    """Generate member and non-member data as a tuple. Guaranteed to be disjoint."""
    random.seed(seed)
    
    if data_type == "int":
        data = list(range(2 * n))
        member_data = random.sample(data, n)
        member_set = set(member_data)
        non_member_data = [item for item in data if item not in member_set]
        return member_data, non_member_data
    
    elif data_type == "string":
        all_strings = []
        for _ in range(2 * n):
            all_strings.append(''.join(random.choices(string.ascii_letters + string.digits, k=16)))
        member_data = random.sample(all_strings, n)
        member_set = set(member_data)
        non_member_data = [s for s in all_strings if s not in member_set]
        return member_data, non_member_data
    
    elif data_type == "tuple":
        all_tuples = []
        for _ in range(2 * n):
            tuple_length = random.randint(1, 5)
            tuple_elements = []
            for _ in range(tuple_length):
                if random.choice([True, False]):
                    tuple_elements.append(random.randint(0, 100))
                else:
                    tuple_elements.append(random.choice(string.ascii_letters))
            all_tuples.append(tuple(tuple_elements))
        member_data = random.sample(all_tuples, n)
        member_set = set(member_data)
        non_member_data = [t for t in all_tuples if t not in member_set]
        return member_data, non_member_data

    elif data_type == "mixed":
        # generate 2n distinct items, ~homogenous mix of the three types
        all_items = []
        for i in range(2 * n):
            item_type = random.choice(['int', 'string', 'tuple'])
            if item_type == 'int':
                item = i
            elif item_type == 'string':
                item = ''.join(random.choices(string.ascii_letters, k=10))
            elif item_type == 'tuple':
                item = (random.randint(0, 1000), random.choice(['a', 'b', 'c']))
            all_items.append(item)
        member_data = random.sample(all_items, n)
        member_set = set(member_data)
        non_member_data = [x for x in all_items if x not in member_set]
        return member_data, non_member_data
    
    return [], []


def benchmark_single_insert(bf, data, insert_fn):
    """
    Benchmark insertion for a single filter.
    
    Args:
        bf: The bloom filter instance
        data: Items to insert
        insert_fn: Function to call for insertion (e.g., lambda bf, item: bf.add(item))
    
    Returns:
        Time taken in seconds, or None if failed
    """
    try:
        start = time.perf_counter()
        for item in data:
            insert_fn(bf, item)
        return time.perf_counter() - start
    except Exception as e:
        print(f"  Insert failed: {e}")
        return None


def benchmark_single_query(bf, data, query_fn):
    """
    Benchmark query for a single filter.
    
    Args:
        bf: The bloom filter instance
        data: Items to query
        query_fn: Function to call for query (e.g., lambda bf, item: item in bf)
    
    Returns:
        (time, found_count) or (None, None) if failed
    """
    try:
        start = time.perf_counter()
        found = sum([1 for item in data if query_fn(bf, item)])
        return time.perf_counter() - start, found
    except Exception as e:
        print(f"  Query failed: {e}")
        return None, None