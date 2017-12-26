// push CONSTANT 3030
@3030
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop POINTER 0
@SP
M=M-1
@SP
A=M
D=M
@THIS
M=D
// push CONSTANT 3040
@3040
D=A
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
// push CONSTANT 32
@32
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop THIS 2
@SP
M=M-1
@THIS
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
// push CONSTANT 46
@46
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop THAT 6
@SP
M=M-1
@THAT
D=M
@6
D=D+A
@R15
M=D
@SP
A=M
D=M
@R15
A=M
M=D
// push POINTER 0
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
// push POINTER 1
@THAT
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
// push THIS 2
@THIS
D=M
@2
D=D+A
A=D
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
// push THAT 6
@THAT
D=M
@6
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
