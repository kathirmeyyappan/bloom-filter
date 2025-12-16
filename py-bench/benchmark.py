#!/usr/bin/env python3
"""Benchmark comparing bloom_filter (Python) vs kathir_bloom_filter (Rust)."""

from kathir_bloom_filter import BloomFilter as KathirBloomFilter
from bloom_filter import BloomFilter
from rbloom import Bloom as RbloomFilter
from bloom_filter2 import BloomFilter as BloomFilter2
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


def benchmark_insertion(bf, bf2, rbf, kbf, data):
    """Benchmark insertion speed."""
    # bloom-filter
    start = time.perf_counter()
    for item in data:
        bf.add(item)
    py_time = time.perf_counter() - start
    
    # bloom-filter2
    start = time.perf_counter()
    for item in data:
        bf2.add(item)
    bf2_time = time.perf_counter() - start
    
    # rbloom
    start = time.perf_counter()
    for item in data:
        rbf.add(item)
    rbloom_time = time.perf_counter() - start
    
    # kathir-bloom-filter
    start = time.perf_counter()
    for item in data:
        kbf.insert(item)
    rust_time = time.perf_counter() - start
    
    return py_time, bf2_time, rbloom_time, rust_time


def benchmark_query(bf, bf2, rbf, kbf, data):
    """Benchmark query speed."""
    # bloom-filter
    start = time.perf_counter()
    py_found = sum([item in bf for item in data])
    py_time = time.perf_counter() - start
    
    # bloom-filter2
    start = time.perf_counter()
    bf2_found = sum([item in bf2 for item in data])
    bf2_time = time.perf_counter() - start
    
    # rbloom
    start = time.perf_counter()
    rbloom_found = sum([item in rbf for item in data])
    rbloom_time = time.perf_counter() - start
    
    # kathir-bloom-filter
    start = time.perf_counter()
    rust_found = sum([item in kbf for item in data])
    rust_time = time.perf_counter() - start
    
    return py_time, bf2_time, rbloom_time, rust_time, py_found, bf2_found, rbloom_found, rust_found


def benchmark_false_positives(bf, bf2, rbf, kbf, non_member_data):
    """Benchmark false positive rate."""
    py_fp = sum([item in bf for item in non_member_data])
    bf2_fp = sum([item in bf2 for item in non_member_data])
    rbloom_fp = sum([item in rbf for item in non_member_data])
    rust_fp = sum([item in kbf for item in non_member_data])
    return py_fp, bf2_fp, rbloom_fp, rust_fp


def run_benchmark(data_type: str, n: int, capacity: int, error_rate: float):
    """Run complete benchmark for a data type."""
    print(f"\n{data_type.upper()} (N={n:,}):")
    print("-" * 60)
    
    # Generate data - returns tuple of (member_data, non_member_data) guaranteed to be disjoint
    member_data, non_member_data = generate_data(data_type, n, seed=42)
    
    # Create filters
    bf = BloomFilter(max_elements=capacity, error_rate=error_rate)
    kbf = KathirBloomFilter(capacity=capacity, false_positive_rate=error_rate)
    rbf = RbloomFilter(expected_items=capacity, false_positive_rate=error_rate)
    bf2 = BloomFilter2(max_elements=capacity, error_rate=error_rate)
    
    # Insertion
    py_insert, bf2_insert, rbloom_insert, rust_insert = benchmark_insertion(bf, bf2, rbf, kbf, member_data)
    print(f"  Insertion:")
    print(f"    bloom-filter:        {py_insert:.4f}s ({n/py_insert:,.0f} items/sec)")
    print(f"    bloom-filter2:      {bf2_insert:.4f}s ({n/bf2_insert:,.0f} items/sec)")
    print(f"    rbloom:              {rbloom_insert:.4f}s ({n/rbloom_insert:,.0f} items/sec)")
    print(f"    kathir-bloom-filter: {rust_insert:.4f}s ({n/rust_insert:,.0f} items/sec)")
    
    # Query
    py_query, bf2_query, rbloom_query, rust_query, py_found, bf2_found, rbloom_found, rust_found = benchmark_query(bf, bf2, rbf, kbf, member_data)
    print(f"  Query (present):")
    print(f"    bloom-filter:        {py_query:.4f}s ({n/py_query:,.0f} queries/sec)")
    print(f"    bloom-filter2:      {bf2_query:.4f}s ({n/bf2_query:,.0f} queries/sec)")
    print(f"    rbloom:              {rbloom_query:.4f}s ({n/rbloom_query:,.0f} queries/sec)")
    print(f"    kathir-bloom-filter: {rust_query:.4f}s ({n/rust_query:,.0f} queries/sec)")
    print(f"    Found:               bloom-filter={py_found:,}/{n:,}, bloom-filter2={bf2_found:,}/{n:,}, rbloom={rbloom_found:,}/{n:,}, kathir-bloom-filter={rust_found:,}/{n:,}")
    
    # False positives
    py_fp, bf2_fp, rbloom_fp, rust_fp = benchmark_false_positives(bf, bf2, rbf, kbf, non_member_data)
    expected_fp = n * error_rate
    print(f"  False Positives:")
    print(f"    Expected:            {expected_fp:,.0f}")
    print(f"    bloom-filter:        {py_fp:,} ({py_fp/n*100:.4f}%)")
    print(f"    bloom-filter2:      {bf2_fp:,} ({bf2_fp/n*100:.4f}%)")
    print(f"    rbloom:              {rbloom_fp:,} ({rbloom_fp/n*100:.4f}%)")
    print(f"    kathir-bloom-filter: {rust_fp:,} ({rust_fp/n*100:.4f}%)")


def main():
    """Run all benchmarks."""
    print("=" * 60)
    print("BLOOM FILTER BENCHMARK")
    
    n, capacity, error_rate = 1_000_000, 1_000_000, 0.001
    
    data_types = ["int", "string", "mixed"]
    
    print(f"CONFIGURATION: N={n:,}, Capacity={capacity:,}, Error Rate={error_rate}")
    print(f"{'='*60}")
    
    for data_type in data_types:
        try:
            run_benchmark(data_type, n, capacity, error_rate)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print(f"\n{'='*60}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
