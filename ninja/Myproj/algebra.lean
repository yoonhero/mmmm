import Mathlib.Tactic

-- Close Structure
--   Magma: ∀ x y, x * y ∈ S
--   Semigroup: ∀ x y z, x * (y * z) = x * y * z
--   Monoid: ∃ y, ∀ x, x * e = x
--   Group: ∀ x, ∃ y, x * y = e ∧ y * x = e

def xs: List Nat := [0, 1, 2]
def identity: List Nat := []
#eval xs ++ identity

def x1 := [1]
def x2 := [2]
def x3 := [3]
#eval x1++(x2++x3) = x1++x2++x3

theorem list_assoc (a b c : List Nat) : a++(b++c) = a++b++c := by
  simp

-- so how does Monoid implmented in programing language?
-- instance : Monoid (List α) where
--   mul := (++)
--   one := []
--   mul_assoc := List.append_assoc
--   one_mul := List.nil_append
--   mul_one := List.append_nil

-- generic <T> vs. α: Type
--   in Lean, you can write "prop about type" in logic system
--     mul: α → α → α

variable {G : Type} [Group G]

example (a b : G) : (a * b)⁻¹ = b⁻¹ * a⁻¹ := by
  group

example (a : G) : a⁻¹ * a = 1 := by
  group

