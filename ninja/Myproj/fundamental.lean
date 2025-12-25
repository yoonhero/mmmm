-- The world of type theory
-- Prop       -> Types
-- Pf         -> Terms of Type
-- True Prop  -> Non-empty Type
-- False Prop -> Empty Type
-- "Implies"  -> Function Type
-- "And"      -> Product Type
-- "Exists"   -> Dependent Product Type
-- "For all"  -> Dependent Function Type

-- Universe layer
#check Type -- `Type` refers to 'type of types'
#check Type 0
#check Type 1
#check Type 2
-- without universe we get Russel Paradox!
--   for instance, we might set R := { X : Type | X ∉ X}
--   Type이 자기 자신을 포함할 수 있다면.
-- hierarchy is required for let set.
--   def allTypes : List Type := ?
-- you can come up with Turing's approach
--   Halting Problem은 결국 한 단계 높은 집합이 필요함.
--   countable: ℵ / non-countable: 2^ℵ
structure Magma where
  carrier : Type
  mul : carrier → carrier → carrier
#check Magma -- +1 level as it contain `Type`

#check fun x => x
-- ∀ x : A, B ≃ A → B (if B isn't dependent on x)

-- Prop is Type
#check Prop
#check True
#check True.intro
-- Prop is proof-irrelevant, it cares the only existence.
-- If Type is also irrelevant, true false : Bool it's non-sense.
-- Prop(can u?) vs. Data

-- 
#check Eq
-- inductive _Eq (a : α) : α → Prop
-- | refl : _Eq a
#check rfl


