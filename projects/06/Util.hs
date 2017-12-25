module Util where

import Data.List.Split(splitOn)
import Data.List(isPrefixOf)

commentsWhitespace :: String -> Bool
commentsWhitespace x = (not (isPrefixOf "//" x) && (length x > 0))

stripTrailing :: String -> String
stripTrailing x = inst where
        noComments = (splitOn "//" x) !! 0
        inst = filter (' '/=) noComments
