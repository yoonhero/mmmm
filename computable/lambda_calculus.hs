{-# LANGUAGE RankNTypes #-}

module Lambda where
import Prelude hiding (and, or, succ, add, mul, sub, fst, scd, sub, append, nil, length, (!!), true, false, not, (<=), (<), min, max, map, (:), reverse, head, mod, filter, tail, zip, zipWith, take, takeWhile)

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
nine = mul three three
n81 = mul nine nine

toInt :: Nat -> Int
toInt (Nat n) = n (+1) 0

instance Show Nat where
    show = show . toInt

add :: Nat -> Nat -> Nat
add (Nat n) (Nat m) = Nat (\f x -> n f (m f x))
mul :: Nat -> Nat -> Nat
mul (Nat n) (Nat m) = Nat (\f x -> n (m f) x)

_precF :: Pair Nat Nat -> Pair Nat Nat
_precF p = makePair (scd p) (succ $ scd p)
prec :: Nat -> Nat
prec (Nat n) = fst $ n _precF $ makePair zero zero
sub :: Nat -> Nat -> Nat
sub n (Nat m) = m prec n
mod :: Nat -> Nat -> Nat
mod n@(Nat fn) m = fn (\x -> ifThen (x < m) x $ sub x m) n -- this isn't wise way.
-- five a way to implement it using Y-Combinator.

instance LEq Nat where
    n === m = and (isZero $ sub n m) (isZero $ sub m n)

instance LOrd Nat where
    n <= m = isZero $ sub n m

-- List = not evaluated `foldr` in Haskell
newtype List n = List { runList :: forall r. (n->r->r)->r->r }

nil :: List n
nil = List (\c h -> h)

cons :: n -> List n -> List n
cons x (List xs) = List (\c h -> xs c (c x h))
uncons :: List n -> List n
uncons li@(List xs) =
    List (\c h -> scd $ xs (\x p -> makePair (succ $ fst p) $ ifThen (fst p === zero) (scd p) (c x $ scd p)) (makePair zero h))
makeList = flip cons nil
push :: n -> List n -> List n
push x (List xs) = List (\c h -> c x (xs c h))
append :: List n -> List n -> List n
append (List fst) (List scd) = List (\c h -> scd c (fst c h))
infixr 5 ++.
(++.) = append
--need more thinking
reverse :: List n -> List n
reverse xs = case head xs of
    Just x  -> push x $ reverse (uncons xs)
    Nothing -> xs

sum :: List Nat -> Nat
sum (List xs) = xs (\x acc -> add x acc) zero
length :: List n -> Nat
length (List xs) = xs (\_ acc -> add one acc) zero 
elem :: LEq a => a -> List a -> LBool
elem n (List xs) = xs (\el prev -> ifThen (n===el) true prev) false
last :: List a -> Maybe a
last (List xs) = xs (\x _ -> Just x) Nothing
head :: List a -> Maybe a
head list@(List xs) =
    scd $ xs (\x p -> makePair (succ $ fst p) $ ifThen (fst p === zero) (Just x) (scd p)) (makePair zero Nothing)
tail = uncons
infixr 5 !!
(!!) :: LEq a => List a -> Nat -> Maybe a
(!!) list@(List xs) n =
    scd $ xs (\el p -> makePair (succ $ fst p) (ifThen (fst p === n) (Just el) (scd p))) (makePair zero Nothing)

range :: Nat -> Nat -> List Nat
range n m = let (Nat x) = sub m n in
    scd $ x (\acc -> makePair (succ $ fst acc) (push (fst acc) (scd acc))) (makePair n nil)
rangeD :: Nat -> Nat -> Nat -> List Nat
rangeD n m d = let (Nat x) = sub m n in
    scd $ x (\acc -> ifThen (fst acc < m) (makePair (add d $ fst acc) (push (fst acc) (scd acc))) acc) (makePair n nil) 

map :: (a->b) -> List a -> List b
map f (List xs) = List (\c h -> xs (\a acc -> c (f a) acc) h)

filter :: (LOrd a) => (a -> LBool) -> List a -> List a
filter f (List xs) = xs (\x acc -> ifThen (f x) (push x acc) acc) nil

zip :: List a -> List b -> List (Pair a b)
zip xs ys =
    case (head xs, head ys) of
        (Just hx, Just hy) -> cons (makePair hx hy) $ zip (tail xs) (tail ys)
        _                  -> nil
zipWith :: (a->b->r) -> List a -> List b -> List r
zipWith f xs ys = let (List zs) = zip xs ys in
    List (\c h -> zs (\x acc -> c (f (fst x) (scd x)) acc) h)

take :: Nat -> List a -> List a
take n xs = 
    ifThen (isZero n)
        nil 
        (case head xs of
            Just x  -> cons x $ take (prec n) (tail xs)
            Nothing -> nil)
takeWhile :: (a -> LBool) -> List a -> List a
takeWhile f xs = case head xs of
    Just x  -> ifThen (f x) (cons x $ takeWhile f (tail xs)) nil
    Nothing -> nil
fib = zero `cons` (one `cons` zipWith add fib (tail fib))

instance (Show n) => Show (List n) where
    show (List xs) = "[" ++ xs (\el acc -> if acc == "" then show el else acc ++ ", " ++ show el) "" ++ "]"

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
    i === j = fst ijSub === scd ijSub
        where (Z ijSub) = subZ i j 

instance Show Z where
    show z
        | toBool (p2 === zero) = show p1
        | toBool (p1 === zero) =  "-" ++ show p2
        | otherwise  = show zero
        where (Z p) = normZ z
              p1 = fst p
              p2 = scd p

instance LOrd Z where
    x <= y = let (Z p) = normZ $ subZ x y in fst p === zero

-- Q = Pair Z Z
-- all goes same

-- examples
data Tree a = EmptyTree | Node a (Tree a) (Tree a) deriving (Show, Read)
singleton :: (LOrd a) => a -> Tree a
singleton x = Node x EmptyTree EmptyTree
insertTree :: (LOrd a) => a -> Tree a -> Tree a
insertTree x EmptyTree = singleton x
insertTree x (Node a leftTree rightTree)
    | toBool (x === a) = Node x leftTree rightTree
    | toBool (x < a)   = Node a (insertTree x leftTree) rightTree
    | otherwise        = Node a leftTree (insertTree x rightTree)
treeElem :: (LOrd a) => a -> Tree a -> LBool
treeElem x EmptyTree = false
treeElem x (Node a leftTree rightTree)
    | toBool (x === a) = true
    | toBool (x < a)   = treeElem x leftTree
    | otherwise        = treeElem x rightTree

qsort :: (LOrd a) => List a -> List a
qsort list = case head list of
    Just x  -> let xs = tail list in (qsort $ filter (< x) xs) ++. (makeList x) ++. (qsort $ filter (x <=) xs)
    Nothing -> nil

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
    print $ "81 mod 5 == " ++ show (n81 `mod` five)

    print $ (++) "-1 < -3 is " $ show $ (mkZ two three ) <= (mkZ zero three)
    print $ mulZ (mkZ two three) (mkZ zero two)
    print $ (mkZ one zero) === (mkZ three two)

    print $ cons zero (cons two nil) !! one -- [0, 2][1]
    print $ cons zero (cons two nil)        -- [0, 2]
    print $ range zero three                -- [0, 1, 2]
    print $ rangeD zero n81 nine
    print $ uncons $ range zero three       -- [1, 2]
    print $ reverse $ range zero five       -- [4, 3, 2, 1, 0]
    print $ map (mul three) $ range zero three
    print $ let nums@(List xs) = cons three (cons five (cons zero (cons nine nil))) in xs insertTree EmptyTree
    print $ qsort $ reverse $ range zero three
    print $ filter (<= two) $ range zero three
    -- print $ fib
    print $ take three $ reverse $ range zero n81 -- [80, 79, 78]
    print $ takeWhile (isZero . flip mod three) $ rangeD zero n81 nine