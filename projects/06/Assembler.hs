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

symbols :: Map String Int
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

data Instruction = A String
                 | C (Maybe String) String (Maybe String)
                 deriving(Eq, Show)

parse :: [String] -> [Maybe Instruction]
parse x = filter (Nothing /=) $ map parseLine x

parseLine :: String -> Maybe Instruction
parseLine x
    | "//" `isPrefixOf` x = Nothing
    | "@" `isPrefixOf` x = parseAInstruction x
    | '=' `elem` x = parseAssignment x
    | ';' `elem` x = parseJump x
    | otherwise = Nothing

parseAInstruction :: String -> Maybe Instruction
parseAInstruction ('@': symb) = Just $ A symb

parseAssignment :: String -> Maybe Instruction
parseAssignment x = Just $ C (Just dest) comp Nothing where
    parts = splitOn "=" x
    dest = parts !! 0
    comp = parts !! 1

parseJump :: String -> Maybe Instruction
parseJump x = Just $ C Nothing symb (Just jmp) where
    parts = splitOn ";" x
    symb = parts !! 0
    jmp = parts !! 1

translate :: [Maybe Instruction] -> [String]
translate = map translateInstruction

translateInstruction :: Maybe Instruction -> String
translateInstruction inst =
    case inst of
        Nothing -> error "Cannot translate empty Instruction"
        Just (A val) -> "0" ++ padTo (instructionWidth - 1) (symbolToBinary val)
        Just (C (Just dest) comp Nothing) -> "111" ++ aRegCheck comp ++ compToBin comp ++ padTo 3 (destToBin dest) ++ "000"
        Just (C Nothing comp (Just jmp)) -> "111" ++ aRegCheck comp ++ compToBin comp ++ "000" ++ padTo 3 (jumpCmdToBin jmp)

aRegCheck :: String -> String
aRegCheck str = if 'M' `elem` str then "0" else "1"

compToBin :: String -> String
compToBin comp =
    case Map.lookup comp compMap of
        Just bin -> bin

destToBin :: String -> String
destToBin x = case x `elemIndex` destRegs of
    Just idx -> intToBin idx

intToBin :: Int -> String
intToBin 0 = "0"
intToBin x = go x [] where
    go 0 bin = bin
    go x bin = go (x `div` 2) (intToDigit (x `mod` 2) : bin)

jumpCmdToBin :: String -> String
jumpCmdToBin x = case x `elemIndex` jumpCmds of
    Just idx -> intToBin idx

symbolToBinary :: String -> String
symbolToBinary = intToBin . symbolToValue

symbolToValue :: String -> Int
symbolToValue sym = case Map.lookup sym symbols of
    Just val -> val
    Nothing -> read sym

padTo :: Int -> String -> String
padTo w x = go (w - length x) x where
    go 0 x = x
    go n x = go (n - 1) ('0' : x)

main :: IO ()
main = do
    args <- getArgs
    content <- readFile (args !! 0)
    let asm = splitOn "\r\n" content
        parsed = parse asm
        binary = translate parsed
    hdl <- openFile (args !! 1) WriteMode
    mapM_ (hPutStrLn hdl) binary
    hClose hdl