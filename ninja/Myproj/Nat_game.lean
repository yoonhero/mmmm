import Mathlib.Tactic

theorem isMe (x q : Nat) : 37 * x + q = 37 * x + q := by rfl
theorem isMeWoHypothesis (x y: Nat) (h1: y = x + 7) : 2*y=2*(x+7) := by
  rw [h1]

theorem one_eq_succ_zero : Nat.succ 0 = 1 := by rfl
theorem two_eq_succ_one : Nat.succ 1 = 2 := by rfl

theorem addOneisSucc (n : Nat) : Nat.succ n = n + 1 := by
  rw [← one_eq_succ_zero]
  -- rw [← Nat.add_succ]
  -- rw [← Nat.add_zero]

theorem twoPlusTwoIsFuckingFour : (2 : Nat) + 2 = 4 := by
  nth_rewrite 2 [← two_eq_succ_one]
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
