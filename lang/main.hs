-- import qualified Data.Set as Set
import qualified Data.Map as Map
import Data.List (intercalate)
import qualified Data.Set as Set
import Data.Char (ord, chr)

data Nat = Z | S Nat

toInt :: Nat -> Int
toInt n = case n of
    Z -> 0
    S m -> 1 + toInt m
fromInt :: Int -> Nat
fromInt n = case n of
    0 -> Z
    otherwise -> S (fromInt $ n-1)

add :: Nat -> Nat -> Nat
add n Z = n
add n (S m) = S (add n m)

zero = Z
three = S (S (S Z))
four = fromInt 4

data NonEmpty a = a :| [a] deriving (Show, Eq)
headNe :: NonEmpty a -> a
headNe (h:|tail) = h
tailNe :: NonEmpty a -> a
tailNe (h:|tail) = case tail of
    (t:ttail) -> tailNe (t:|tail)
    otherwise -> h

toList :: NonEmpty a -> [a]
toList (h:|tail) = case tail of
    (t:ttail) -> h:toList (t:|ttail)
    otherwise -> [h]

safeIndex :: [a] -> Int -> Maybe a
safeIndex (x:xs) 0 = Just x
safeIndex (x:[]) _ = Nothing
safeIndex (x:xs) n
    | n < 0 = safeIndex xs (n-1)
    | n > 0 = Nothing

data ParenError = UnexpectedClose | UnclosedOpen Int deriving (Show, Eq)
checkParens :: String -> Either ParenError ()
checkParens "" = Right ()
-- checkParens dump = case checked of
--     Left UnexpectedClose -> Left UnexpectedClose
--     otherwise ->
--         case last dump of
--             '('       -> case checked of
--                             Left (UnclosedOpen n) -> Left (UnclosedOpen (n+1))
--                             otherwise -> Left (UnclosedOpen 1)
--             ')'       -> case checked of
--                             Left (UnclosedOpen n) -> if n > 1 then Left (UnclosedOpen (n-1))
--                                                 else if n == 1 then Right () else Left UnexpectedClose
--                             otherwise -> Left UnexpectedClose
--             otherwise -> checked
--     where checked = checkParens (init dump)
checkParens s = go 0 s
    where
        go n []
            | n == 0    = Right ()
            | otherwise = Left  (UnclosedOpen n)
        go n (c:cs)
            | c == '('  = go (n+1) cs
            | c == ')'  = if n == 0 then Left UnexpectedClose else go (n-1) cs
            | otherwise = go n cs

data Expr
    = Lit Int
    | Add Expr Expr
    | Mul Expr Expr
    | Neg Expr

eval :: Expr -> Int
eval expr = case expr of
    Lit n -> n
    Add e1 e2 -> (eval e1) + (eval e2)
    Mul e1 e2 -> (eval e1) * (eval e2)
    Neg e     -> -(eval e)

sampleExpr = Add (Neg (Lit 1)) (Mul (Add (Neg (Lit 1)) (Lit 3)) (Lit 2))

parent :: (Expr -> String) -> Expr -> String
parent f s = case s of
    Lit n -> f s
    otherwise -> "(" ++ f s ++ ")"
pretty :: Expr -> String
pretty expr = case expr of
    Lit n -> show n
    Add e1 e2 -> (pretty e1) ++ "+" ++ (pretty e2)
    Mul e1 e2 -> (parent pretty e1) ++ "*" ++ (parent pretty e2)
    Neg e     ->  "-" ++ parent pretty e

digitToInt x = ord x - ord '0'
isDigit =  (\x -> x >= 0 && x < 10) . digitToInt

solveRPN :: (Num a, Read a) => String -> a
solveRPN = head . foldl parse [] . words
    where
        parse (x:y:ys) "*" = (x*y):ys
        parse (x:y:ys) "-" = (x-y):ys
        parse (x:y:ys) "+" = (x+y):ys
        parse xs numberString = read numberString:xs

-- Json Parser

data J
    = JNull | JBool Bool | JNum Double | JStr String | JArr [J] | JObj (Map.Map String J) 
    deriving (Show, Eq)

data Op = OpGet | OpUpdate deriving (Show, Eq)
data Step = Key String | Index Int deriving (Show, Eq)

type JPath = [Step]

data JErrKind
    = NotObject J
    | NotArray J
    | MissingKey String
    | IndexOutOfBounds { idx :: Int, len :: Int }
    deriving (Show, Eq)

data JError = JError 
    { op    :: Op
    , kind  :: JErrKind
    } deriving (Show, Eq)

singleton :: String -> J -> J
singleton k v = JObj (Map.singleton k v)

get :: J -> JPath -> Either JError J
get j [] = Right j
get j (x:xs) = case x of
    Key k   ->
        case j of
            JObj map_ ->
                case Map.lookup k map_ of
                    Just nextj -> get nextj xs
                    Nothing    -> Left JError {op=OpGet, kind=MissingKey k }
            _ -> Left JError {op=OpGet, kind=NotObject j }
    Index i -> 
        case j of
            JArr ys -> 
                case safeIndex ys i of
                    Just nextj -> get nextj xs
                    Nothing    -> Left JError {op=OpGet, kind=IndexOutOfBounds {idx=i, len=length ys} }
            _ -> Left JError {op=OpGet, kind=NotArray j }


replaceNth :: Int -> a -> [a] -> [a]
replaceNth n a xs
    | n == 0     = a : drop 1 xs
    | n > 0      = take n xs ++ [a] ++ drop (n + 1) xs
    | otherwise  = xs

update :: J -> JPath -> J -> Either JError J
update j [] val = Right val
update j (x:xs) val = case x of
    Key k   ->
        case j of
            JObj map_ ->
                case Map.lookup k map_ of
                    Just nextj -> case update nextj xs val of
                        Right x -> Right (JObj (Map.insert k x map_))
                        Left x -> Left x 
                    Nothing    -> case length xs of
                        0 -> Right (JObj (Map.insert k val map_))
                        _ -> Left JError {op=OpUpdate, kind=MissingKey k }
            _ -> Left JError {op=OpUpdate, kind=NotObject j }
    Index i -> 
        case j of
            JArr ys -> 
                case safeIndex ys i of
                    Just nextj -> case update nextj xs val of
                        Right x -> Right (JArr (replaceNth i x ys))
                        Left x -> Left x 
                    Nothing    -> case length xs of
                        0 -> Right (JArr (replaceNth i val ys))
                        _ -> Left JError {op=OpUpdate, kind=IndexOutOfBounds {idx=i, len=length ys} }
            _ -> Left JError {op=OpUpdate, kind=NotArray j }

json = singleton "hello" (JStr "world")
updated = let x = (update json [Key "hi"] (JArr [JNum 1, JNum 2])) in
    case x of
        Right x -> x

encode :: J -> String
encode j = case j of
    JNull -> "null"
    JBool b -> show b
    JNum n -> show n
    JStr s -> show s
    JArr arr -> "[" ++ intercalate ", " (map encode arr) ++ "]" 
    JObj map_ -> "{" ++ (tail . tail) (Map.foldlWithKey (\acc k a -> acc++", "++show k++": "++encode a) "" map_)  ++ "}"

strip :: String -> String
strip = f . f 
    where f = reverse . dropWhile (/=' ')

wordsWhen :: (Char -> Bool) -> String -> [String]
wordsWhen p s =  case dropWhile p s of
                      "" -> []
                      s' -> w : wordsWhen p s''
                            where (w, s'') = break p s'

splitOn :: Char -> String -> [String]
splitOn t = wordsWhen (/=t)

listToPair :: [a] -> (a, a)
listToPair [x, y] = (x, y)
listToPair _      = error "List must contain exactly two elements"

splitComma :: String -> [String]
splitComma = splitOn ','

splitRecord :: String -> (String, String)
splitRecord = listToPair . splitOn ':' 

safeBody :: [a] -> Maybe [a]
safeBody xs
    | length xs >= 2 = Just ((tail . init) xs)
    | otherwise      = Nothing

decode :: String -> J

decode s = let ss = strip s in case head ss of
    '{' -> case last ss of
        '}' -> JObj (Map.map decode $ Map.fromList $ map splitRecord (splitComma ss))
        _ -> JNull
    '[' -> case last ss of
        ']' -> JArr (map decode $ splitComma ss)
        _ -> JNull
    _ -> case ss of
        "\"null\"" -> JNull
        "\"true\"" -> JBool True
        "\"false\"" -> JBool False

main :: IO ()
main = do
    print $ toInt $ fromInt 4
    print $ toInt $ add three three

    print $ toList $ 1:|[2, 3]

    print $ safeIndex [1, 2] (-1)
    print $ safeIndex [1, 2] 2

    print $ checkParens "()(((())))()(("

    print $ pretty sampleExpr
    print $ eval sampleExpr
    print $ "Solve: (1+2)*3 is " ++ show (solveRPN "1 2 + 3 *")

    print $ json
    print $ get json [(Key "hello")]

    print $ updated
    print $ encode updated
