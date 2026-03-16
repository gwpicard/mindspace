"""Tests for eval metric functions."""

from mindspace.eval.metrics import (
    hit_at_k,
    mrr,
    negative_leakage,
    precision_at_k,
    recall_at_k,
)


class TestPrecisionAtK:
    def test_perfect_precision(self):
        assert precision_at_k(["a", "b", "c"], ["a", "b", "c"], k=3) == 1.0

    def test_half_precision(self):
        assert precision_at_k(["a", "x", "b", "y"], ["a", "b"], k=4) == 0.5

    def test_no_relevant(self):
        assert precision_at_k(["x", "y", "z"], ["a", "b"], k=3) == 0.0

    def test_k_larger_than_retrieved(self):
        assert precision_at_k(["a"], ["a", "b"], k=5) == 1.0

    def test_k_zero(self):
        assert precision_at_k(["a", "b"], ["a"], k=0) == 0.0

    def test_empty_retrieved(self):
        assert precision_at_k([], ["a"], k=3) == 0.0


class TestRecallAtK:
    def test_perfect_recall(self):
        assert recall_at_k(["a", "b", "c"], ["a", "b"], k=3) == 1.0

    def test_partial_recall(self):
        assert recall_at_k(["a", "x", "y"], ["a", "b"], k=3) == 0.5

    def test_no_recall(self):
        assert recall_at_k(["x", "y", "z"], ["a", "b"], k=3) == 0.0

    def test_empty_relevant(self):
        assert recall_at_k(["a", "b"], [], k=3) == 0.0

    def test_k_zero(self):
        assert recall_at_k(["a", "b"], ["a"], k=0) == 0.0


class TestMRR:
    def test_first_position(self):
        assert mrr(["a", "b", "c"], ["a"]) == 1.0

    def test_second_position(self):
        assert mrr(["x", "a", "c"], ["a"]) == 0.5

    def test_third_position(self):
        assert mrr(["x", "y", "a"], ["a"]) == pytest.approx(1 / 3)

    def test_no_match(self):
        assert mrr(["x", "y", "z"], ["a"]) == 0.0

    def test_multiple_relevant_returns_first(self):
        assert mrr(["x", "a", "b"], ["a", "b"]) == 0.5


class TestHitAtK:
    def test_hit(self):
        assert hit_at_k(["x", "a", "y"], ["a"], k=3) is True

    def test_miss(self):
        assert hit_at_k(["x", "y", "z"], ["a"], k=3) is False

    def test_hit_outside_k(self):
        assert hit_at_k(["x", "y", "a"], ["a"], k=2) is False

    def test_k_zero(self):
        assert hit_at_k(["a"], ["a"], k=0) is False


class TestNegativeLeakage:
    def test_no_leakage(self):
        assert negative_leakage(["a", "b", "c"], ["x", "y"], k=3) == []

    def test_leakage(self):
        assert negative_leakage(["a", "x", "b"], ["x", "y"], k=3) == ["x"]

    def test_multiple_leakage(self):
        result = negative_leakage(["x", "a", "y"], ["x", "y"], k=3)
        assert result == ["x", "y"]

    def test_empty_negatives(self):
        assert negative_leakage(["a", "b"], [], k=3) == []

    def test_k_zero(self):
        assert negative_leakage(["x"], ["x"], k=0) == []


import pytest
