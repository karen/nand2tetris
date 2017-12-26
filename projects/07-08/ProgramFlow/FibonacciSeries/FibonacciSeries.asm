// push ARG 1
@ARG
D=M
@1
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// pop POINTER 1
@SP
M=M-1
@SP
A=M
D=M
@THAT
M=D
// push CONSTANT 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop THAT 0
@SP
M=M-1
@THAT
D=M
@0
D=D+A
@R15
M=D
@SP
A=M
D=M
@R15
A=M
M=D
// push CONSTANT 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop THAT 1
@SP
M=M-1
@THAT
D=M
@1
D=D+A
@R15
M=D
@SP
A=M
D=M
@R15
A=M
M=D
// push ARG 0
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push CONSTANT 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=M-D
@SP
M=M+1
// pop ARG 0
@SP
M=M-1
@ARG
D=M
@0
D=D+A
@R15
M=D
@SP
A=M
D=M
@R15
A=M
M=D
// label MAIN_LOOP_START
(MAIN_LOOP_START)
// push ARG 0
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// if-goto COMPUTE_ELEMENT
@SP
M=M-1
@SP
A=M
D=M
@COMPUTE_ELEMENT
D;JNE
// goto END_PROGRAM
@END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(COMPUTE_ELEMENT)
// push THAT 0
@THAT
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push THAT 1
@THAT
D=M
@1
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=D+M
@SP
M=M+1
// pop THAT 2
@SP
M=M-1
@THAT
D=M
@2
D=D+A
@R15
M=D
@SP
A=M
D=M
@R15
A=M
M=D
// push POINTER 1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
// push CONSTANT 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=D+M
@SP
M=M+1
// pop POINTER 1
@SP
M=M-1
@SP
A=M
D=M
@THAT
M=D
// push ARG 0
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push CONSTANT 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=M-D
@SP
M=M+1
// pop ARG 0
@SP
M=M-1
@ARG
D=M
@0
D=D+A
@R15
M=D
@SP
A=M
D=M
@R15
A=M
M=D
// goto MAIN_LOOP_START
@MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(END_PROGRAM)
