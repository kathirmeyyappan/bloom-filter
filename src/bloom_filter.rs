/// Core Bloom Filter implementation in Rust.

use std::hash::{BuildHasher, Hash, Hasher};
use bitvec::prelude::*;
use ahash::RandomState;

const LN_2: f64 = 0.6931471805599453;

pub struct BloomFilter {
    bit_array: BitVec<u64, Lsb0>,
    pub num_hashes: usize,
    pub capacity: usize,
}

impl BloomFilter {
    /// Create a new Bloom filter with the given capacity and false positive rate.
    /// 
    /// # Arguments
    /// * `capacity` - Expected number of elements
    /// * `false_positive_rate` - Desired false positive probability (e.g., 0.01 for 1%)
    /// 
    /// # Panics
    /// Panics if `capacity` is 0 or if `false_positive_rate` is >= 1.0
    pub fn new(capacity: usize, false_positive_rate: f64) -> Self {
        assert!(capacity != 0, "capacity must be greater than 0");
        assert!(false_positive_rate < 1.0, "false_positive_rate must be less than 1.0");
        
        // personal reference for math: https://www.notion.so/kathirm/Bloom-filter-project-references-2ca9871cd3ff802fb87bef28266252e9?source=copy_link#d803f6ad34b1415ba1047fdd7c666800
        let num_bits = (-(capacity as f64 * false_positive_rate.ln() / (LN_2.powi(2)))).ceil() as usize;
        let num_hashes = (num_bits as f64 / capacity as f64 * LN_2).ceil() as usize; // slightly faster than taking log(false_positive_rate)
        
        Self {
            bit_array: BitVec::repeat(false, num_bits),
            num_hashes,
            capacity,
        }
    }

    /// Add an item to the Bloom filter.
    pub fn insert<T: Hash>(&mut self, item: &T) {
        for hash_num in 0..self.num_hashes{
            let i = self.hash_index(item, hash_num);
            self.bit_array.set(i, true);
        }
    }

    /// Check if an item might be in the Bloom filter.
    /// Returns true if the item might be present (with possibility of false positives),
    /// false if the item is definitely not present.
    pub fn might_contain<T: Hash>(&self, item: &T) -> bool {
        // check if all hashes for item are set
        (0..self.num_hashes).all(|hash_num| {
            let i = self.hash_index(item, hash_num);
            self.bit_array[i]
        })
    }

    /// Hash based on a seed to consistently get results for n-hashes on an item
    fn hash_index<T: Hash>(&self, item: &T, hash_num: usize) -> usize {
        let state = RandomState::with_seeds(hash_num as u64, 42, 42, 42);
        let mut hasher = state.build_hasher();
        item.hash(&mut hasher);
        hasher.finish() as usize % self.bit_array.len()
    }

    /// Get the number of bits in the filter.
    pub fn bit_count(&self) -> usize {
        self.bit_array.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_insert_and_contains() {
        let mut bf = BloomFilter::new(100, 0.01);
        bf.insert(&"hello");
        bf.insert(&"world");
        
        assert!(bf.might_contain(&"hello"));
        assert!(bf.might_contain(&"world"));
        assert!(!bf.might_contain(&"not_present"));
    }

    #[test]
    fn test_no_false_negatives() {
        let mut bf = BloomFilter::new(10_000, 0.01);

        for item in 0..10_000 {
            bf.insert(&item);
        }
        
        for item in 0..10_000 {
            assert!(bf.might_contain(&item), "False negative for item: {}", item);
        }
    }

    #[test]
    fn test_empty_filter() {
        let bf = BloomFilter::new(100, 0.01);
        
        // empty filter should return false for everything
        assert!(!bf.might_contain(&"anything"));
        assert!(!bf.might_contain(&42));
        assert!(!bf.might_contain(&vec![1, 2, 3]));
    }

    #[test]
    fn test_different_types() {
        let mut bf = BloomFilter::new(100, 0.01);
        
        bf.insert(&"string");
        bf.insert(&42i32);
        bf.insert(&100u64);
        bf.insert(&vec![1, 2, 3]);
        
        assert!(bf.might_contain(&"string"));
        assert!(bf.might_contain(&42i32));
        assert!(bf.might_contain(&100u64));
        assert!(bf.might_contain(&vec![1, 2, 3]));
        
        assert!(!bf.might_contain(&"different_string"));
        assert!(!bf.might_contain(&99i32));
    }

    #[test]
    fn test_duplicate_inserts() {
        let mut bf = BloomFilter::new(100, 0.01);
        let item = "test_item";
        
        // inserting same item multiple times should be fine
        bf.insert(&item);
        bf.insert(&item);
        bf.insert(&item);
        assert!(bf.might_contain(&item));
    }


    #[test]
    fn test_large_capacity() {
        let capacity = 10_000;
        let mut bf = BloomFilter::new(capacity, 0.01);
        
        for i in (0..capacity).step_by(100) {
            bf.insert(&i);
        }
        
        for i in (0..capacity).step_by(100) {
            assert!(bf.might_contain(&i));
        }
    }

    #[test]
    fn test_false_positive_rate() {
        let cap = 100;
        let mut bf = BloomFilter::new(cap, 0.1);
        for i in 0..cap {
            bf.insert(&i);
        }
        
        // test 100k items that are not in bloom filter to see false positives
        let false_positives = (cap..cap+100_000)
            .filter(|i| bf.might_contain(i))
            .count();
        
        // should have roughly 10% false positives with this configuration
        assert!(false_positives > 7500);
        assert!(false_positives < 12500);
    }

    #[test]
    fn test_very_low_false_positive_rate() {
        let mut bf = BloomFilter::new(100_000, 0.0001);
        
        for i in 0..100_000 {
            bf.insert(&i);
        }
        
        // test 100k items that are not in bloom filter to see false positives
        let false_positives = (100_000..200_000)
            .filter(|i| bf.might_contain(i))
            .count();
        
        // with 0.01% false positive rate, expect roughly 10 false positives in 100k tests
        assert!(false_positives < 20);
    }

    #[test]
    #[should_panic(expected = "capacity must be greater than 0")]
    fn test_zero_capacity_panics() {
        BloomFilter::new(0, 0.01);
    }

    #[test]
    #[should_panic(expected = "false_positive_rate must be less than 1.0")]
    fn test_false_positive_rate_ge_one_panics() {
        BloomFilter::new(100, 1.0);
    }

    #[test]
    #[should_panic(expected = "false_positive_rate must be less than 1.0")]
    fn test_false_positive_rate_gt_one_panics() {
        BloomFilter::new(100, 1.5);
    }
}

