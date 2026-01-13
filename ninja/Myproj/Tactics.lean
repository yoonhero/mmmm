import Mathlib.Tactic

theorem trivial_norm_num : 2 = 2 := by
  norm_num

-- Introduction Rule: ∀n, P(n) -> intro n; <prove P(n)>
-- Elimination Rule: have h := fa m
theorem alg' : forall (c d : Nat), (c + d)^3 = c^3 + d^3 + 3*c^2*d + 3*c*d^2 := by
  intro c d
  ring

-- Introduction Rule: ∃r, P(r) -> use k; <prove P(n)>
theorem ev10 : Even 10 := by
  unfold Even -- unfold definition of Even
  use 5

-- Introduction Rule: intro hp;
-- Elimination Rule: obtain ⟨k, hk⟩
theorem two_div_even : ∀ (n : Nat), Even n → 2 ∣ n := by
  -- Assume n
  intro n
  -- Assume n is even
  intro n_even
  unfold Even at n_even
  -- n = r + r for some r
  obtain ⟨r, hr⟩ := n_even
  have n_eq_2r : n = 2 * r := by
    rw [hr]
    ring
  rw [n_eq_2r]
  simp

#check ev10
#check two_div_even 10 even10

-- Elimination Rule: have hq := im(:P → Q) <proof P>
theorem two_div_ten : 2 ∣ 10 := by
  have h := two_div_even 10 ev10
  exact h

def PrimeNum (n: Nat) : Prop := n ≥ 2 ∧ ∀ (m: Nat), m ∣ n → m = 1 ∨ m = n

-- Elimination Rule: obtain ⟨hl, hr⟩ := an
theorem not_prime1 : ¬ PrimeNum 1 := by
  -- Assume 1 is PrimeNum
  intro pr1
  unfold PrimeNum at pr1
  obtain ⟨hl, hr⟩ := pr1
  contradiction

-- Elimination Rule: rcases or with hl | hr
theorem not_prime9 : ¬ PrimeNum 9 := by
  intro pr9
  unfold PrimeNum at pr9
  obtain ⟨hl, hr⟩ := pr9
  have hr_3 := hr 3
  have three_div_nine : (3: Nat) ∣ 9 := by simp
  have or_cases := hr_3 three_div_nine
  rcases or_cases with c1 | c2
  · contradiction
  · contradiction

-- ∧ Introduction Rule: exact ⟨<prove P>, <prove Q>⟩
-- ∨ Introduction Rule: exact Or.inl <prove P or Q>
theorem prime_5 : PrimeNum 5 := by
  unfold PrimeNum
  have g1 : 5 ≥ 2 := by norm_num
  have g2 : ∀ m : Nat, m ∣ 5 → m = 1 ∨ m = 5 := by
    intro m h_m_div_5
    match m with
    | 0 => contradiction
    | 1 =>
      have h : 1 = 1 := by rfl
      exact Or.inl h
    | 2 => contradiction
    | 3 => contradiction
    | 4 => contradiction
    | 5 =>
      have h : 5 = 5 := by rfl
      exact Or.inr h
    | n + 6 =>
      have h1 : 5 < n + 6 := by norm_num
      have h2 :=
        Nat.eq_zero_of_dvd_of_lt h_m_div_5 h1
      contradiction
  exact ⟨g1, g2⟩


#check Classical.em

#check irrational_sqrt_two

#check Real.rpow_mul

theorem irrat_pow_irrat_rat : ∃ (x y : ℝ), Irrational x ∧ Irrational y ∧ ¬ Irrational (x ^ y) := by
  have em := Classical.em (Irrational (√2^√2))
  rcases em with hl | hr
  · use √2^√2, √2
    have irrat : Irrational √2 := irrational_sqrt_two
    have eq : (√2^√2)^√2 = 2 := by
      calc
        (√2^√2)^√2 = √2^(√2 * √2) := by
          have nonneg_sq : 0 ≤ √2 := by
            simp
          have h := Real.rpow_mul nonneg_sq √2 √2
          rw [h]
          --symm at h
          --exact h
        _ = √2^2 := by simp
        _ = 2 := by simp
    have rat : ¬ Irrational ((√2^√2)^√2) := by
      rw [eq]
      simp
    exact ⟨hl, irrat, rat⟩
  · use √2, √2
    have irrat : Irrational √2 := irrational_sqrt_two
    exact ⟨irrat, irrat, hr⟩

-- this is proved several ways
--   Euclid: clever way! minimal
--   Euler: put 1 into Euler product function(Dirichlet sequence)
--   Erdos: 1/p sequence
#check Nat.exists_prime_and_dvd
#check Nat.factorial_pos
#check Classical.byContradiction
#check Nat.dvd_factorial
#check Nat.dvd_add_right
#check Nat.Prime.two_le
#check Nat.eq_zero_of_dvd_of_lt
theorem infinite_primes : ∀ n : Nat, ∃ p : Nat, Nat.Prime p ∧ p > n := by
  intro n
  have not1 : n.factorial + 1 ≠ 1 := by
    have h := Nat.factorial_pos n
    linarith
  have p_exists := Nat.exists_prime_and_dvd not1
  obtain ⟨p, p_prime, p_dvd_nfp1⟩ := p_exists
  use p
  have plen_false : ¬ (p > n) → False := by
    intro plen
    push_neg at plen
    have pgt1 : 1 < p := by
      have h := Nat.Prime.two_le p_prime
      linarith
    have pgt0 : 0 < p := by
      linarith
    have p_dvd_nf : p ∣ n.factorial := by
      exact Nat.dvd_factorial pgt0 plen
    have p_dvd_1 : p ∣ 1 := by
      obtain ⟨hl, hr⟩ := Nat.dvd_add_right p_dvd_nf
      have h := hl p_dvd_nfp1
      exact h
    have f : 1 = 0 := by
      have h := Nat.eq_zero_of_dvd_of_lt p_dvd_1 pgt1
      exact h
    contradiction
  have pgtn : p > n := by
    have h := Classical.byContradiction plen_false
    exact h
  exact ⟨p_prime, pgtn⟩


#check Classical.choose

open Classical
#check choose
#check choose_spec

theorem surj_imp_right_inv {A B : Type } : ∀ f : A → B, 
  Function.Surjective f → ∃ g : B → A,
    ∀ y : B, f (g y) = y := by
      intro f surjf
      unfold Function.Surjective at surjf

      let g := fun y : B =>
        choose (surjf y)
      use g
      intro b
      unfold g
      have h := choose_spec (surjf b)
      exact h















