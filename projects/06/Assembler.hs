-- Usage:
-- ./Assembler /path/to/file.asm /path/to/out.hack
module Main where

import System.Environment
import System.IO
import Data.List.Split(splitOn)
import Data.List(isPrefixOf, elemIndex)
import Data.Map(Map)
import Data.Char(intToDigit)
import qualified Data.Map as Map

instructionWidth = 16

symbols :: Map String Integer
symbols = Map.fromList ([("R" ++ show x, x) | x <- [0..15]] ++
                              [("SCREEN", 16384), ("KBD", 24576),
                               ("SP", 0), ("LCL", 1), ("ARG", 2),
                               ("THIS", 3), ("THAT", 4)])

compMap :: Map String String
compMap = Map.fromList [("0", "101010"), ("1", "111111"), ("-1", "111010"),
                        ("D", "001100"), ("A", "110000"), ("M", "110000"),
                        ("!D", "001101"), ("!A", "110001"), ("!M", "110001"),
                        ("-D", "001111"), ("-A", "110011"), ("-M", "110011"),
                        ("D+1", "011111"), ("A+1", "110111"), ("M+1", "110111"),
                        ("D-1", "001110"), ("A-1", "110010"), ("M-1", "110010"),
                        ("D+A", "000010"), ("D+M", "000010"), ("D-A", "010011"),
                        ("D-M", "010011"), ("A-D", "000111"), ("M-D", "000111"),
                        ("D&A", "000000"), ("D&M", "000000"), ("D|A", "010101"),
                        ("D|M", "010101")]

destRegs :: [String]
destRegs = ["", "M", "D", "MD", "A", "AM", "AD", "AMD"]

jumpCmds :: [String]
jumpCmds = ["", "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"]

data Instruction = A Integer
                 | C (Maybe String) String (Maybe String)
                 deriving(Eq, Show)

parse :: [String] -> Map String Integer -> [Maybe Instruction]
parse x m = filter (Nothing /=) $ map (parseLine m) x

parseLine :: Map String Integer -> String -> Maybe Instruction
parseLine m x
    | "//" `isPrefixOf` x = Nothing
    | "@" `isPrefixOf` x = parseAInstruction m x
    | '=' `elem` x = parseAssignment x
    | ';' `elem` x = parseJump x
    | otherwise = Nothing

parseAInstruction :: Map String Integer -> String -> Maybe Instruction
parseAInstruction m ('@': symb) = Just $ A value where
    value = case Map.lookup symb m of
        Just addr -> addr
        Nothing -> case Map.lookup symb symbols of
            Just addr -> addr
            Nothing -> read symb

parseAssignment :: String -> Maybe Instruction
parseAssignment x = Just $ C (Just dest) comp Nothing where
    parts = splitOn "=" x
    dest = parts !! 0
    comp = parts !! 1

parseJump :: String -> Maybe Instruction
parseJump x = Just $ C Nothing comp (Just jump) where
    parts = splitOn ";" x
    comp = parts !! 0
    jump = parts !! 1

translate :: [Maybe Instruction] -> [String]
translate = map translateInstruction

translateInstruction :: Maybe Instruction -> String
translateInstruction inst =
    case inst of
        Nothing -> error "Cannot translate empty Instruction"
        Just (A val) -> "0" ++ padTo (instructionWidth - 1) (intToBin val)
        Just (C (Just dest) comp Nothing) -> "111" ++ aRegCheck comp ++ compToBin comp ++ padTo 3 (destToBin dest) ++ "000"
        Just (C Nothing comp (Just jmp)) -> "111" ++ aRegCheck comp ++ compToBin comp ++ "000" ++ padTo 3 (jumpCmdToBin jmp)

aRegCheck :: String -> String
aRegCheck str = if 'M' `elem` str then "1" else "0"

compToBin :: String -> String
compToBin comp =
    case Map.lookup comp compMap of
        Just bin -> bin

destToBin :: String -> String
destToBin x = case x `elemIndex` destRegs of
    Just idx -> intToBin (toInteger idx)

intToBin :: Integer -> String
intToBin 0 = "0"
intToBin x = go x [] where
    go 0 bin = bin
    go x bin = go (x `div` 2) (intToDigit (fromIntegral (x `mod` 2)) : bin)

jumpCmdToBin :: String -> String
jumpCmdToBin x = case x `elemIndex` jumpCmds of
    Just idx -> intToBin (toInteger idx)

padTo :: Int -> String -> String
padTo w x = go (w - length x) x where
    go 0 x = x
    go n x = go (n - 1) ('0' : x)

extractSymbols :: [String] -> [(String, Integer)]
extractSymbols (x:xs) = go x xs 0 where
    go _ [] i = []
    go x (x':xs) i = if "(" `isPrefixOf` x then (stripSymbol x, i) : go x' xs i else go x' xs (i+1)

stripSymbol :: String -> String
stripSymbol x = take (length x - 2) $ drop 1 x

defineSymbols :: [(String, Integer)] -> Map String Integer -> Map String Integer
defineSymbols xs m = foldr go m xs where
    go (key, val) m = Map.insert key val m

commentsWhitespace :: String -> Bool
commentsWhitespace x = (not (isPrefixOf "//" x) && (length x > 0))

stripTrailing :: String -> String
stripTrailing x = inst where
        noComments = (splitOn "//" x) !! 0
        inst = filter (' '/=) noComments

main :: IO ()
main = do
    args <- getArgs
    content <- readFile (args !! 0)
    let asm = map stripTrailing $ filter commentsWhitespace (splitOn "\r\n" content)
        symbolToInstNum = extractSymbols asm
        initialTable = Map.empty :: Map String Integer
        symbolTable = defineSymbols symbolToInstNum initialTable
        parsed = parse asm symbolTable
        binary = translate parsed
    hdl <- openFile (args !! 1) WriteMode
    mapM_ (hPutStrLn hdl) binary
    hClose hdl