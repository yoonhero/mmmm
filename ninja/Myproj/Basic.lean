import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.QuadraticDiscriminant

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

-- from wikipedia (https://ko.wikipedia.org/wiki/Lean)
theorem and_swap (p q : Prop) : p ∧ q → q ∧ p := by
  intro h -- 가정 p ∧ q을 도입한다.
  apply And.intro -- 결론 q ∧ p를 구성하기 위해서 And.intro 적용
  .exact h.right -- 첫 번째 구성요소 q를 h에서 추출?
  .exact h.left -- 두 번째 구성요소 p를 h에서 추출?

-- it seems like more advanced way! using Tactic.
theorem another_and_swap (p q : Prop) : p ∧ q → q ∧ p := by
  intro h
  obtain ⟨hl, hr⟩ := h
  exact ⟨hr, hl⟩

theorem or_swap (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  rcases h with c1 | c2
  · exact Or.inr c1
  · exact Or.inl c2

theorem example1 (p q : Prop) : p → p := by
  intro h
  exact h

open Real

#check (39 : ℝ)
#check sq_nonneg
#check add_le_add
#check discrim_lt_zero_of_neg
#check quadratic_ne_zero_of_discrim_ne_sq
#check ne_of_lt
#check lt_of_lt_of_le
#check mul_eq_zero.mp

theorem my_favorite_theorem (a b : ℝ) (h0: a^3 - 3*a*b^2 = 39) (h1: b^3 - 3*b*a^2=26) :
    a^2 + b^2 = 13 := by
      have A : a^6 - 6*a^4*b^2 + 9*a^2*b^4 = 39^2 := by
        calc 
          a^6 - 6*a^4*b^2  + 9*a^2*b^4 = (a^3 - 3*a*b^2)^2 := by
            ring_nf
          _ = 39^2 := by rw [h0]
      have B : b^6 - 6*a^2*b^4 + 9*a^4*b^2 = 26^2 := by
        calc 
          b^6 - 6*a^2*b^4 + 9*a^4*b^2 = (b^3 - 3*b*a^2)^2 := by
            ring_nf
          _ = 26^2 := by rw [h1]
      have C : (a^2+b^2)^3 = 13^3 := by
        calc
          (a^2+b^2)^3 = a^6 + 3*a^4*b^2 + 3*a^2*b^4 + b^6 := by
            ring_nf
          _ = (a^6 - 6*a^4*b^2 + 9*a^2*b^4) + (b^6 - 6*a^2*b^4 + 9*a^4*b^2) := by
            ring_nf
          _ = 13^3 := by
            rw [A, B]
            ring

       -- have square_sum_larger_than_0 : 0 ≤ a^2 + b^2 := by
       --   have ha : 0 ≤ a^2 := sq_nonneg a       
       --   have hb : 0 ≤ b^2 := sq_nonneg b
       --   have h : 0 + 0 ≤ a^2 + b^2 := add_le_add ha hb
       --   simpa using h
      have square_sum_larger_than_0 : 0 ≤ a^2 + b^2 := add_nonneg (sq_nonneg a) (sq_nonneg b)
      have Or : a^2 + b^2 - 13 = 0 ∨ (a^2+b^2)^2 + 13 * (a^2+b^2) + 13^2 = 0 := by
        have h : ((a^2 + b^2) - 13) * ((a^2+b^2)^2 + 13 * (a^2+b^2) + 13^2) = 0 := by
          calc
            ((a^2 + b^2) - 13) * ((a^2+b^2)^2 + 13*(a^2+b^2) + 13^2) = (a^2+b^2)^3 - 13^3 := by ring
            _ = 0 := by simp [C]
        exact mul_eq_zero.mp h
      
      rcases Or with c1 | c2
      · exact sub_eq_zero.mp c1
      · exfalso
        let x : ℝ := a^2 + b^2
        have hq : 1*(x*x) + 13*x + 169 = 0 := by
          norm_num at c2
          simpa [x, pow_two] using c2
        
        have hD : discrim (1:ℝ) 13 169 < 0 := by
          norm_num [discrim]

        have h := quadratic_ne_zero_of_discrim_ne_sq (a := (1:ℝ)) (b := 13) (c := 169)
          (by
            intro s
            have : 0 ≤ s^2 := sq_nonneg s
            exact ne_of_lt (lt_of_lt_of_le hD this))
          x
        
        exact h hq       



-- def qq : ℚ := 1/2
-- #eval (3 : ℚ) + (4 : ℚ)
-- theorem sqrt2_irrational : ¬ ∃ (a, b : ℤ)
