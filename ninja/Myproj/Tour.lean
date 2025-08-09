namespace BasicFunctions
-- https://lean-lang.org/documentation/1900-1-1-a-tour-of-lean/
--    Very Similar with lambda calculus philosophy!
-- def square x := x * x + 0 -- it complains if only give "x*x" -> type infer...
def square (x: Nat) : Nat := x * x
def result1 := square 1
#eval result1
def plusOne x := x + 1
def add x y := x + y + 0

-- Programming Paradigm
--    명령형(절차지향, 객체지향) / 선언형(함수형)
--    -> Explain "What" to do instead of "How"

-- First-class and higher-order function -> just as d/dx operator;
def result2 := add (square 2) (square 3)
def result3 := add (add (add 1 2) 1) 2
#eval result2
#eval result3
#eval println! "The result of add 1 2 1 2 is {result3}"

def sampleFunction2 (x: Nat) := 2 * x * x - x
def result4 := sampleFunction2 (1+3)
#eval result4

def sampleFunction3 (x: Nat) :=
  if x > 100 then
    sampleFunction2 x
  else
    add (sampleFunction2 x) (sampleFunction2 x)
def result5 := sampleFunction3 1 -- 2

end BasicFunctions

def twice (f : Nat → Nat) (a : Nat) :=
  f (f a)
#eval twice (fun x ↦ x + 2) 10
#eval twice (· + 2) 10

theorem twiceAdd2 (a : Nat) : twice (fun x ↦ x + 2) a = a + 4 :=
  -- The proof is by reflexivity. Lean "symbolically" reduces both sides of the equality
  -- until they are identical.
  rfl -- oh!

inductive Weekday where
  | sunday : Weekday
  | monday : Weekday
#check Weekday.sunday
open Weekday
#check sunday

def natOfWeekday (d : Weekday) : Nat :=
  match d with
  | sunday => 1
  | monday => 2
#eval natOfWeekday monday

def isMonday : Weekday → Bool :=
  -- Syntax sugar of 'fun'  + 'match'
  fun
    | monday => true
    | _ => false

instance: ToString Weekday where
  toString (d : Weekday) : String :=
    match d with
    | sunday => "Sunday"
    | monday => "Monday"

#eval toString (sunday, 10)

-- Abelian...
def next : Weekday -> Weekday :=
  fun
    | sunday => monday
    | monday => sunday

def prev : Weekday -> Weekday :=
  fun
    | sunday => monday
    | monday => sunday

theorem nextOfPrevIsIdentity (d: Weekday) : next (prev d) = d := by
  cases d       -- proof by case distinction
  all_goals rfl -- Each case accomplished with rfl

-- Let's start REAL CLASSSSSSS

-- Curry–Howard perspective: Types are dependent on values, propositions(types) -> getting proof(program) type-by-type
--    term style - proof as a lambda expression
--    tactic style - (by intro cases rw simp ...)
-- theorem my_lemma (n: Nat) : n + 0 = n := sorry
theorem my_lemma (n: Nat) : n + 0 = n := by rfl
theorem my_lemma_tac (n: Nat) : n + 0 = n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    calc
      Nat.succ n + 0 = Nat.succ (n+0) := rfl
