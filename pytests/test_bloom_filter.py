# AI-generated pytest tests for the BloomFilter class

from kathir_bloom_filter import BloomFilter


def test_basic_insert_and_contains():
    bf = BloomFilter(capacity=1000, false_positive_rate=0.01)
    bf.insert("hello")
    bf.insert("world")
    
    assert "hello" in bf
    assert "world" in bf
    assert bf.might_contain("hello")
    assert bf.might_contain("world")


def test_definitely_not_contains():
    bf = BloomFilter(capacity=100, false_positive_rate=0.01)
    bf.insert("apple")
    
    # Items never inserted should (usually) not be found
    # We test many to ensure at least some return False
    not_found_count = sum(1 for i in range(1000) if f"notinserted_{i}" not in bf)
    assert not_found_count > 900  # At least 90% should be correctly rejected


def test_integers():
    bf = BloomFilter(capacity=1000, false_positive_rate=0.01)
    for i in range(100):
        bf.insert(i)
    
    for i in range(100):
        assert i in bf
    
    # Check non-members
    not_found_count = sum(1 for i in range(1000, 2000) if i not in bf)
    assert not_found_count > 900


def test_mixed_types():
    bf = BloomFilter(capacity=1000, false_positive_rate=0.01)
    bf.insert("string_item")
    bf.insert(42)
    bf.insert((1, 2, 3))  # tuple is hashable
    
    assert "string_item" in bf
    assert 42 in bf
    assert (1, 2, 3) in bf


def test_properties():
    bf = BloomFilter(capacity=1000, false_positive_rate=0.01)
    
    assert bf.capacity == 1000
    assert bf.false_positive_rate == 0.01
    assert bf.bit_count > 0
    assert bf.hash_count > 0


def test_false_positive_rate_reasonable():
    """Test that actual false positive rate is close to expected."""
    capacity = 10000
    fpr = 0.01
    bf = BloomFilter(capacity=capacity, false_positive_rate=fpr)
    
    # Insert items
    for i in range(capacity):
        bf.insert(i)
    
    # Check false positives on non-members
    false_positives = sum(1 for i in range(capacity, capacity * 2) if i in bf)
    actual_fpr = false_positives / capacity
    
    # Allow 3x tolerance (bloom filters can vary)
    assert actual_fpr < fpr * 3, f"FPR {actual_fpr} too high (expected ~{fpr})"


def test_large_capacity():
    bf = BloomFilter(capacity=100000, false_positive_rate=0.001)
    
    for i in range(1000):
        bf.insert(f"item_{i}")
    
    for i in range(1000):
        assert f"item_{i}" in bf

