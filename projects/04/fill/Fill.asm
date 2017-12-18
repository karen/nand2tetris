// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
    
    @curr // prev, curr = 0, 0
    M=0
    @prev
    M=0

(LOOP)
    @KBD
    D=M
    @SETFILL
    D; JNE
    @SETCLEAR
    D; JEQ
(RETURN1)
    @SETSCREEN
    0; JMP

(SETCLEAR)
    @curr
    D=M
    @prev // prev = curr
    M=D
    @curr // curr = CLEAR (0)
    M=0
    @RETURN1
    0; JMP

(SETFILL)
    @curr
    D=M
    @prev
    M=D
    @curr
    M=-1
    @RETURN1
    0; JMP

(SETSCREEN)
    @curr
    D=M
    @prev
    D=D-M
    @LOOP
    D; JEQ // do not re-draw if they are the same

    @SCREEN
    D=A
    @i
    M=D

(ITER)
    @i
    D=M
    @KBD
    D=D-A
    @LOOP
    D; JGE // stop once we reach @KBD

    @curr
    D=M
    @i
    A=M
    M=D // draw

    @i
    M=M+1

    @ITER
    0; JMP
