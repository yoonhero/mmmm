-- import
import Mathlib.Data.Rat.Init
import Mathlib.Data.Int.GCD

def hello := "world"
def m : Nat := 1
def n : Nat := 0
def b1 : Bool := true
def b2: Bool := false

#check m
#check b1 && b2

#eval 5 * 4

#check Nat → Nat → Bool
#check Nat → Nat

#eval (5, 9).2
#check Nat × Nat → Nat
#check Nat.add
#check Nat → (Nat → Nat)
#check Nat.add 3
#check Nat.succ
#eval Nat.add 3 6

def α : Type := Nat
def β : Type := Nat
def γ : Type := (α × β) → Nat

#check Prod α β
#check α


inductive Nat2: Type
| zero: Nat2
| succ: Nat2 → Nat2
def Nat2.add : Nat2 → Nat2 → Nat2
| n, Nat2.zero => n
| n, Nat2.succ m => Nat2.succ (Nat2.add n m)
-- def a: Nat2 := 2
-- #eval Nat2.add : Nat2 3: Nat2

-- constant and : Prop → Prop → Prop
variable {p q r : Prop}
#check p
#check And p q
#check p ∧ q

-- LEAN4
-- based on Dependent type theory
--    proposition as type, proof as term of type. (proposition-as-types paradigm)
--    Curry-Horward isomorphism?
-- Tactic based approach
--    Direct Proof           apply/exact
--    Contradiction Proof    by_contra/exfalso
--    induction              induction
--    cases                  cases

theorem and_swap (p q : Prop) : p ∧ q → q ∧ p := by
  intro h -- 가정 p ∧ q을 도입한다.
  apply And.intro -- 결론 q ∧ p를 구성하기 위해서 And.intro 적용
  .exact h.right -- 첫 번째 구성요소 q를 h에서 추출?
  .exact h.left -- 두 번째 구성요소 p를 h에서 추출?

theorem example1 (p q : Prop) : p → p := by
  intro h
  exact h

theorem my_favorite_theorem {a b : ℝ} (h₀ : a^3 - 3*a*b^2=39) (h₁ : b^3 - 3*b*a^2=26):
  a^2+b^2=13 := by sorry

def qq : ℚ := 1/2
#eval (3 : ℚ) + (4 : ℚ)
-- theorem sqrt2_irrational : ¬ ∃ (a, b : ℤ)
