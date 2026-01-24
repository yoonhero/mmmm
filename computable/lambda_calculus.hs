{-# LANGUAGE RankNTypes #-}

module Lambda where
import Prelude hiding (and, or, succ, add, mul, sub, fst, scd, sub, append, nil, length, (!!), true, false, not, (<=), (<), min, max, map, (:), reverse, head)

-- Logics
newtype LBool = LBool { runLBool :: forall a. a->a->a }

true :: LBool
true = LBool (\x y -> x)
false :: LBool
false = LBool (\x y -> y)
not :: LBool -> LBool
not (LBool b) = b false true

class LEq a where
    (===) :: a -> a -> LBool
    infix 4 ===

    (/==) :: a -> a -> LBool
    x /== y = not (x === y)
    infix 4 /==

instance Eq LBool where
    (LBool f1) == (LBool f2) = f1 True False == f2 True False

toBool :: LBool -> Bool
toBool b = b == true

instance Show LBool where
    show b = if b == true then "TRUE" else "FALSE"

ifThen :: LBool -> a -> a -> a
ifThen (LBool b) x y = b x y

and :: LBool -> LBool -> LBool
and (LBool x) y = x y false

or :: LBool -> LBool -> LBool
or (LBool x) y = x true y

class LEq a => LOrd a where
    (<=) :: a -> a -> LBool
    infix 4 <=

    (<)  :: a -> a -> LBool
    x < y = and (x <= y) (not $ y <= x)
    infix 4 <
    
    (>=) :: a -> a -> LBool
    x >= y = not (x < y)
    (>)  :: a -> a -> LBool
    x > y = not (x <= y)

    min :: a -> a -> a
    min x y = ifThen (x <= y) x y
    max :: a -> a -> a
    max x y = ifThen (x <= y) y x

-- Pair
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
isZero (Nat n) = n (\_ -> false) true
succ :: Nat -> Nat
succ (Nat n) = Nat (\f x -> f (n f x))
one = succ zero
two = succ one
three = succ two
four = succ three
five = succ four

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

instance LEq Nat where
    n === m = and (isZero $ sub n m) (isZero $ sub m n)

instance LOrd Nat where
    n <= m = isZero $ sub n m

-- List
newtype List n = List { runList :: forall r. (n->r->r)->r->r }

nil :: List n
nil = List (\c h -> h)

cons :: n -> List n -> List n
cons x (List xs) = List (\c h -> xs c (c x h))
uncons :: List n -> List n
uncons li = let (List xs) = li in
    List (\c h -> scd $ xs (\x p -> makePair (succ $ fst p) $ ifThen (fst p === length li) (scd p) (c x $ scd p)) (makePair one h))
append :: List n -> List n -> List n
append (List fst) (List scd) = List (\c h -> fst c (scd c h))
infixr 5 ++.
(++.) = append
--need more thinking
reverse :: List n -> List n
reverse xs = case head xs of
    Just x  -> x `cons` reverse (uncons xs) 
    Nothing -> xs

length :: List n -> Nat
length (List xs) = xs (\_ acc -> add one acc) zero 
elem :: LEq a => a -> List a -> LBool
elem n (List xs) = xs (\el prev -> ifThen (n===el) true prev) false
head :: List a -> Maybe a
head (List xs) = xs (\x _ -> Just x) Nothing
tail = uncons
infixr 5 !!
(!!) :: LEq a => List a -> Nat -> Maybe a
(!!) list n = let (List xs) = list in
    scd $ xs (\el p -> makePair (prec $ fst p) (ifThen ((fst p)===one) (Just el) (scd p))) (makePair (sub (length list) n) Nothing)

range :: Nat -> Nat -> List Nat
range n m = let (Nat x) = sub m n in
    scd $ x (\acc -> makePair (succ $ fst acc) (cons (fst acc) (scd acc))) (makePair n nil)

map :: (a->b) -> List a -> List b
map f (List xs) = List (\c h -> xs (\a acc -> c (f a) acc) h)
-- zipWith :: (a->b->r) -> List a -> List b -> List r
-- zipWith f (List xs) (List ys) = 
-- fib = zero `cons` one `cons` (zipWith add fib $ tail fib)

instance (Show n) => Show (List n) where
    show (List xs) = "[" ++ (xs (\el acc -> if acc == "" then (show el) else (show el) ++ ", " ++ acc) "") ++ "]"

-- Integer number
newtype Z = Z { runZ :: Pair Nat Nat }

mkZ :: Nat -> Nat -> Z
mkZ a b = Z (makePair a b)

normZ :: Z -> Z
normZ (Z p)
    | (p2 <= p1) == true  = mkZ (sub p1 p2) zero
    | otherwise           = mkZ zero (sub p2 p1)
    where p1 = fst p
          p2 = scd p

addZ :: Z -> Z -> Z
addZ (Z p1) (Z p2) = mkZ (add (fst p1) (fst p2)) (add (scd p1) (scd p2))
mulZ :: Z -> Z -> Z
mulZ (Z p1) (Z p2) = mkZ (add (mul (fst p1) (fst p2)) (mul (scd p1) (scd p2))) (add (mul (fst p1) (scd p2)) (mul (scd p1) (fst p2))) 
subZ :: Z -> Z -> Z
subZ (Z p1) (Z p2) = mkZ (add (fst p1) (scd p2)) (add (scd p1) (fst p2))

instance LEq Z where
    i === j = fst(ijSub) === scd(ijSub)
        where (Z ijSub) = subZ i j 

instance Show Z where
    show z
        | toBool (p2 === zero) = show p1
        | toBool (p1 === zero) =  "-" ++ (show p2)
        | otherwise  = show zero
        where (Z p) = normZ z
              p1 = fst p
              p2 = scd p

instance LOrd Z where
    x <= y = let (Z p) = normZ $ subZ x y in fst p === zero

-- Q = Pair Z Z
-- all goes same

main :: IO ()
main = do
    print $ true
    print $ true == false
    print $ ifThen true true false
    print $ and true false

    print $ show one
    print $ show $ mul three three
    print $ show $ sub three two
    print $ "Two is equal two three: " ++ (show $ three === two)
    print $ "2 < 3 is " ++ show (two < three)
    print $ "3 < 1 is " ++ show (three < one)

    print $ (++) "-1 < -3 is " $ show $ (mkZ two three ) <= (mkZ zero three)
    print $ mulZ (mkZ two three) (mkZ zero two)
    print $ (mkZ one zero) === (mkZ three two)

    print $ cons zero (cons two nil) !! two
    print $ cons zero (cons two nil) !! one
    print $ cons zero (cons two nil)
    print $ range zero three
    print $ uncons $ range zero three
    print $ reverse $ range zero five
