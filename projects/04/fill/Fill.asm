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

// Put your code here.
@128
D=A
@enterkey
M=D
@SCREEN
D=A
@cur
M=D     // cur = @SCREEN(16384)
@idx
M=0     // idx = 0
(LOOP)
    @KBD
    D=M     // read a keyboard input
    @enterkey
    D=D-M
    @KEYDOWN
    D;JEQ   // if (key == "\n") then goto KEYDOWN, otherwise goto KEYUP
    @KEYUP
    0;JMP
(LOOP_END)
(KEYDOWN)
    @cur
    D=M
    @idx
    A=D+M
    M=-1
    @idx
    D=M
    @512
    D=D-A
    @LOOP
    D;JEQ
    @idx
    M=M+1
    @LOOP
    0;JMP
(KEYUP)
    @cur
    D=M
    @idx
    A=D+M
    M=0
    @idx
    D=M
    @0
    D=D-A
    @LOOP
    D;JEQ
    @idx
    M=M-1
    @LOOP
    0;JMP
