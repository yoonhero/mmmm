import Mathlib.Tactic

-- theorem assoc (a b c: Nat) : a+b+c = (a+b)+c := by rfl (l2r)

inductive _Tree (α : Type u) where
  | leaf
  | node (left : _Tree α) (x : α) (right : _Tree α)

def _Tree.map (f : α → β) : _Tree α → _Tree β
  | _Tree.leaf => _Tree.leaf
  | _Tree.node l x r => _Tree.node (_Tree.map f l) (f x) (_Tree.map f r)

def fibs : Nat → Nat
  | 0 => 0
  | 1 => 1
  | .succ (.succ m) => -- leading-dot notation
    fibs m + fibs (Nat.succ m)

def fibsAux : Nat → Nat → Nat → List Nat
  | 0, _, _ => []
  | Nat.succ n, a, b => a :: fibsAux n b (a+b)

#eval fibs 10
#eval fibsAux 10 0 1
#eval fibs $ 5 + 5
#eval fibs <| 5+5

variable {K V: Type*}
variable [Field K]
variable [AddCommGroup V] [Module K V]

#check V
