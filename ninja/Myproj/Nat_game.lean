import Mathlib.Tactic

theorem isMe (x q : Nat) : 37 * x + q = 37 * x + q := by rfl
theorem isMeWoHypothesis (x y: Nat) (h1: y = x + 7) : 2*y=2*(x+7) := by
  rw [h1]

theorem one_eq_succ_zero : 1 = Nat.succ 0 := by rfl
theorem two_eq_succ_one : 2 = Nat.succ 1 := by rfl

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
