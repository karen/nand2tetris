// push CONSTANT 111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1
// push CONSTANT 333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1
// push CONSTANT 888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop STATIC 8
@SP
M=M-1
@SP
A=M
D=M
@StaticTest.8
M=D
// pop STATIC 3
@SP
M=M-1
@SP
A=M
D=M
@StaticTest.3
M=D
// pop STATIC 1
@SP
M=M-1
@SP
A=M
D=M
@StaticTest.1
M=D
// push STATIC 3
@StaticTest.3
D=M
@SP
A=M
M=D
@SP
M=M+1
// push STATIC 1
@StaticTest.1
D=M
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
// push STATIC 8
@StaticTest.8
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
