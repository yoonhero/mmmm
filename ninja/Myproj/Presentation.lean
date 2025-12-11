import Mathlib.Data.List.Basic
import Mathlib.Tactic

open List

theorem sum_le_length (L : List ℕ) (h : ∀ i ∈ L, i ≤ 1) : L.sum ≤ L.length := by
  induction L with
  | nil => simp
  | cons head tail ih =>
    simp
    have h_head : head ≤ 1 := h head (by simp)
    have h_tail : ∀ i ∈ tail, i ≤ 1 := by
      intro i hi
      exact h i (by simp [hi])
    have ih' : tail.sum ≤ tail.length := ih h_tail

    have h_add : head + tail.sum ≤ 1 + tail.length :=
      Nat.add_le_add h_head ih'

    simpa [Nat.succ_eq_add_one, Nat.add_comm] using h_add

-- Pigeons in holes. Here there are 10 pigeons and 9 holes.
-- Is there any holes has more than one pigeon?
theorem pigeon_hole_principle (counts: List ℕ) (h_holes: counts.length = 9) (h_pigeons: counts.sum = 10) : ∃ m ∈ counts, m ≥ 2 := by
  by_contra! h_all_lt_2
  have h_all_le_1 : ∀ m ∈ counts, m ≤ 1 := by
    intro m hm_in
    exact Nat.le_of_lt_succ (h_all_lt_2 m hm_in)

  have h_sum_le_9 : counts.sum ≤ counts.length :=
    sum_le_length counts h_all_le_1

  rw [h_pigeons, h_holes] at h_sum_le_9
  tauto

def counts := [0, 0, 0, 0, 0, 0, 0, 0, 0]

#eval counts.length
#eval counts.sum
#eval decide (counts.length == 9)
#eval decide (∃ m ∈ counts, m ≤ 2)

#check pigeon_hole_principle

#find Nat → Nat
