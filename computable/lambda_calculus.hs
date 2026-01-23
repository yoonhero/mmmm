{-# LANGUAGE RankNTypes #-}

module Lambda where
import Prelude hiding (and, or, succ, add, mul, sub, fst, scd, sub)

-- Logics
newtype LBool = LBool { runLBool :: forall a. a->a->a }

trueL :: LBool
trueL = LBool (\x y -> x)
falseL :: LBool
falseL = LBool (\x y -> y)

instance Eq LBool where
    (LBool f1) == (LBool f2) = f1 True False == f2 True False

instance Show LBool where
    show b = if b == trueL then "TRUE" else "FALSE"

ifThen :: LBool -> a -> a -> a
ifThen (LBool b) x y = b x y

and :: LBool -> LBool -> LBool
and (LBool x) y = x y falseL

or :: LBool -> LBool -> LBool
or (LBool x) y = x trueL y

-- Pair && List
newtype Pair a b = Pair { runPair :: forall r. (a->b->r)->r }

makePair :: a -> b -> Pair a b
makePair x y = Pair (\f -> f x y)

fst :: Pair a b -> a
fst (Pair p) = p (\x y -> x) -- In essence, it's "TRUE"

scd :: Pair a b -> b
scd (Pair p) = p (\x y -> y)

-- Natural Number!
newtype Nat = Nat { runNat :: forall a. (a->a)->a->a }

zero :: Nat
zero = Nat (\f x -> x)
isZero :: Nat -> LBool
isZero (Nat n) = n (\_ -> falseL) trueL
succ :: Nat -> Nat
succ (Nat n) = Nat (\f x -> f (n f x))
one = succ zero
two = succ one
three = succ two

toInt :: Nat -> Int
toInt (Nat n) = n (+1) 0

instance Show Nat where
    show = show . toInt

add :: Nat -> Nat -> Nat
add (Nat n) (Nat m) = Nat (\f x -> n f (m f x))
mul :: Nat -> Nat -> Nat
mul (Nat n) (Nat m) = Nat (\f x -> n (m f) x)

_prec_f :: Pair Nat Nat -> Pair Nat Nat
_prec_f p = makePair (scd p) (succ $ scd p)
prec :: Nat -> Nat
prec (Nat n) = fst $ n _prec_f $ makePair zero zero
sub :: Nat -> Nat -> Nat
sub n (Nat m) = m prec n

instance Eq Nat where
    n == m = and (isZero $ sub n m) (isZero $ sub m n) == trueL

instance Ord Nat where
    n <= m = (isZero $ sub n m) == trueL

newtype Z = Z { runZ :: Pair Nat Nat }

mkZ :: Nat -> Nat -> Z
mkZ a b = Z (makePair (a b))

-- normPair :: Pair Nat Nat -> Pair Nat Nat
-- normPair p =  

main :: IO ()
main = do
    print $ trueL
    print $ trueL == falseL

    print $ ifThen trueL trueL falseL
    print $ and trueL falseL

    print $ show one
    print $ show $ mul three three
    print $ show $ sub three two
    print $ "Two is equal two three: " ++ (show $ three == two)
    print $ "2 < 3 is " ++ show (two < three)
    print $ "3 < 1 is " ++ show (three < one)

