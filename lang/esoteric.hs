-- 
-- Haskell is 'Pure functional programmming language'
--   :you don't tell the computer what to do as such but rather you tell it what stuff is. - Learnyouahaskell
-- lazy, statically typed, elegant and concise!
--
import qualified Data.Map as Map

main :: IO ()
-- Purity: same input, always same output
--   I/O -> create new world!
--     IO a = World -> (World, a) # runtime only
doubleMe x = x + x
doubleSmallNum x = if x > 100
  then x
  else x*2
-- use ' in a strict version of a function (one that isn't lazy, e.g. foldl')

-- lists are a homogenous data structure.
--   [1, 2] ++ [3, 4] -> [1..4]
--   1:[2, 3] -> [1, 2, 3] = 1:2:3:[]
--   "Hello, World!" !! 0 -> "H"
test = [1..4]
head_test = head test -- 1
last_test = last test -- 4
init_test = init test -- [1..3]
tail_test = tail test -- [2..4]
length_test = length test
isNull_test = null test
reversed_test = reverse test
take_n_test n = take n test
drop_n_test n = drop n test
is_one_inside_test = 1 `elem` test
-- cycle, repeat, replicate

evens :: [Int] -> [Int]
evens xs = [x | x <- xs, even x]

length' xs = sum [1 | _ <- xs]
enumerate' xs = zip [0..] xs
value_of_enumerate xs = map (snd) xs
rightTriangles = [(a,b,c) | a <- [1..10], b <- [1..10], c <- [1..10], a^2+b^2==c^2]

-- xs = evens (take 10 (cycle [1..4]))
-- xs = filter even (take 10 (cycle [1..4]))
xs = let ys = take 10 (cycle [1..4]) in filter even ys
xxs = map (+ 1) [1, 2, 3]
xxs_ = map (succ) [1, 2, 3]

-- use `function` to make prefix into infix
--   compare x y -> x `compare` y

-- :t head
-- head :: [a] -> a
--   in not capital case, it's actually a type variable!
--   (~generics)
-- we called this type of function as polymorphic functions
--
-- typeclasses
-- :t (==)
-- (==) :: (Eq a) => a -> a -> Bool
--            |
--        restrict!(member of `Eq` class)
-- `elem` :: (Eq a) => a -> [a] -> Bool
-- (1 +) :: (Num a) => a -> a
--
-- show :: (Show a) => a -> String
-- read :: (Read a) => String -> a
--   this is partial funciton! (e.g. read "Hello" :: Int)
--   in pratice, they use String -> Maybe a.
--   + not "parser" instead "Haskell literal deserialize tool" (read (show 1) == 1)
--
-- Enum, Bounded, Num(numeric typeclass being able to act like numbers)
--                ㄴ Integral, Floating
--   fromIntegral :: (Num b, Integral a) => a -> b

factorial :: (Integral a) => a -> a
factorial 0 = 1
factorial n = n * factorial (n-1)

addVec :: (Num a) => (a, a) -> (a, a) -> (a, a)
-- addVec a b = (fst a + fst b, snd a + snd b)
addVec (x1, y1) (x2, y2) = (x1+x2, y1+y2)

head' :: [a] -> a
head' [] = error "Bro"
head' (x:_) = x
length'' :: (Num b) => [a] -> b
length'' [] = 0
length'' (_:xs) = 1+length'' xs

capital :: String -> String
capital "" = "Empty"
captial all@(x:xs) = "First of " ++ all ++ " is " ++ [x]

isEven x
  | x `mod` 2 == 0 = "Wow"
  | otherwise = "Good"

prime_factor n = [ x | x <- [1..n], n `mod` x == 0]
isPerfect n = sum (init (prime_factor n)) == n
perfects = [ x | x <- [1..], isPerfect x ]

-- Thinking recursive.
--   :how we can work out very concise and elegant solutions to problems by thinking recursively.
--   ㄴ declare what something is instead of declaring how you get it.
replicate' :: (Num i, Ord i) => i -> a -> [a]
replicate' n x
  | n <= 0 = []
  | otherwise = x:replicate' (n-1) x
take' :: (Num i, Ord i) => i -> [a] -> [a]
take' n _
  | n <= 0 = []
take' _ [] = []
take' n (x:xs) = x:take' (n-1) xs
reverse' :: [a] -> [a]
reverse' [] = []
reverse' (x:xs) = reverse' xs ++ [x] -- this is why randomly order in N isn't well-ordered set! (0>1>2>...)

quick :: (Ord a) => [a] -> [a]
quick [] = []
quick (x:xs) =
  let smaller = quick [a | a <- sorted, a <= x]
      bigger = quick [a | a <- sorted, a > x]
  in smaller ++ [x] ++ bigger
  where sorted = quick(xs)

-- fixed-point combinator in Haskell!
step :: (Int -> Int) -> (Int -> Int)
step f = \n -> if n == 0 then 1 else n * f (n-1)
factorial' n
  | n == 0 = 1
  | otherwise = n * factorial' (n-1)
-- step factorial = factorial -> fixed-point!
-- but is it unique?
--   -> Haskell give a shit on `least fixed point`
-- in math, Banach thm or domain theory(?)
fix :: (a -> a) -> a -- it gives a function satisfying step f = f
fix f = f (fix f) 
-- fix f = let x = f x in x
factorial'' n = fix step n

-- corecursive
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Curried-form: how function takes more than one parameters?
max' :: (Ord a) => a -> a -> a -- a -> (a -> a)
max' x y = if x > y then x else y
isPerfect' = (`elem` (take 3 perfects))

applyTwice :: (a -> a) -> a -> a
applyTwice f x = f (f x)

zipWith' :: (a -> b -> c) -> [a] -> [b] -> [c]
zipWith' _ [] _ = []
zipWith' _ _ [] = []
zipWith' f (x:xs) (y:ys) = f x y : zipWith' f xs ys
squares = zipWith' (*) [1..9] [1..9]
flip' :: (a -> b -> c) -> (b -> a -> c)
flip' f = g
  where g x y = f y x -- f y x = f x y
divide_two = zipWith' (flip' div) [2, 2..] [2, 4, 6, 8, 10]

take_first_word = takeWhile (/= ' ')
-- Collatz sequence!
chain :: (Integral a) => a -> [a]
chain 1 = [1]
chain n
  | even n = n:chain (n `div` 2)
  | odd n = n:chain (n*3 + 1)
longChains = map head (filter isLong (map chain [1..100]))
  where isLong xs = length xs > 15
gugu = [map op [1..9] | op <- map (*) [1..9]]
flip'' f = \x y -> f y x -- \x y = \x -> \y

-- foldl f z (x:xs) = foldl f (f z x) xs
--   -> accum first! g (g (g (g ...))) first
-- foldr f z (x:xs) = f x (foldr f z xs)
--   -> f 1 (f 2 (f 3 (f ...)))
--
-- dealing with infinite list
--   ㄴfoldl: fail (return anything)
--   ㄴfoldr: maybe (map, filter, takeWhile..)
sum'' :: (Num a) => [a] -> a
sum'' = foldl (+) 0
elem' :: (Eq a) => a -> [a] -> Bool
elem' y = foldl (\acc x -> if x == y then True else acc) False
map' :: (a -> b) -> [a] -> [b]
map' f xs = foldr (\x acc -> f x : acc) [] xs

-- scan = report fold result in a form of list
sqrtSums :: Int
sqrtSums = length (takeWhile (<1000) (scanl1 (+) (map sqrt [1..]))) + 1 -- filter doesn't work on infinite lists.

-- function applications
--
-- $ -> work as parameter register
--   in python, we have simlilar one, `functools.partial`
-- (.) :: (b->c) -> (a->b) -> a -> c
--   f . g = \x -> f (g x)
trick0 = map ($ 3) [(4+), (10*), (^2), sqrt]
fn0 x = (1/) ((1+) ((^2) x)) -- arctan x = 1/(1+x^2)
fn0' = (1/) . (1+) . (^2)

-- import Data.List (nub, sort)
-- import Data.List hiding (nub)
-- import qualified Data.Map as M


-- ***ADT(Algebraic Data Type)***
--   construct new data type just as algebra does
--
-- data Bool' = False | True -- how to define type
data Point = Point Float Float deriving (Show)
data Shape = Circle Point Float | Rectangle Point Point deriving (Show)
surface :: Shape -> Float
surface (Circle _ r) = 3.14 * r ^ 2 -- come up with (x:xs), we use pattern matching against constructors!
surface (Rectangle (Point x1 y1) (Point x2 y2)) = (abs $ x2 - x1) * (abs $ y2 - y1)
nudge :: Shape -> Float -> Float -> Shape
nudge (Circle (Point x y) r) a b = Circle (Point (x+a) (y+b)) r
nudge (Rectangle (Point x1 y1) (Point x2 y2)) a b = Rectangle (Point (x1+a) (y1+b)) (Point (x2+a) (y2+b))
originPt = Point 0 0
unitCircle = Circle originPt 1

data Car = Car {company :: String, shape:: Shape} deriving (Show)
cybertruck = Car {company="Tesla", shape=Rectangle originPt (Point 1 1)}

-- Type constructor!!
data Maybe' a = Nothing' | Just' a
-- data (Ord k) => Map k v = ... (cool)

-- Derived instances
--   typecalss=interface defining some behaviour
--   type=instance of typeclass
-- 
-- ex) Real = 완비 순서체 deriving (Ord,  Num)
data Day' = MON | TUE | WED | TUR | FRI | SAT | SUN
  deriving (Eq, Ord, Show, Read, Bounded, Enum) -- 0 | 1 | ...
type Days = [Day'] -- type synonyms

data Status = UP | DOWN deriving (Show, Eq)
type Content = String
type Sockets = Map.Map Int (Status, Content)
ping :: Int -> Sockets -> Either String Content
ping address map =
  case Map.lookup address map of
    Nothing -> Left "Stop DDOS!"
    Just (status, content) -> if status /= DOWN
      then Right content
      else Left "Wait a bit"

-- Recursive type declaration
-- data List' a = Empty | Cons a (List a) deriving (Show, Read, Eq, Ord)
--                        Cons { listHead :: a, listTail :: List a}
infixr 5 :-: -- Fixity declaratioions: when we define functions as operators
--               ㄴ ... < infixl 6(+) < infixl 7(*)
data List' a = Empty | a :-: (List' a) deriving (Show, Read, Eq, Ord)
infixr 5 .++
(.++) :: List' a -> List' a -> List' a
Empty .++ ys = ys
(x :-: xs) .++ ys = x :-: (xs .++ ys)
merrych_list = 12 :-: 25 :-: Empty

data Tree a = EmptyTree | Node a (Tree a) (Tree a) deriving (Show, Read, Eq)
singleton :: a -> Tree a
singleton x = Node x EmptyTree EmptyTree

treeInsert :: (Ord a) => a -> Tree a -> Tree a
treeInsert x EmptyTree = singleton x
treeInsert x (Node a left right)
  | x == a = Node x left right
  | x < a = Node a (treeInsert x left) right
  | x > a = Node a left (treeInsert x right)

treeElem :: (Ord a) => a -> Tree a -> Bool
treeElem x EmptyTree = False
treeElem x (Node a left right)
  | x == a = True
  | x < a = treeElem x left
  | x > a = treeElem x right

nums = [4,3,2,6,1,2,9,7]
numsTree = foldr treeInsert EmptyTree nums

-- Typeclassessssssss
--   check class interface with :info
--
-- class Eq a where 
--   (==) :: a -> a -> Bool
--   (/=) :: a -> a -> Bool
--   x == y = not (x /= y)
--   x /= y = not (x == y)
-- 
-- we don't need to implement function body, just specify it
data Animal = Tiger | Bear
instance Eq Animal where
  Tiger == Tiger = True
  Bear == Bear = True
  _ == _ = False
instance Show Animal where
  show Tiger = "Tiger"
  show Bear = "Bear"

instance (Eq m) => Eq (Maybe m) where -- Eq Maybe nono, it's type constructor
  Just x == Just y = x == y
  Nothing == Nothing = True
  _ == _ = False

-- Functor Typeclass
--   for things that can be mapped over.
-- 
-- class Functor f where
--   fmap :: (a->b) -> f a -> f b
-- 
-- instance Functor [] where
--  fmap = map
instance Functor Tree where -- be careful if it destroys bintree.
  fmap f EmptyTree = EmptyTree
  fmap f (Node x leftsub rightsub) = Node (f x) (fmap f leftsub) (fmap f rightsub)

-- what's the type of type constructor? (it feels like function!)
--   :k Maybe ====> Maybe :: * -> *
--
data Frank a b = Frank {frankField :: b a} deriving (Show) -- * -> (* -> *) -> *
-- Frank {frankField = "abc"} : Frank Char []
class Tofu t where
  tofu :: j a -> t a j -- t :: * -> (* -> *) -> *
instance Tofu Frank where
  tofu x = Frank x

main = do
    print xs
    print xxs_
    print (fibs !! 4)
    print (take 3 (enumerate' [0,2..]))
    print (value_of_enumerate (enumerate' "Hello World"))
    print rightTriangles
    print (isEven 2)
    print (take 3 perfects)
    print (quick [4, 2, 3, 1])
    print (factorial'' 4)
    print (take_first_word "hello, world")
    print longChains
    print ((map (*) [0..] !! 4) 5)
    print (let ildan = gugu !! 0 in ildan)
    print (take 10 (map (*2) [1..]))
    print (fn0 1 == fn0' 1)
    print $ surface $ unitCircle
    print $ unitCircle
    print $ company cybertruck
    print $ (read (show MON) :: Day')
    print $ [MON ..]
    print merrych_list
    print numsTree
