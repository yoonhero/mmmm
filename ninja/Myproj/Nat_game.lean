import Mathlib.Tactic

theorem isMe (x q : Nat) : 37 * x + q = 37 * x + q := by rfl
theorem isMeWoHypothesis (x y: Nat) (h1: y = x + 7) : 2*y=2*(x+7) := by
  rw [h1]

theorem one_eq_succ_zero : 1 = Nat.succ 0 := by rfl
theorem two_eq_succ_one : 2 = Nat.succ 1 := by rfl
theorem four_eq_succ_three : 4 = Nat.succ 3 := by rfl

theorem addOneisSucc (n : Nat) : Nat.succ n = n + 1 := by
  rw [one_eq_succ_zero]
  -- rw [← Nat.add_succ]
  -- rw [← Nat.add_zero]

theorem twoPlusTwoIsFuckingFour : (2 : Nat) + 2 = 4 := by
  nth_rewrite 2 [two_eq_succ_one]
  rw [Nat.add_succ]
  -- rw [← succ_eq_add_one]
  -- rw [← three_eq_succ_two]
  -- rw [← four_eq_succ_three]
  -- rfl
  --> just by rfl is good? anyway lol

theorem _add_zero (n: Nat) : n + 0 = n := by
  rfl

theorem _zero_add (n: Nat) : 0 + n = n := by
  -- OLD Way Induction
  -- induction n with d hd
  -- rw [add_zero]
  -- rfl
  -- rw [add_succ]
  -- rw [d]
  -- rfl

  -- Current Way
  induction n with
  | zero => rfl
  | succ d ih =>
    rw [Nat.add_succ]
    rw [ih]

theorem _add_succ (a b : ℕ) : a + Nat.succ b = Nat.succ (a + b) := by
  rfl

theorem _succ_eq_add_one (n : ℕ) : Nat.succ n = n + 1 := by
  rfl

-- communicative에 신경 쓰면서 전개하기 생각보다 어렵네
theorem _succ_add (a b: ℕ) : Nat.succ a + b = Nat.succ (a + b) := by
  induction b with
  | zero => rfl
  | succ d ih =>
    rw [← Nat.succ_eq_add_one]
    rw [Nat.add_succ]
    rw [Nat.add_succ]
    rw [ih]

theorem _add_comm (a b : ℕ) : a + b = b + a := by
  induction b with
  | zero =>
    rw [_zero_add]
    rw [_add_zero]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_add_succ]
    rw [_succ_add]
    rw [ih]

-- in Lean a + b + c = (a + b) + c
theorem _add_assoc (a b c : ℕ) : a + b + c = a + (b + c) := by
  induction c with
  | zero =>
    -- rw [_add_zero]
    -- rw [_add_zero]
    simp [_add_zero]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_add_succ]
    rw [_add_succ]
    rw [_add_succ]
    rw [ih]

theorem _add_right_comm (a b c : ℕ) : a + b + c = a + c + b := by
   induction c with
  | zero =>
    rw [_add_zero]
    rw [_add_zero]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_add_succ]
    rw [_add_succ]
    rw [_succ_add]
    rw [ih]

theorem _mul_zero n : n * 0 = 0 := by rfl
theorem _mul_succ a b : a * Nat.succ b = a * b + a := by rfl

theorem _mul_one n : n * 1 = n := by
  rw [one_eq_succ_zero]
  rw [_mul_succ]
  rw [_mul_zero]
  rw [zero_add]

theorem _zero_mul n : 0 * n = 0 := by
  induction n with
  | zero =>
    rfl
  | succ d ih =>
    rw [_mul_succ]
    rw [_add_zero]
    rw [ih]

theorem _succ_mul a b : Nat.succ a * b = a * b + b := by
  induction b with
  | zero =>
    rw [_mul_zero]
    rw [_mul_zero]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_mul_succ]
    rw [_mul_succ]
    rw [_add_succ]
    rw [_add_succ]
    rw [ih]
    rw [_add_right_comm]

theorem _mul_comm (x y : Nat) : x * y = y * x := by
  induction y with
  | zero =>
    rw [_mul_zero]
    rw [_zero_mul]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_mul_succ]
    rw [_succ_mul]
    rw [ih]

theorem _one_mul (n : Nat) : 1 * n = n := by
  -- by succ_mul
  -- rw [one_eq_succ_zero]
  -- rw [_succ_mul]
  -- rw [_zero_mul]
  -- rw [_zero_add]
  -- or mul_comm
  rw [_mul_comm, _mul_one]

theorem _one_mul_by_induction (n : Nat) : 1 * n = n := by
  -- by induction
  induction n with
  | zero =>
    rw [mul_zero]
  | succ d ih =>
  nth_rewrite 1 [← _succ_eq_add_one]
  rw [_mul_succ]
  rw [ih]

theorem _two_mul (n : Nat) : 2 * n = n + n := by
  rw [two_eq_succ_one, _succ_mul, _one_mul]

theorem _mul_add (a b c : Nat) : a * (b + c) = a*b + a*c := by
  induction c with
  | zero =>
    rw [_add_zero, _mul_zero, _add_zero]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_add_succ, _mul_succ, _mul_succ, ih, _add_assoc]

theorem _add_mul (a b c : Nat) : (a + b) * c = a*c + b*c := by
  nth_rewrite 1 [_mul_comm]
  nth_rewrite 2 [_mul_comm]
  nth_rewrite 3 [_mul_comm]
  rw [_mul_add]

  -- repeat is more clean...!
  -- rw [mul_comm, mul_add]
  -- repeat rw [mul_comm c]

theorem _mul_assoc (a b c : Nat) : (a * b) * c = a * (b * c) := by
  induction b with
  | zero =>
    rw [_mul_zero, _zero_mul, _mul_zero]
  | succ d ih =>
    rw [← _succ_eq_add_one]
    rw [_mul_succ, _add_mul, ih]
    rw [_succ_mul, _mul_add]

theorem _pow_zero (n : ℕ) : n ^ 0 = 1 := by rfl
theorem _pow_succ (a b : ℕ) : a ^ (Nat.succ b)  = a ^ b * a := by rfl

theorem _zero_pow_zero : (0 : ℕ) ^ 0 = 1 := by
  rw [_pow_zero]

theorem _zero_pow_succ (n : ℕ) : 0 ^ (Nat.succ n) = 0 := by
  rw [_pow_succ, _mul_zero]

theorem _pow_one (n : ℕ) : n ^ 1 = n := by
  match n with
  | Nat.zero => rw [one_eq_succ_zero, _zero_pow_succ]
  | _ => rw [one_eq_succ_zero, _pow_succ, _pow_zero, _one_mul]

theorem _one_pow (n: ℕ) : 1 ^ n = 1 := by
  induction n with
  | zero =>
    rw [_pow_zero]
  | succ d ih =>
    rw [_pow_succ, _mul_one, ih]

theorem _pow_two (a : ℕ) : a ^ 2 = a * a := by
  rw [two_eq_succ_one, _pow_succ, _pow_one]

theorem _pow_add (a m n : ℕ) : a ^ (m + n) = a ^ m * a ^ n := by
  induction n with
  | zero =>
    rw [_add_zero, _pow_zero, _mul_one]
  | succ d ih =>
    rw [_add_succ, _pow_succ]
    rw [← _succ_eq_add_one, _pow_succ]
    rw [ih, _mul_assoc]

theorem _mul_pow (a b n : ℕ) : (a * b) ^ n = a ^ n * b ^ n := by
  induction n with
  | zero =>
    repeat rw [_pow_zero]
  | succ d ih =>
    repeat rw [_pow_succ]
    rw [ih]
    rw [_mul_assoc]
    rw [← _mul_assoc (b ^ d) a b]
    rw [_mul_comm (b ^ d) a]
    rw [_mul_assoc]
    rw [← _mul_assoc]

theorem _pow_pow (a m n : ℕ) : (a ^ m) ^ n = a ^ (m * n) := by
  induction n with
  | zero =>
    rw [_pow_zero, _mul_zero, _pow_zero]
  | succ d ih =>
    rw [_pow_succ, ih]
    rw [_mul_add, _mul_one, _pow_add]

theorem _add_sq (a b : ℕ) : (a + b) ^ 2 = a ^ 2 + b ^ 2 + 2 * a * b := by
  rw [_pow_two, _mul_add]
  repeat rw [_add_mul, ← _pow_two]
  rw [_mul_comm, _add_assoc, ← _add_assoc (a * b), ← _two_mul, ← _mul_assoc]
  rw [_add_comm (2 * a * b), ← _add_assoc]

-- Beyond my level sir
theorem FermetLastTheorme (a b c n : ℕ) : (a + 1) ^ (n + 3) + (b + 1) ^ (n + 3) ≠ (c + 1) ^ (n + 3) := by
  sorry

-- Beautiful!
theorem succ_inj (a b : ℕ) (h: a.succ = b.succ) : a = b := by
  rw [← Nat.pred_succ a]
  rw [← Nat.pred_succ b]
  rw [h]

-- Implication = new tactic!
theorem apply_example (a b : ℕ) (h: Nat.succ (a + 37) = Nat.succ (b + 42)) : a + 37 = b + 42 := by
  apply (Nat.succ_inj.mp) at h -- P -> Q : transform proposition
  exact h
  -- rw [Nat.succ_inj] at h
  -- exact h
  -- Or just
  -- rw [← Nat.succ_inj]
  -- exact h

theorem threePlusOneIsFour (a : ℕ) (h: a + 1 = 4) : a = 3 := by
  rw [four_eq_succ_three] at h
  rw [← _succ_eq_add_one] at h
  apply succ_inj at h
  exact h

  -- apply succ_inj -----> why this is working? not sure you are bijective..
                          -- But actually <-> sir
  -- rw [succ_eq_add_one, ← four_eq_succ_three]
  -- exact h

theorem intro_example (x : ℕ) : x = 3 → x = 3 := by
  intro h -- assuming it's true!
  exact h

theorem logic_example (x y : ℕ) : x + 1 = y + 1 → x = y := by
  intro h
  -- repeat rw [← succ_eq_add_one] at h
  apply succ_inj at h
  exact h

theorem logic_opposite_example (x y : ℕ) (h1: x = y) (h2: x ≠ y) : False := by
  apply h2 at h1
  exact h1

theorem _one_ne_zero : (1 : ℕ) ≠ 0 := by
  intro h
  rw [one_eq_succ_zero] at h
  apply Nat.succ_ne_zero at h
  exact h

theorem _zero_ne_one : (0: ℕ) ≠ 1 := by
  intro h
  symm at h
  apply _one_ne_zero at h
  exact h

  -- symm ---> beautiful...
  -- exact zero_ne_one

theorem two_two_ne_five : Nat.succ (Nat.succ 0) + Nat.succ (Nat.succ 0) ≠ Nat.succ (Nat.succ (Nat.succ (Nat.succ (Nat.succ 0)))) := by
  intro h
  repeat rw [_add_succ, _succ_add] at h
  repeat apply succ_inj at h
  apply _zero_ne_one
  exact h

-- I need more progress to write this...
theorem implication_example (x y : ℕ) (h1: y = 11 - x) (h2: x = y + 5) : y = 3 := by sorry

theorem _add_left_comm (a b c : ℕ) : a + (b + c) = b + (a + c) := by
  rw [← _add_assoc, _add_comm a b, _add_assoc]

theorem _abcd_comm (a b c d : ℕ) : a + b + (c + d) = a + c + d + b := by
  repeat rw [_add_assoc]
  rw [_add_left_comm b, _add_comm b d]

-- beyond level where we have to write down.
theorem _abcdefgh (a b c d e f g h : ℕ) : (d + f) + (h + (a + c)) + (g + e + b) = a + b + c + d + e + f + g + h := by
  -- simp only [_add_assoc, _add_comm] -> it won't find out,
  simp only [_add_comm, _add_left_comm]

macro "simp_add" : tactic => `(tactic|(
  simp only [add_assoc, _add_left_comm, add_comm]
))

theorem _abcdefgh2 (a b c d e f g h : ℕ) : (d + f) + (h + (a + c)) + (g + e + b) = a + b + c + d + e + f + g + h := by
  simp_add

-- Philosophy moment: It is an axiom of Lean that recursion is a valid way to define functions from types such as the naturals.
def succ (n: Nat) := n + 1
def pred : Nat → Nat
  | 0 => 0
  | Nat.succ n => n

theorem pred_succ (a : ℕ) : pred (succ a) = a := by
  rfl

def is_zero : Nat → Bool
  | 0 => True
  | Nat.succ n => False

def is_zero_succ (n : ℕ) : (is_zero (Nat.succ n) = true) = False := by
  induction n with
  | zero =>
    rw [← one_eq_succ_zero]
    trivial
  | succ d hd =>
    trivial

theorem succ_ne_zero (n : ℕ) : Nat.succ n ≠ 0 := by
  intro h
  rw [← is_zero_succ]
  rw [h]
  trivial

theorem succ_ne_succ (m n : ℕ) (h: m ≠ n) : Nat.succ m ≠ Nat.succ n := by
  contrapose! h
  apply succ_inj at h
  exact h

theorem twentyPlusTwentyFourty : (20 : Nat) + 20 = 40 := by
  decide -- its recursive call makes everything fine! (reduce)

theorem two_two_ne_five_2 : (2 : Nat) + 2 ≠ 5 := by
  decide

theorem _add_right_cancel (a b n : Nat) : a + n = b + n → a = b := by
  induction n with
  | zero =>
    intro h
    repeat rw [_add_zero] at h
    exact h
  | succ d ih =>
    intro h
    rw [← _succ_eq_add_one] at h
    repeat rw [_add_succ] at h
    apply succ_inj at h
    apply ih at h
    exact h

theorem _add_left_cancel (a b n : Nat) : n + a = n + b → a = b := by
  rw [_add_comm n a]
  rw [_add_comm n b]
  exact _add_right_cancel a b n

theorem _add_left_eq_self (x y : Nat) : x + y = y → x = 0 := by
  nth_rewrite 2 [← _zero_add y]
  apply _add_right_cancel x 0 y

theorem _add_right_eq_self (x y : Nat) : x + y = x → y = 0 := by
  rw [_add_comm x y]
  exact _add_left_eq_self y x

theorem _add_right_eq_zero (a b : Nat) : a + b = 0 → a = 0 := by
  cases b with
  | zero =>
    exact _add_left_eq_self a 0
  | succ d =>
    intro h
    rw [← _succ_eq_add_one, _add_succ] at h
    apply succ_ne_zero at h
    trivial

theorem _add_left_eq_zero (a b : Nat) : a + b = 0 → b = 0 := by
  rw [_add_comm a b]
  exact _add_right_eq_zero b a
