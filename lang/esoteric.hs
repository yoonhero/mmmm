-- 
-- Haskell is 'Pure functional programmming language'
--   :you don't tell the computer what to do as such but rather you tell it what stuff is. - Learnyouahaskell
-- lazy, statically typed, elegant and concise!
--

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

fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

main = do
    print xs
    print xxs_
    print (fibs !! 4)
    print (take 3 (enumerate' [0,2..]))
    print (value_of_enumerate (enumerate' "Hello World"))
    print rightTriangles
    print (isEven 2)
    print (take 3 perfects)
