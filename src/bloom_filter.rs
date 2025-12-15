/// Core Bloom Filter implementation in Rust.
/// This is a pure Rust implementation that can be tested independently.

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
    pub fn new(capacity: usize, false_positive_rate: f64) -> Self {
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
        todo!()
        // make this return a result to unpack later        
    }

    /// Check if an item might be in the Bloom filter.
    /// Returns true if the item might be present (with possibility of false positives),
    /// false if the item is definitely not present.
    pub fn might_contain<T: Hash>(&self, item: &T) -> bool {
        todo!()
    }

    /// Hash based on a seed to consistently get results for n-hashes on an item
    fn hash_index<T: Hash>(&self, item: &T, hash_num: usize) -> usize {
        let state = RandomState::with_seed(hash_num);
        let mut hasher = state.build_hasher();
        item.hash(&mut hasher);
        hasher.finish() as usize % self.bit_array.len()
    }

    /// Get the number of bits in the filter.
    pub fn bit_count(&self) -> usize {
        todo!()
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
    fn test_false_positives() {
        let mut bf = BloomFilter::new(10, 0.1); // Small capacity, higher false positive rate
        for i in 0..10 {
            bf.insert(&i);
        }
        
        // Check some items that weren't inserted
        // With small capacity, we might get false positives
        let false_positives = (10..20)
            .filter(|i| bf.might_contain(i))
            .count();
        
        // Should have some false positives with this configuration
        // (exact count depends on hash collisions)
        println!("False positives in range 10-20: {}", false_positives);
    }
}

