-- I can confidently say "Learning Category as Programmers' Perspective is cool"

data Frank a b = Frank {frankField :: b a} deriving (Show)

-- kinds
class Tofu t where
    tofu :: j a -> t a j

instance Tofu Frank where
    -- tofu x = Frank x -> syntax sugaring
    tofu x = Frank {frankField = x}

-- Barry :: (*->*) -> * -> * -> *
data Barry t k p = Barry { yabba :: p, dabba :: t k }
instance Functor (Barry a b) where
    fmap f (Barry { yabba=x, dabba=y }) = Barry {yabba=f x, dabba=y}

-- absurd :: Void -> a -> falsity follows anything
tf :: Bool -> Bool
tf _ = undefined -- to keep purity, haskell adds _|_ to each type

num64 :: () -> Int
num64 () = 64

-- **Category-ish things in a nutshell**
--
-- empty category = zero objs + zero morphs
-- free category  = ~like 'free group'
-- thin category  = Hom_c(a, b)=(single or empty) -> pre-order set!
-- Magma > Semi-Group(assoc) > Monoid(unit) > Group(inverse)
--             no id..            ㄴ     category     ㄱ

newtype Set' a = Set { items :: [a] }
unitSet' = Set []
unionSet' (Set x) (Set y) = Set (x++y)

-- Why Magma doesn't exist in Haskell?
instance Semigroup (Set' a) where
    (<>) = unionSet' -- extensional equality
-- It seems like assoc is derivied from Semigroup
instance Monoid (Set' a) where
    mempty = unitSet' -- translates into equality of morphs in the category Hask

-- NOTE: Hom_c(m, m) is "Category"! -> element = morphism + point

-- Kleisli Categories: embellishment of types
type Writer a = (a, String)
-- we called this symbol "fish"
(>=>) :: (a -> Writer b) -> (b -> Writer c) -> (a -> Writer c)
m1 >=> m2 = \x ->
    let (y, ms1) = m1 x
        (z, ms2) = m2 y
    in (z, ms1 ++ ms2)
idFish :: a -> Writer a
idFish x = (x, "")

-- model theory as Haskell perspective
--   T = class / M = instance            $M \models T$
--   Language = ops / Domain = operands
-- 
-- QE(Quantifiable elimination) - 양화사 없이도 동치인 공식으로 바꿀 수 있음
--   -> flat surface theory = easy to tame  
--
-- L(A) := L U {c_a | a in |A|}

main :: IO ()
main = do
    print $ Frank {frankField = Just "Haha"}
    print $ ((tofu (Just "Haha")) :: Frank String Maybe)
    -- print $ Frank {frankField = Maybe Int}
