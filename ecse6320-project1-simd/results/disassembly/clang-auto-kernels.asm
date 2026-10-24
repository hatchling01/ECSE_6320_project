; Targeted disassembly: clang-auto
; Object file: 
C:\Users\CHOUDN3\Downloads\EcSE_4320\ecse6320-project1-simd\build-clang-auto\CMakeFiles\project_kernels.dir\src\kernels.cpp.obj
; GNU objdump -d -C -Mintel; project_kernels symbols only.

0000000000000000 <void project::axpy<float>(float, float const*, float*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 e4 00 00 00    	je     ed <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xed>
   9:	49 83 f9 08          	cmp    r9,0x8
   d:	72 18                	jb     27 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x27>
   f:	4b 8d 04 88          	lea    rax,[r8+r9*4]
  13:	4a 8d 0c 8a          	lea    rcx,[rdx+r9*4]
  17:	49 39 c8             	cmp    r8,rcx
  1a:	0f 92 c1             	setb   cl
  1d:	48 39 c2             	cmp    rdx,rax
  20:	0f 92 c0             	setb   al
  23:	84 c1                	test   cl,al
  25:	74 71                	je     98 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x98>
  27:	31 c0                	xor    eax,eax
  29:	48 8d 48 01          	lea    rcx,[rax+0x1]
  2d:	41 f6 c1 01          	test   r9b,0x1
  31:	74 18                	je     4b <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x4b>
  33:	f3 0f 10 0c 82       	movss  xmm1,DWORD PTR [rdx+rax*4]
  38:	f3 0f 59 c8          	mulss  xmm1,xmm0
  3c:	f3 41 0f 58 0c 80    	addss  xmm1,DWORD PTR [r8+rax*4]
  42:	f3 41 0f 11 0c 80    	movss  DWORD PTR [r8+rax*4],xmm1
  48:	48 89 c8             	mov    rax,rcx
  4b:	49 39 c9             	cmp    r9,rcx
  4e:	0f 84 99 00 00 00    	je     ed <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xed>
  54:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
  5b:	00 00 00 00 00 
  60:	f3 0f 10 0c 82       	movss  xmm1,DWORD PTR [rdx+rax*4]
  65:	f3 0f 59 c8          	mulss  xmm1,xmm0
  69:	f3 41 0f 58 0c 80    	addss  xmm1,DWORD PTR [r8+rax*4]
  6f:	f3 41 0f 11 0c 80    	movss  DWORD PTR [r8+rax*4],xmm1
  75:	f3 0f 10 4c 82 04    	movss  xmm1,DWORD PTR [rdx+rax*4+0x4]
  7b:	f3 0f 59 c8          	mulss  xmm1,xmm0
  7f:	f3 41 0f 58 4c 80 04 	addss  xmm1,DWORD PTR [r8+rax*4+0x4]
  86:	f3 41 0f 11 4c 80 04 	movss  DWORD PTR [r8+rax*4+0x4],xmm1
  8d:	48 83 c0 02          	add    rax,0x2
  91:	49 39 c1             	cmp    r9,rax
  94:	75 ca                	jne    60 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x60>
  96:	eb 55                	jmp    ed <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xed>
  98:	4c 89 c8             	mov    rax,r9
  9b:	48 83 e0 f8          	and    rax,0xfffffffffffffff8
  9f:	0f 28 c8             	movaps xmm1,xmm0
  a2:	0f c6 c8 00          	shufps xmm1,xmm0,0x0
  a6:	31 c9                	xor    ecx,ecx
  a8:	0f 1f 84 00 00 00 00 	nop    DWORD PTR [rax+rax*1+0x0]
  af:	00 
  b0:	0f 10 14 8a          	movups xmm2,XMMWORD PTR [rdx+rcx*4]
  b4:	0f 10 5c 8a 10       	movups xmm3,XMMWORD PTR [rdx+rcx*4+0x10]
  b9:	41 0f 10 24 88       	movups xmm4,XMMWORD PTR [r8+rcx*4]
  be:	41 0f 10 6c 88 10    	movups xmm5,XMMWORD PTR [r8+rcx*4+0x10]
  c4:	0f 59 d1             	mulps  xmm2,xmm1
  c7:	0f 58 d4             	addps  xmm2,xmm4
  ca:	0f 59 d9             	mulps  xmm3,xmm1
  cd:	0f 58 dd             	addps  xmm3,xmm5
  d0:	41 0f 11 14 88       	movups XMMWORD PTR [r8+rcx*4],xmm2
  d5:	41 0f 11 5c 88 10    	movups XMMWORD PTR [r8+rcx*4+0x10],xmm3
  db:	48 83 c1 08          	add    rcx,0x8
  df:	48 39 c8             	cmp    rax,rcx
  e2:	75 cc                	jne    b0 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xb0>
  e4:	49 39 c1             	cmp    r9,rax
  e7:	0f 85 3c ff ff ff    	jne    29 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x29>
  ed:	c3                   	ret

Disassembly of section .text$_ZN7project4axpyIdEEvT_PKS1_PS1_y:


0000000000000000 <void project::axpy<double>(double, double const*, double*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 ee 00 00 00    	je     f7 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xf7>
   9:	49 83 f9 06          	cmp    r9,0x6
   d:	72 18                	jb     27 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x27>
   f:	4b 8d 04 c8          	lea    rax,[r8+r9*8]
  13:	4a 8d 0c ca          	lea    rcx,[rdx+r9*8]
  17:	49 39 c8             	cmp    r8,rcx
  1a:	0f 92 c1             	setb   cl
  1d:	48 39 c2             	cmp    rdx,rax
  20:	0f 92 c0             	setb   al
  23:	84 c1                	test   cl,al
  25:	74 71                	je     98 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x98>
  27:	31 c0                	xor    eax,eax
  29:	48 8d 48 01          	lea    rcx,[rax+0x1]
  2d:	41 f6 c1 01          	test   r9b,0x1
  31:	74 18                	je     4b <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x4b>
  33:	f2 0f 10 0c c2       	movsd  xmm1,QWORD PTR [rdx+rax*8]
  38:	f2 0f 59 c8          	mulsd  xmm1,xmm0
  3c:	f2 41 0f 58 0c c0    	addsd  xmm1,QWORD PTR [r8+rax*8]
  42:	f2 41 0f 11 0c c0    	movsd  QWORD PTR [r8+rax*8],xmm1
  48:	48 89 c8             	mov    rax,rcx
  4b:	49 39 c9             	cmp    r9,rcx
  4e:	0f 84 a3 00 00 00    	je     f7 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xf7>
  54:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
  5b:	00 00 00 00 00 
  60:	f2 0f 10 0c c2       	movsd  xmm1,QWORD PTR [rdx+rax*8]
  65:	f2 0f 59 c8          	mulsd  xmm1,xmm0
  69:	f2 41 0f 58 0c c0    	addsd  xmm1,QWORD PTR [r8+rax*8]
  6f:	f2 41 0f 11 0c c0    	movsd  QWORD PTR [r8+rax*8],xmm1
  75:	f2 0f 10 4c c2 08    	movsd  xmm1,QWORD PTR [rdx+rax*8+0x8]
  7b:	f2 0f 59 c8          	mulsd  xmm1,xmm0
  7f:	f2 41 0f 58 4c c0 08 	addsd  xmm1,QWORD PTR [r8+rax*8+0x8]
  86:	f2 41 0f 11 4c c0 08 	movsd  QWORD PTR [r8+rax*8+0x8],xmm1
  8d:	48 83 c0 02          	add    rax,0x2
  91:	49 39 c1             	cmp    r9,rax
  94:	75 ca                	jne    60 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x60>
  96:	eb 5f                	jmp    f7 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xf7>
  98:	4c 89 c8             	mov    rax,r9
  9b:	48 83 e0 fc          	and    rax,0xfffffffffffffffc
  9f:	66 0f 28 c8          	movapd xmm1,xmm0
  a3:	66 0f 14 c8          	unpcklpd xmm1,xmm0
  a7:	31 c9                	xor    ecx,ecx
  a9:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
  b0:	66 0f 10 14 ca       	movupd xmm2,XMMWORD PTR [rdx+rcx*8]
  b5:	66 0f 10 5c ca 10    	movupd xmm3,XMMWORD PTR [rdx+rcx*8+0x10]
  bb:	66 41 0f 10 24 c8    	movupd xmm4,XMMWORD PTR [r8+rcx*8]
  c1:	66 41 0f 10 6c c8 10 	movupd xmm5,XMMWORD PTR [r8+rcx*8+0x10]
  c8:	66 0f 59 d1          	mulpd  xmm2,xmm1
  cc:	66 0f 58 d4          	addpd  xmm2,xmm4
  d0:	66 0f 59 d9          	mulpd  xmm3,xmm1
  d4:	66 0f 58 dd          	addpd  xmm3,xmm5
  d8:	66 41 0f 11 14 c8    	movupd XMMWORD PTR [r8+rcx*8],xmm2
  de:	66 41 0f 11 5c c8 10 	movupd XMMWORD PTR [r8+rcx*8+0x10],xmm3
  e5:	48 83 c1 04          	add    rcx,0x4
  e9:	48 39 c8             	cmp    rax,rcx
  ec:	75 c2                	jne    b0 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xb0>
  ee:	49 39 c1             	cmp    r9,rax
  f1:	0f 85 32 ff ff ff    	jne    29 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x29>
  f7:	c3                   	ret

Disassembly of section .text$_ZN7project11dot_productIfEET_PKS1_S3_y:


0000000000000000 <float project::dot_product<float>(float const*, float const*, unsigned long long)>:
   0:	4d 85 c0             	test   r8,r8
   3:	74 14                	je     19 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x19>
   5:	44 89 c0             	mov    eax,r8d
   8:	83 e0 03             	and    eax,0x3
   b:	49 83 f8 04          	cmp    r8,0x4
   f:	73 0c                	jae    1d <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x1d>
  11:	0f 57 c0             	xorps  xmm0,xmm0
  14:	45 31 c9             	xor    r9d,r9d
  17:	eb 6b                	jmp    84 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x84>
  19:	0f 57 c0             	xorps  xmm0,xmm0
  1c:	c3                   	ret
  1d:	49 83 e0 fc          	and    r8,0xfffffffffffffffc
  21:	0f 57 c0             	xorps  xmm0,xmm0
  24:	45 31 c9             	xor    r9d,r9d
  27:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  2e:	00 00 
  30:	f3 42 0f 10 0c 89    	movss  xmm1,DWORD PTR [rcx+r9*4]
  36:	f3 42 0f 10 54 89 04 	movss  xmm2,DWORD PTR [rcx+r9*4+0x4]
  3d:	f3 42 0f 59 0c 8a    	mulss  xmm1,DWORD PTR [rdx+r9*4]
  43:	f3 42 0f 59 54 8a 04 	mulss  xmm2,DWORD PTR [rdx+r9*4+0x4]
  4a:	f3 0f 58 c8          	addss  xmm1,xmm0
  4e:	f3 42 0f 10 5c 89 08 	movss  xmm3,DWORD PTR [rcx+r9*4+0x8]
  55:	f3 42 0f 59 5c 8a 08 	mulss  xmm3,DWORD PTR [rdx+r9*4+0x8]
  5c:	f3 0f 58 d1          	addss  xmm2,xmm1
  60:	f3 42 0f 10 44 89 0c 	movss  xmm0,DWORD PTR [rcx+r9*4+0xc]
  67:	f3 42 0f 59 44 8a 0c 	mulss  xmm0,DWORD PTR [rdx+r9*4+0xc]
  6e:	f3 0f 58 da          	addss  xmm3,xmm2
  72:	f3 0f 58 c3          	addss  xmm0,xmm3
  76:	49 83 c1 04          	add    r9,0x4
  7a:	4d 39 c8             	cmp    r8,r9
  7d:	75 b1                	jne    30 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x30>
  7f:	48 85 c0             	test   rax,rax
  82:	74 24                	je     a8 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xa8>
  84:	4a 8d 14 8a          	lea    rdx,[rdx+r9*4]
  88:	4a 8d 0c 89          	lea    rcx,[rcx+r9*4]
  8c:	45 31 c0             	xor    r8d,r8d
  8f:	90                   	nop
  90:	f3 42 0f 10 0c 81    	movss  xmm1,DWORD PTR [rcx+r8*4]
  96:	f3 42 0f 59 0c 82    	mulss  xmm1,DWORD PTR [rdx+r8*4]
  9c:	f3 0f 58 c1          	addss  xmm0,xmm1
  a0:	49 ff c0             	inc    r8
  a3:	4c 39 c0             	cmp    rax,r8
  a6:	75 e8                	jne    90 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x90>
  a8:	c3                   	ret

Disassembly of section .text$_ZN7project11dot_productIdEET_PKS1_S3_y:


0000000000000000 <double project::dot_product<double>(double const*, double const*, unsigned long long)>:
   0:	4d 85 c0             	test   r8,r8
   3:	74 15                	je     1a <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x1a>
   5:	44 89 c0             	mov    eax,r8d
   8:	83 e0 03             	and    eax,0x3
   b:	49 83 f8 04          	cmp    r8,0x4
   f:	73 0d                	jae    1e <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x1e>
  11:	66 0f 57 c0          	xorpd  xmm0,xmm0
  15:	45 31 c9             	xor    r9d,r9d
  18:	eb 6a                	jmp    84 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x84>
  1a:	0f 57 c0             	xorps  xmm0,xmm0
  1d:	c3                   	ret
  1e:	49 83 e0 fc          	and    r8,0xfffffffffffffffc
  22:	66 0f 57 c0          	xorpd  xmm0,xmm0
  26:	45 31 c9             	xor    r9d,r9d
  29:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
  30:	f2 42 0f 10 0c c9    	movsd  xmm1,QWORD PTR [rcx+r9*8]
  36:	f2 42 0f 10 54 c9 08 	movsd  xmm2,QWORD PTR [rcx+r9*8+0x8]
  3d:	f2 42 0f 59 0c ca    	mulsd  xmm1,QWORD PTR [rdx+r9*8]
  43:	f2 42 0f 59 54 ca 08 	mulsd  xmm2,QWORD PTR [rdx+r9*8+0x8]
  4a:	f2 0f 58 c8          	addsd  xmm1,xmm0
  4e:	f2 42 0f 10 5c c9 10 	movsd  xmm3,QWORD PTR [rcx+r9*8+0x10]
  55:	f2 42 0f 59 5c ca 10 	mulsd  xmm3,QWORD PTR [rdx+r9*8+0x10]
  5c:	f2 0f 58 d1          	addsd  xmm2,xmm1
  60:	f2 42 0f 10 44 c9 18 	movsd  xmm0,QWORD PTR [rcx+r9*8+0x18]
  67:	f2 42 0f 59 44 ca 18 	mulsd  xmm0,QWORD PTR [rdx+r9*8+0x18]
  6e:	f2 0f 58 da          	addsd  xmm3,xmm2
  72:	f2 0f 58 c3          	addsd  xmm0,xmm3
  76:	49 83 c1 04          	add    r9,0x4
  7a:	4d 39 c8             	cmp    r8,r9
  7d:	75 b1                	jne    30 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x30>
  7f:	48 85 c0             	test   rax,rax
  82:	74 24                	je     a8 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0xa8>
  84:	4a 8d 14 ca          	lea    rdx,[rdx+r9*8]
  88:	4a 8d 0c c9          	lea    rcx,[rcx+r9*8]
  8c:	45 31 c0             	xor    r8d,r8d
  8f:	90                   	nop
  90:	f2 42 0f 10 0c c1    	movsd  xmm1,QWORD PTR [rcx+r8*8]
  96:	f2 42 0f 59 0c c2    	mulsd  xmm1,QWORD PTR [rdx+r8*8]
  9c:	f2 0f 58 c1          	addsd  xmm0,xmm1
  a0:	49 ff c0             	inc    r8
  a3:	4c 39 c0             	cmp    rax,r8
  a6:	75 e8                	jne    90 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x90>
  a8:	c3                   	ret

Disassembly of section .text$_ZN7project20elementwise_multiplyIfEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 20 01 00 00    	je     129 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x129>
   9:	49 83 f9 0c          	cmp    r9,0xc
   d:	72 24                	jb     33 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x33>
   f:	48 89 c8             	mov    rax,rcx
  12:	4c 29 c0             	sub    rax,r8
  15:	48 83 f8 e1          	cmp    rax,0xffffffffffffffe1
  19:	0f 93 c0             	setae  al
  1c:	49 89 d2             	mov    r10,rdx
  1f:	4d 29 c2             	sub    r10,r8
  22:	49 83 fa e1          	cmp    r10,0xffffffffffffffe1
  26:	41 0f 93 c2          	setae  r10b
  2a:	41 08 c2             	or     r10b,al
  2d:	0f 84 a9 00 00 00    	je     dc <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xdc>
  33:	31 c0                	xor    eax,eax
  35:	4d 89 cb             	mov    r11,r9
  38:	49 89 c2             	mov    r10,rax
  3b:	49 83 e3 03          	and    r11,0x3
  3f:	74 29                	je     6a <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x6a>
  41:	49 89 c2             	mov    r10,rax
  44:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
  4b:	00 00 00 00 00 
  50:	f3 42 0f 10 04 91    	movss  xmm0,DWORD PTR [rcx+r10*4]
  56:	f3 42 0f 59 04 92    	mulss  xmm0,DWORD PTR [rdx+r10*4]
  5c:	f3 43 0f 11 04 90    	movss  DWORD PTR [r8+r10*4],xmm0
  62:	49 ff c2             	inc    r10
  65:	49 ff cb             	dec    r11
  68:	75 e6                	jne    50 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x50>
  6a:	4c 29 c8             	sub    rax,r9
  6d:	48 83 f8 fc          	cmp    rax,0xfffffffffffffffc
  71:	0f 87 b2 00 00 00    	ja     129 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x129>
  77:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  7e:	00 00 
  80:	f3 42 0f 10 04 91    	movss  xmm0,DWORD PTR [rcx+r10*4]
  86:	f3 42 0f 59 04 92    	mulss  xmm0,DWORD PTR [rdx+r10*4]
  8c:	f3 43 0f 11 04 90    	movss  DWORD PTR [r8+r10*4],xmm0
  92:	f3 42 0f 10 44 91 04 	movss  xmm0,DWORD PTR [rcx+r10*4+0x4]
  99:	f3 42 0f 59 44 92 04 	mulss  xmm0,DWORD PTR [rdx+r10*4+0x4]
  a0:	f3 43 0f 11 44 90 04 	movss  DWORD PTR [r8+r10*4+0x4],xmm0
  a7:	f3 42 0f 10 44 91 08 	movss  xmm0,DWORD PTR [rcx+r10*4+0x8]
  ae:	f3 42 0f 59 44 92 08 	mulss  xmm0,DWORD PTR [rdx+r10*4+0x8]
  b5:	f3 43 0f 11 44 90 08 	movss  DWORD PTR [r8+r10*4+0x8],xmm0
  bc:	f3 42 0f 10 44 91 0c 	movss  xmm0,DWORD PTR [rcx+r10*4+0xc]
  c3:	f3 42 0f 59 44 92 0c 	mulss  xmm0,DWORD PTR [rdx+r10*4+0xc]
  ca:	f3 43 0f 11 44 90 0c 	movss  DWORD PTR [r8+r10*4+0xc],xmm0
  d1:	49 83 c2 04          	add    r10,0x4
  d5:	4d 39 d1             	cmp    r9,r10
  d8:	75 a6                	jne    80 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x80>
  da:	eb 4d                	jmp    129 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x129>
  dc:	4c 89 c8             	mov    rax,r9
  df:	48 83 e0 f8          	and    rax,0xfffffffffffffff8
  e3:	45 31 d2             	xor    r10d,r10d
  e6:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  ed:	00 00 00 
  f0:	42 0f 10 04 91       	movups xmm0,XMMWORD PTR [rcx+r10*4]
  f5:	42 0f 10 4c 91 10    	movups xmm1,XMMWORD PTR [rcx+r10*4+0x10]
  fb:	42 0f 10 14 92       	movups xmm2,XMMWORD PTR [rdx+r10*4]
 100:	0f 59 d0             	mulps  xmm2,xmm0
 103:	42 0f 10 44 92 10    	movups xmm0,XMMWORD PTR [rdx+r10*4+0x10]
 109:	0f 59 c1             	mulps  xmm0,xmm1
 10c:	43 0f 11 14 90       	movups XMMWORD PTR [r8+r10*4],xmm2
 111:	43 0f 11 44 90 10    	movups XMMWORD PTR [r8+r10*4+0x10],xmm0
 117:	49 83 c2 08          	add    r10,0x8
 11b:	4c 39 d0             	cmp    rax,r10
 11e:	75 d0                	jne    f0 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xf0>
 120:	49 39 c1             	cmp    r9,rax
 123:	0f 85 0c ff ff ff    	jne    35 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x35>
 129:	c3                   	ret

Disassembly of section .text$_ZN7project20elementwise_multiplyIdEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 28 01 00 00    	je     131 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x131>
   9:	49 83 f9 0a          	cmp    r9,0xa
   d:	72 24                	jb     33 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x33>
   f:	48 89 c8             	mov    rax,rcx
  12:	4c 29 c0             	sub    rax,r8
  15:	48 83 f8 e1          	cmp    rax,0xffffffffffffffe1
  19:	0f 93 c0             	setae  al
  1c:	49 89 d2             	mov    r10,rdx
  1f:	4d 29 c2             	sub    r10,r8
  22:	49 83 fa e1          	cmp    r10,0xffffffffffffffe1
  26:	41 0f 93 c2          	setae  r10b
  2a:	41 08 c2             	or     r10b,al
  2d:	0f 84 a9 00 00 00    	je     dc <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xdc>
  33:	31 c0                	xor    eax,eax
  35:	4d 89 cb             	mov    r11,r9
  38:	49 89 c2             	mov    r10,rax
  3b:	49 83 e3 03          	and    r11,0x3
  3f:	74 29                	je     6a <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x6a>
  41:	49 89 c2             	mov    r10,rax
  44:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
  4b:	00 00 00 00 00 
  50:	f2 42 0f 10 04 d1    	movsd  xmm0,QWORD PTR [rcx+r10*8]
  56:	f2 42 0f 59 04 d2    	mulsd  xmm0,QWORD PTR [rdx+r10*8]
  5c:	f2 43 0f 11 04 d0    	movsd  QWORD PTR [r8+r10*8],xmm0
  62:	49 ff c2             	inc    r10
  65:	49 ff cb             	dec    r11
  68:	75 e6                	jne    50 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x50>
  6a:	4c 29 c8             	sub    rax,r9
  6d:	48 83 f8 fc          	cmp    rax,0xfffffffffffffffc
  71:	0f 87 ba 00 00 00    	ja     131 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x131>
  77:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  7e:	00 00 
  80:	f2 42 0f 10 04 d1    	movsd  xmm0,QWORD PTR [rcx+r10*8]
  86:	f2 42 0f 59 04 d2    	mulsd  xmm0,QWORD PTR [rdx+r10*8]
  8c:	f2 43 0f 11 04 d0    	movsd  QWORD PTR [r8+r10*8],xmm0
  92:	f2 42 0f 10 44 d1 08 	movsd  xmm0,QWORD PTR [rcx+r10*8+0x8]
  99:	f2 42 0f 59 44 d2 08 	mulsd  xmm0,QWORD PTR [rdx+r10*8+0x8]
  a0:	f2 43 0f 11 44 d0 08 	movsd  QWORD PTR [r8+r10*8+0x8],xmm0
  a7:	f2 42 0f 10 44 d1 10 	movsd  xmm0,QWORD PTR [rcx+r10*8+0x10]
  ae:	f2 42 0f 59 44 d2 10 	mulsd  xmm0,QWORD PTR [rdx+r10*8+0x10]
  b5:	f2 43 0f 11 44 d0 10 	movsd  QWORD PTR [r8+r10*8+0x10],xmm0
  bc:	f2 42 0f 10 44 d1 18 	movsd  xmm0,QWORD PTR [rcx+r10*8+0x18]
  c3:	f2 42 0f 59 44 d2 18 	mulsd  xmm0,QWORD PTR [rdx+r10*8+0x18]
  ca:	f2 43 0f 11 44 d0 18 	movsd  QWORD PTR [r8+r10*8+0x18],xmm0
  d1:	49 83 c2 04          	add    r10,0x4
  d5:	4d 39 d1             	cmp    r9,r10
  d8:	75 a6                	jne    80 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x80>
  da:	eb 55                	jmp    131 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x131>
  dc:	4c 89 c8             	mov    rax,r9
  df:	48 83 e0 fc          	and    rax,0xfffffffffffffffc
  e3:	45 31 d2             	xor    r10d,r10d
  e6:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  ed:	00 00 00 
  f0:	66 42 0f 10 04 d1    	movupd xmm0,XMMWORD PTR [rcx+r10*8]
  f6:	66 42 0f 10 4c d1 10 	movupd xmm1,XMMWORD PTR [rcx+r10*8+0x10]
  fd:	66 42 0f 10 14 d2    	movupd xmm2,XMMWORD PTR [rdx+r10*8]
 103:	66 0f 59 d0          	mulpd  xmm2,xmm0
 107:	66 42 0f 10 44 d2 10 	movupd xmm0,XMMWORD PTR [rdx+r10*8+0x10]
 10e:	66 0f 59 c1          	mulpd  xmm0,xmm1
 112:	66 43 0f 11 14 d0    	movupd XMMWORD PTR [r8+r10*8],xmm2
 118:	66 43 0f 11 44 d0 10 	movupd XMMWORD PTR [r8+r10*8+0x10],xmm0
 11f:	49 83 c2 04          	add    r10,0x4
 123:	4c 39 d0             	cmp    rax,r10
 126:	75 c8                	jne    f0 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xf0>
 128:	49 39 c1             	cmp    r9,rax
 12b:	0f 85 04 ff ff ff    	jne    35 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x35>
 131:	c3                   	ret

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIfEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)>:
   0:	41 57                	push   r15
   2:	41 56                	push   r14
   4:	41 54                	push   r12
   6:	56                   	push   rsi
   7:	57                   	push   rdi
   8:	53                   	push   rbx
   9:	48 8b 44 24 68       	mov    rax,QWORD PTR [rsp+0x68]
   e:	48 85 c0             	test   rax,rax
  11:	0f 84 fa 00 00 00    	je     111 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x111>
  17:	4c 8b 54 24 60       	mov    r10,QWORD PTR [rsp+0x60]
  1c:	4c 8b 5c 24 58       	mov    r11,QWORD PTR [rsp+0x58]
  21:	48 83 f8 14          	cmp    rax,0x14
  25:	72 41                	jb     68 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x68>
  27:	4c 89 d6             	mov    rsi,r10
  2a:	48 83 f6 01          	xor    rsi,0x1
  2e:	48 89 d7             	mov    rdi,rdx
  31:	48 83 f7 01          	xor    rdi,0x1
  35:	48 09 f7             	or     rdi,rsi
  38:	4c 89 ce             	mov    rsi,r9
  3b:	48 83 f6 01          	xor    rsi,0x1
  3f:	48 09 fe             	or     rsi,rdi
  42:	75 24                	jne    68 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x68>
  44:	48 89 ce             	mov    rsi,rcx
  47:	4c 29 de             	sub    rsi,r11
  4a:	48 83 fe e1          	cmp    rsi,0xffffffffffffffe1
  4e:	0f 93 c3             	setae  bl
  51:	4c 89 c6             	mov    rsi,r8
  54:	4c 29 de             	sub    rsi,r11
  57:	48 83 fe e1          	cmp    rsi,0xffffffffffffffe1
  5b:	40 0f 93 c6          	setae  sil
  5f:	40 08 de             	or     sil,bl
  62:	0f 84 b3 00 00 00    	je     11b <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x11b>
  68:	31 f6                	xor    esi,esi
  6a:	48 8d 7e 01          	lea    rdi,[rsi+0x1]
  6e:	a8 01                	test   al,0x1
  70:	74 26                	je     98 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x98>
  72:	48 89 f3             	mov    rbx,rsi
  75:	48 0f af da          	imul   rbx,rdx
  79:	f3 0f 10 04 99       	movss  xmm0,DWORD PTR [rcx+rbx*4]
  7e:	48 89 f3             	mov    rbx,rsi
  81:	49 0f af d9          	imul   rbx,r9
  85:	f3 41 0f 59 04 98    	mulss  xmm0,DWORD PTR [r8+rbx*4]
  8b:	49 0f af f2          	imul   rsi,r10
  8f:	f3 41 0f 11 04 b3    	movss  DWORD PTR [r11+rsi*4],xmm0
  95:	48 89 fe             	mov    rsi,rdi
  98:	48 39 f8             	cmp    rax,rdi
  9b:	74 74                	je     111 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x111>
  9d:	48 29 f0             	sub    rax,rsi
  a0:	48 8d 7e 01          	lea    rdi,[rsi+0x1]
  a4:	4c 89 d3             	mov    rbx,r10
  a7:	48 0f af df          	imul   rbx,rdi
  ab:	4d 89 ce             	mov    r14,r9
  ae:	4c 0f af f7          	imul   r14,rdi
  b2:	48 0f af fa          	imul   rdi,rdx
  b6:	49 89 f7             	mov    r15,rsi
  b9:	4d 0f af fa          	imul   r15,r10
  bd:	49 c1 e2 03          	shl    r10,0x3
  c1:	49 89 f4             	mov    r12,rsi
  c4:	4d 0f af e1          	imul   r12,r9
  c8:	49 c1 e1 03          	shl    r9,0x3
  cc:	48 0f af f2          	imul   rsi,rdx
  d0:	48 c1 e2 03          	shl    rdx,0x3
  d4:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
  db:	00 00 00 00 00 
  e0:	f3 0f 10 04 b1       	movss  xmm0,DWORD PTR [rcx+rsi*4]
  e5:	f3 43 0f 59 04 a0    	mulss  xmm0,DWORD PTR [r8+r12*4]
  eb:	f3 43 0f 11 04 bb    	movss  DWORD PTR [r11+r15*4],xmm0
  f1:	f3 0f 10 04 b9       	movss  xmm0,DWORD PTR [rcx+rdi*4]
  f6:	f3 43 0f 59 04 b0    	mulss  xmm0,DWORD PTR [r8+r14*4]
  fc:	f3 41 0f 11 04 9b    	movss  DWORD PTR [r11+rbx*4],xmm0
 102:	4d 01 d3             	add    r11,r10
 105:	4d 01 c8             	add    r8,r9
 108:	48 01 d1             	add    rcx,rdx
 10b:	48 83 c0 fe          	add    rax,0xfffffffffffffffe
 10f:	75 cf                	jne    e0 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xe0>
 111:	5b                   	pop    rbx
 112:	5f                   	pop    rdi
 113:	5e                   	pop    rsi
 114:	41 5c                	pop    r12
 116:	41 5e                	pop    r14
 118:	41 5f                	pop    r15
 11a:	c3                   	ret
 11b:	48 89 c6             	mov    rsi,rax
 11e:	48 83 e6 f8          	and    rsi,0xfffffffffffffff8
 122:	31 ff                	xor    edi,edi
 124:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
 12b:	00 00 00 00 00 
 130:	0f 10 04 b9          	movups xmm0,XMMWORD PTR [rcx+rdi*4]
 134:	0f 10 4c b9 10       	movups xmm1,XMMWORD PTR [rcx+rdi*4+0x10]
 139:	41 0f 10 14 b8       	movups xmm2,XMMWORD PTR [r8+rdi*4]
 13e:	0f 59 d0             	mulps  xmm2,xmm0
 141:	41 0f 10 44 b8 10    	movups xmm0,XMMWORD PTR [r8+rdi*4+0x10]
 147:	0f 59 c1             	mulps  xmm0,xmm1
 14a:	41 0f 11 14 bb       	movups XMMWORD PTR [r11+rdi*4],xmm2
 14f:	41 0f 11 44 bb 10    	movups XMMWORD PTR [r11+rdi*4+0x10],xmm0
 155:	48 83 c7 08          	add    rdi,0x8
 159:	48 39 fe             	cmp    rsi,rdi
 15c:	75 d2                	jne    130 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x130>
 15e:	48 39 f0             	cmp    rax,rsi
 161:	74 ae                	je     111 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x111>
 163:	e9 02 ff ff ff       	jmp    6a <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x6a>

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIdEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)>:
   0:	41 57                	push   r15
   2:	41 56                	push   r14
   4:	41 54                	push   r12
   6:	56                   	push   rsi
   7:	57                   	push   rdi
   8:	53                   	push   rbx
   9:	48 8b 44 24 68       	mov    rax,QWORD PTR [rsp+0x68]
   e:	48 85 c0             	test   rax,rax
  11:	0f 84 fa 00 00 00    	je     111 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x111>
  17:	4c 8b 54 24 60       	mov    r10,QWORD PTR [rsp+0x60]
  1c:	4c 8b 5c 24 58       	mov    r11,QWORD PTR [rsp+0x58]
  21:	48 83 f8 12          	cmp    rax,0x12
  25:	72 41                	jb     68 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x68>
  27:	4c 89 d6             	mov    rsi,r10
  2a:	48 83 f6 01          	xor    rsi,0x1
  2e:	48 89 d7             	mov    rdi,rdx
  31:	48 83 f7 01          	xor    rdi,0x1
  35:	48 09 f7             	or     rdi,rsi
  38:	4c 89 ce             	mov    rsi,r9
  3b:	48 83 f6 01          	xor    rsi,0x1
  3f:	48 09 fe             	or     rsi,rdi
  42:	75 24                	jne    68 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x68>
  44:	48 89 ce             	mov    rsi,rcx
  47:	4c 29 de             	sub    rsi,r11
  4a:	48 83 fe e1          	cmp    rsi,0xffffffffffffffe1
  4e:	0f 93 c3             	setae  bl
  51:	4c 89 c6             	mov    rsi,r8
  54:	4c 29 de             	sub    rsi,r11
  57:	48 83 fe e1          	cmp    rsi,0xffffffffffffffe1
  5b:	40 0f 93 c6          	setae  sil
  5f:	40 08 de             	or     sil,bl
  62:	0f 84 b3 00 00 00    	je     11b <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x11b>
  68:	31 f6                	xor    esi,esi
  6a:	48 8d 7e 01          	lea    rdi,[rsi+0x1]
  6e:	a8 01                	test   al,0x1
  70:	74 26                	je     98 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x98>
  72:	48 89 f3             	mov    rbx,rsi
  75:	48 0f af da          	imul   rbx,rdx
  79:	f2 0f 10 04 d9       	movsd  xmm0,QWORD PTR [rcx+rbx*8]
  7e:	48 89 f3             	mov    rbx,rsi
  81:	49 0f af d9          	imul   rbx,r9
  85:	f2 41 0f 59 04 d8    	mulsd  xmm0,QWORD PTR [r8+rbx*8]
  8b:	49 0f af f2          	imul   rsi,r10
  8f:	f2 41 0f 11 04 f3    	movsd  QWORD PTR [r11+rsi*8],xmm0
  95:	48 89 fe             	mov    rsi,rdi
  98:	48 39 f8             	cmp    rax,rdi
  9b:	74 74                	je     111 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x111>
  9d:	48 29 f0             	sub    rax,rsi
  a0:	48 8d 7e 01          	lea    rdi,[rsi+0x1]
  a4:	4c 89 d3             	mov    rbx,r10
  a7:	48 0f af df          	imul   rbx,rdi
  ab:	4d 89 ce             	mov    r14,r9
  ae:	4c 0f af f7          	imul   r14,rdi
  b2:	48 0f af fa          	imul   rdi,rdx
  b6:	49 89 f7             	mov    r15,rsi
  b9:	4d 0f af fa          	imul   r15,r10
  bd:	49 c1 e2 04          	shl    r10,0x4
  c1:	49 89 f4             	mov    r12,rsi
  c4:	4d 0f af e1          	imul   r12,r9
  c8:	49 c1 e1 04          	shl    r9,0x4
  cc:	48 0f af f2          	imul   rsi,rdx
  d0:	48 c1 e2 04          	shl    rdx,0x4
  d4:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
  db:	00 00 00 00 00 
  e0:	f2 0f 10 04 f1       	movsd  xmm0,QWORD PTR [rcx+rsi*8]
  e5:	f2 43 0f 59 04 e0    	mulsd  xmm0,QWORD PTR [r8+r12*8]
  eb:	f2 43 0f 11 04 fb    	movsd  QWORD PTR [r11+r15*8],xmm0
  f1:	f2 0f 10 04 f9       	movsd  xmm0,QWORD PTR [rcx+rdi*8]
  f6:	f2 43 0f 59 04 f0    	mulsd  xmm0,QWORD PTR [r8+r14*8]
  fc:	f2 41 0f 11 04 db    	movsd  QWORD PTR [r11+rbx*8],xmm0
 102:	4d 01 d3             	add    r11,r10
 105:	4d 01 c8             	add    r8,r9
 108:	48 01 d1             	add    rcx,rdx
 10b:	48 83 c0 fe          	add    rax,0xfffffffffffffffe
 10f:	75 cf                	jne    e0 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xe0>
 111:	5b                   	pop    rbx
 112:	5f                   	pop    rdi
 113:	5e                   	pop    rsi
 114:	41 5c                	pop    r12
 116:	41 5e                	pop    r14
 118:	41 5f                	pop    r15
 11a:	c3                   	ret
 11b:	48 89 c6             	mov    rsi,rax
 11e:	48 83 e6 fc          	and    rsi,0xfffffffffffffffc
 122:	31 ff                	xor    edi,edi
 124:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
 12b:	00 00 00 00 00 
 130:	66 0f 10 04 f9       	movupd xmm0,XMMWORD PTR [rcx+rdi*8]
 135:	66 0f 10 4c f9 10    	movupd xmm1,XMMWORD PTR [rcx+rdi*8+0x10]
 13b:	66 41 0f 10 14 f8    	movupd xmm2,XMMWORD PTR [r8+rdi*8]
 141:	66 0f 59 d0          	mulpd  xmm2,xmm0
 145:	66 41 0f 10 44 f8 10 	movupd xmm0,XMMWORD PTR [r8+rdi*8+0x10]
 14c:	66 0f 59 c1          	mulpd  xmm0,xmm1
 150:	66 41 0f 11 14 fb    	movupd XMMWORD PTR [r11+rdi*8],xmm2
 156:	66 41 0f 11 44 fb 10 	movupd XMMWORD PTR [r11+rdi*8+0x10],xmm0
 15d:	48 83 c7 04          	add    rdi,0x4
 161:	48 39 fe             	cmp    rsi,rdi
 164:	75 ca                	jne    130 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x130>
 166:	48 39 f0             	cmp    rax,rsi
 169:	74 a6                	je     111 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x111>
 16b:	e9 fa fe ff ff       	jmp    6a <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x6a>

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIfEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)>:
   0:	56                   	push   rsi
   1:	57                   	push   rdi
   2:	53                   	push   rbx
   3:	48 83 ec 50          	sub    rsp,0x50
   7:	44 0f 29 54 24 40    	movaps XMMWORD PTR [rsp+0x40],xmm10
   d:	44 0f 29 4c 24 30    	movaps XMMWORD PTR [rsp+0x30],xmm9
  13:	44 0f 29 44 24 20    	movaps XMMWORD PTR [rsp+0x20],xmm8
  19:	0f 29 7c 24 10       	movaps XMMWORD PTR [rsp+0x10],xmm7
  1e:	0f 29 34 24          	movaps XMMWORD PTR [rsp],xmm6
  22:	48 8b 84 24 98 00 00 	mov    rax,QWORD PTR [rsp+0x98]
  29:	00 
  2a:	48 85 c0             	test   rax,rax
  2d:	0f 84 e2 01 00 00    	je     215 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x215>
  33:	48 8b 8c 24 90 00 00 	mov    rcx,QWORD PTR [rsp+0x90]
  3a:	00 
  3b:	f3 41 0f 10 19       	movss  xmm3,DWORD PTR [r9]
  40:	f3 0f 11 19          	movss  DWORD PTR [rcx],xmm3
  44:	48 83 f8 01          	cmp    rax,0x1
  48:	0f 84 c7 01 00 00    	je     215 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x215>
  4e:	f3 41 0f 10 5c 81 fc 	movss  xmm3,DWORD PTR [r9+rax*4-0x4]
  55:	f3 0f 11 5c 81 fc    	movss  DWORD PTR [rcx+rax*4-0x4],xmm3
  5b:	48 83 f8 03          	cmp    rax,0x3
  5f:	0f 82 b0 01 00 00    	jb     215 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x215>
  65:	4c 8d 50 fe          	lea    r10,[rax-0x2]
  69:	41 b8 01 00 00 00    	mov    r8d,0x1
  6f:	ba 02 00 00 00       	mov    edx,0x2
  74:	49 83 fa 08          	cmp    r10,0x8
  78:	0f 82 b6 00 00 00    	jb     134 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x134>
  7e:	4c 8d 59 04          	lea    r11,[rcx+0x4]
  82:	48 8d 34 81          	lea    rsi,[rcx+rax*4]
  86:	48 83 c6 fc          	add    rsi,0xfffffffffffffffc
  8a:	49 8d 3c 81          	lea    rdi,[r9+rax*4]
  8e:	49 39 fb             	cmp    r11,rdi
  91:	41 0f 92 c3          	setb   r11b
  95:	49 39 f1             	cmp    r9,rsi
  98:	0f 92 c3             	setb   bl
  9b:	41 84 db             	test   r11b,bl
  9e:	0f 85 90 00 00 00    	jne    134 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x134>
  a4:	4d 89 d3             	mov    r11,r10
  a7:	49 83 e3 f8          	and    r11,0xfffffffffffffff8
  ab:	49 8d 53 02          	lea    rdx,[r11+0x2]
  af:	4d 8d 43 01          	lea    r8,[r11+0x1]
  b3:	0f 28 d9             	movaps xmm3,xmm1
  b6:	0f c6 d9 00          	shufps xmm3,xmm1,0x0
  ba:	0f 28 e0             	movaps xmm4,xmm0
  bd:	0f c6 e0 00          	shufps xmm4,xmm0,0x0
  c1:	0f 28 ea             	movaps xmm5,xmm2
  c4:	0f c6 ea 00          	shufps xmm5,xmm2,0x0
  c8:	31 f6                	xor    esi,esi
  ca:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  d0:	41 0f 10 34 b1       	movups xmm6,XMMWORD PTR [r9+rsi*4]
  d5:	41 0f 10 7c b1 04    	movups xmm7,XMMWORD PTR [r9+rsi*4+0x4]
  db:	45 0f 10 44 b1 08    	movups xmm8,XMMWORD PTR [r9+rsi*4+0x8]
  e1:	45 0f 10 4c b1 10    	movups xmm9,XMMWORD PTR [r9+rsi*4+0x10]
  e7:	45 0f 10 54 b1 14    	movups xmm10,XMMWORD PTR [r9+rsi*4+0x14]
  ed:	0f 59 fb             	mulps  xmm7,xmm3
  f0:	44 0f 59 d3          	mulps  xmm10,xmm3
  f4:	0f 59 f4             	mulps  xmm6,xmm4
  f7:	0f 58 f7             	addps  xmm6,xmm7
  fa:	44 0f 59 cc          	mulps  xmm9,xmm4
  fe:	45 0f 58 ca          	addps  xmm9,xmm10
 102:	41 0f 10 7c b1 18    	movups xmm7,XMMWORD PTR [r9+rsi*4+0x18]
 108:	44 0f 59 c5          	mulps  xmm8,xmm5
 10c:	44 0f 58 c6          	addps  xmm8,xmm6
 110:	0f 59 fd             	mulps  xmm7,xmm5
 113:	41 0f 58 f9          	addps  xmm7,xmm9
 117:	44 0f 11 44 b1 04    	movups XMMWORD PTR [rcx+rsi*4+0x4],xmm8
 11d:	0f 11 7c b1 14       	movups XMMWORD PTR [rcx+rsi*4+0x14],xmm7
 122:	48 83 c6 08          	add    rsi,0x8
 126:	49 39 f3             	cmp    r11,rsi
 129:	75 a5                	jne    d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0xd0>
 12b:	4d 39 da             	cmp    r10,r11
 12e:	0f 84 e1 00 00 00    	je     215 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x215>
 134:	41 89 c3             	mov    r11d,eax
 137:	41 29 d3             	sub    r11d,edx
 13a:	4c 8d 52 01          	lea    r10,[rdx+0x1]
 13e:	41 f6 c3 01          	test   r11b,0x1
 142:	75 10                	jne    154 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x154>
 144:	49 89 d3             	mov    r11,rdx
 147:	4c 89 c2             	mov    rdx,r8
 14a:	4c 39 d0             	cmp    rax,r10
 14d:	75 3e                	jne    18d <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x18d>
 14f:	e9 c1 00 00 00       	jmp    215 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x215>
 154:	f3 43 0f 10 1c 81    	movss  xmm3,DWORD PTR [r9+r8*4]
 15a:	f3 0f 59 d9          	mulss  xmm3,xmm1
 15e:	f3 43 0f 10 64 81 fc 	movss  xmm4,DWORD PTR [r9+r8*4-0x4]
 165:	f3 0f 59 e0          	mulss  xmm4,xmm0
 169:	f3 0f 58 e3          	addss  xmm4,xmm3
 16d:	f3 41 0f 10 1c 91    	movss  xmm3,DWORD PTR [r9+rdx*4]
 173:	f3 0f 59 da          	mulss  xmm3,xmm2
 177:	f3 0f 58 dc          	addss  xmm3,xmm4
 17b:	f3 42 0f 11 1c 81    	movss  DWORD PTR [rcx+r8*4],xmm3
 181:	4d 89 d3             	mov    r11,r10
 184:	4c 39 d0             	cmp    rax,r10
 187:	0f 84 88 00 00 00    	je     215 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x215>
 18d:	48 f7 d8             	neg    rax
 190:	49 ff c3             	inc    r11
 193:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
 19a:	84 00 00 00 00 00 
 1a0:	49 89 d0             	mov    r8,rdx
 1a3:	4c 89 da             	mov    rdx,r11
 1a6:	f3 43 0f 10 1c 81    	movss  xmm3,DWORD PTR [r9+r8*4]
 1ac:	f3 0f 59 d9          	mulss  xmm3,xmm1
 1b0:	f3 43 0f 10 64 81 fc 	movss  xmm4,DWORD PTR [r9+r8*4-0x4]
 1b7:	f3 0f 59 e0          	mulss  xmm4,xmm0
 1bb:	f3 0f 58 e3          	addss  xmm4,xmm3
 1bf:	f3 43 0f 10 5c 99 fc 	movss  xmm3,DWORD PTR [r9+r11*4-0x4]
 1c6:	f3 0f 59 da          	mulss  xmm3,xmm2
 1ca:	f3 0f 58 dc          	addss  xmm3,xmm4
 1ce:	f3 42 0f 11 1c 81    	movss  DWORD PTR [rcx+r8*4],xmm3
 1d4:	f3 43 0f 10 5c 99 fc 	movss  xmm3,DWORD PTR [r9+r11*4-0x4]
 1db:	f3 0f 59 d9          	mulss  xmm3,xmm1
 1df:	f3 43 0f 10 64 99 f8 	movss  xmm4,DWORD PTR [r9+r11*4-0x8]
 1e6:	f3 0f 59 e0          	mulss  xmm4,xmm0
 1ea:	f3 0f 58 e3          	addss  xmm4,xmm3
 1ee:	f3 43 0f 10 1c 99    	movss  xmm3,DWORD PTR [r9+r11*4]
 1f4:	f3 0f 59 da          	mulss  xmm3,xmm2
 1f8:	f3 0f 58 dc          	addss  xmm3,xmm4
 1fc:	f3 42 0f 11 5c 99 fc 	movss  DWORD PTR [rcx+r11*4-0x4],xmm3
 203:	49 83 c3 02          	add    r11,0x2
 207:	4c 8d 04 10          	lea    r8,[rax+rdx*1]
 20b:	49 83 c0 02          	add    r8,0x2
 20f:	49 83 f8 01          	cmp    r8,0x1
 213:	75 8b                	jne    1a0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1a0>
 215:	0f 28 34 24          	movaps xmm6,XMMWORD PTR [rsp]
 219:	0f 28 7c 24 10       	movaps xmm7,XMMWORD PTR [rsp+0x10]
 21e:	44 0f 28 44 24 20    	movaps xmm8,XMMWORD PTR [rsp+0x20]
 224:	44 0f 28 4c 24 30    	movaps xmm9,XMMWORD PTR [rsp+0x30]
 22a:	44 0f 28 54 24 40    	movaps xmm10,XMMWORD PTR [rsp+0x40]
 230:	48 83 c4 50          	add    rsp,0x50
 234:	5b                   	pop    rbx
 235:	5f                   	pop    rdi
 236:	5e                   	pop    rsi
 237:	c3                   	ret

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIdEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)>:
   0:	56                   	push   rsi
   1:	57                   	push   rdi
   2:	53                   	push   rbx
   3:	48 83 ec 40          	sub    rsp,0x40
   7:	66 44 0f 29 4c 24 30 	movapd XMMWORD PTR [rsp+0x30],xmm9
   e:	66 44 0f 29 44 24 20 	movapd XMMWORD PTR [rsp+0x20],xmm8
  15:	66 0f 29 7c 24 10    	movapd XMMWORD PTR [rsp+0x10],xmm7
  1b:	66 0f 29 34 24       	movapd XMMWORD PTR [rsp],xmm6
  20:	48 8b 84 24 88 00 00 	mov    rax,QWORD PTR [rsp+0x88]
  27:	00 
  28:	48 85 c0             	test   rax,rax
  2b:	0f 84 f4 01 00 00    	je     225 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x225>
  31:	48 8b 8c 24 80 00 00 	mov    rcx,QWORD PTR [rsp+0x80]
  38:	00 
  39:	f2 41 0f 10 19       	movsd  xmm3,QWORD PTR [r9]
  3e:	f2 0f 11 19          	movsd  QWORD PTR [rcx],xmm3
  42:	48 83 f8 01          	cmp    rax,0x1
  46:	0f 84 d9 01 00 00    	je     225 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x225>
  4c:	f2 41 0f 10 5c c1 f8 	movsd  xmm3,QWORD PTR [r9+rax*8-0x8]
  53:	f2 0f 11 5c c1 f8    	movsd  QWORD PTR [rcx+rax*8-0x8],xmm3
  59:	48 83 f8 03          	cmp    rax,0x3
  5d:	0f 82 c2 01 00 00    	jb     225 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x225>
  63:	4c 8d 50 fe          	lea    r10,[rax-0x2]
  67:	41 b8 01 00 00 00    	mov    r8d,0x1
  6d:	ba 02 00 00 00       	mov    edx,0x2
  72:	49 83 fa 04          	cmp    r10,0x4
  76:	0f 82 c9 00 00 00    	jb     145 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x145>
  7c:	4c 8d 59 08          	lea    r11,[rcx+0x8]
  80:	48 8d 34 c1          	lea    rsi,[rcx+rax*8]
  84:	48 83 c6 f8          	add    rsi,0xfffffffffffffff8
  88:	49 8d 3c c1          	lea    rdi,[r9+rax*8]
  8c:	49 39 fb             	cmp    r11,rdi
  8f:	41 0f 92 c3          	setb   r11b
  93:	49 39 f1             	cmp    r9,rsi
  96:	0f 92 c3             	setb   bl
  99:	41 84 db             	test   r11b,bl
  9c:	0f 85 a3 00 00 00    	jne    145 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x145>
  a2:	4d 89 d3             	mov    r11,r10
  a5:	49 83 e3 fc          	and    r11,0xfffffffffffffffc
  a9:	49 8d 53 02          	lea    rdx,[r11+0x2]
  ad:	4d 8d 43 01          	lea    r8,[r11+0x1]
  b1:	66 0f 28 d9          	movapd xmm3,xmm1
  b5:	66 0f 14 d9          	unpcklpd xmm3,xmm1
  b9:	66 0f 28 e0          	movapd xmm4,xmm0
  bd:	66 0f 14 e0          	unpcklpd xmm4,xmm0
  c1:	66 0f 28 ea          	movapd xmm5,xmm2
  c5:	66 0f 14 ea          	unpcklpd xmm5,xmm2
  c9:	31 f6                	xor    esi,esi
  cb:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
  d0:	66 41 0f 10 34 f1    	movupd xmm6,XMMWORD PTR [r9+rsi*8]
  d6:	66 41 0f 10 7c f1 08 	movupd xmm7,XMMWORD PTR [r9+rsi*8+0x8]
  dd:	66 45 0f 10 44 f1 10 	movupd xmm8,XMMWORD PTR [r9+rsi*8+0x10]
  e4:	66 45 0f 10 4c f1 18 	movupd xmm9,XMMWORD PTR [r9+rsi*8+0x18]
  eb:	66 0f 59 fb          	mulpd  xmm7,xmm3
  ef:	66 44 0f 59 cb       	mulpd  xmm9,xmm3
  f4:	66 0f 59 f4          	mulpd  xmm6,xmm4
  f8:	66 0f 58 f7          	addpd  xmm6,xmm7
  fc:	66 0f 28 fc          	movapd xmm7,xmm4
 100:	66 41 0f 59 f8       	mulpd  xmm7,xmm8
 105:	66 41 0f 58 f9       	addpd  xmm7,xmm9
 10a:	66 45 0f 10 4c f1 20 	movupd xmm9,XMMWORD PTR [r9+rsi*8+0x20]
 111:	66 44 0f 59 c5       	mulpd  xmm8,xmm5
 116:	66 44 0f 58 c6       	addpd  xmm8,xmm6
 11b:	66 44 0f 59 cd       	mulpd  xmm9,xmm5
 120:	66 44 0f 58 cf       	addpd  xmm9,xmm7
 125:	66 44 0f 11 44 f1 08 	movupd XMMWORD PTR [rcx+rsi*8+0x8],xmm8
 12c:	66 44 0f 11 4c f1 18 	movupd XMMWORD PTR [rcx+rsi*8+0x18],xmm9
 133:	48 83 c6 04          	add    rsi,0x4
 137:	49 39 f3             	cmp    r11,rsi
 13a:	75 94                	jne    d0 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0xd0>
 13c:	4d 39 da             	cmp    r10,r11
 13f:	0f 84 e0 00 00 00    	je     225 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x225>
 145:	41 89 c3             	mov    r11d,eax
 148:	41 29 d3             	sub    r11d,edx
 14b:	4c 8d 52 01          	lea    r10,[rdx+0x1]
 14f:	41 f6 c3 01          	test   r11b,0x1
 153:	75 10                	jne    165 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x165>
 155:	49 89 d3             	mov    r11,rdx
 158:	4c 89 c2             	mov    rdx,r8
 15b:	4c 39 d0             	cmp    rax,r10
 15e:	75 3e                	jne    19e <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x19e>
 160:	e9 c0 00 00 00       	jmp    225 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x225>
 165:	f2 43 0f 10 1c c1    	movsd  xmm3,QWORD PTR [r9+r8*8]
 16b:	f2 0f 59 d9          	mulsd  xmm3,xmm1
 16f:	f2 43 0f 10 64 c1 f8 	movsd  xmm4,QWORD PTR [r9+r8*8-0x8]
 176:	f2 0f 59 e0          	mulsd  xmm4,xmm0
 17a:	f2 0f 58 e3          	addsd  xmm4,xmm3
 17e:	f2 41 0f 10 1c d1    	movsd  xmm3,QWORD PTR [r9+rdx*8]
 184:	f2 0f 59 da          	mulsd  xmm3,xmm2
 188:	f2 0f 58 dc          	addsd  xmm3,xmm4
 18c:	f2 42 0f 11 1c c1    	movsd  QWORD PTR [rcx+r8*8],xmm3
 192:	4d 89 d3             	mov    r11,r10
 195:	4c 39 d0             	cmp    rax,r10
 198:	0f 84 87 00 00 00    	je     225 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x225>
 19e:	48 f7 d8             	neg    rax
 1a1:	49 ff c3             	inc    r11
 1a4:	66 66 66 2e 0f 1f 84 	data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
 1ab:	00 00 00 00 00 
 1b0:	49 89 d0             	mov    r8,rdx
 1b3:	4c 89 da             	mov    rdx,r11
 1b6:	f2 43 0f 10 1c c1    	movsd  xmm3,QWORD PTR [r9+r8*8]
 1bc:	f2 0f 59 d9          	mulsd  xmm3,xmm1
 1c0:	f2 43 0f 10 64 c1 f8 	movsd  xmm4,QWORD PTR [r9+r8*8-0x8]
 1c7:	f2 0f 59 e0          	mulsd  xmm4,xmm0
 1cb:	f2 0f 58 e3          	addsd  xmm4,xmm3
 1cf:	f2 43 0f 10 5c d9 f8 	movsd  xmm3,QWORD PTR [r9+r11*8-0x8]
 1d6:	f2 0f 59 da          	mulsd  xmm3,xmm2
 1da:	f2 0f 58 dc          	addsd  xmm3,xmm4
 1de:	f2 42 0f 11 1c c1    	movsd  QWORD PTR [rcx+r8*8],xmm3
 1e4:	f2 43 0f 10 5c d9 f8 	movsd  xmm3,QWORD PTR [r9+r11*8-0x8]
 1eb:	f2 0f 59 d9          	mulsd  xmm3,xmm1
 1ef:	f2 43 0f 10 64 d9 f0 	movsd  xmm4,QWORD PTR [r9+r11*8-0x10]
 1f6:	f2 0f 59 e0          	mulsd  xmm4,xmm0
 1fa:	f2 0f 58 e3          	addsd  xmm4,xmm3
 1fe:	f2 43 0f 10 1c d9    	movsd  xmm3,QWORD PTR [r9+r11*8]
 204:	f2 0f 59 da          	mulsd  xmm3,xmm2
 208:	f2 0f 58 dc          	addsd  xmm3,xmm4
 20c:	f2 42 0f 11 5c d9 f8 	movsd  QWORD PTR [rcx+r11*8-0x8],xmm3
 213:	49 83 c3 02          	add    r11,0x2
 217:	4c 8d 04 10          	lea    r8,[rax+rdx*1]
 21b:	49 83 c0 02          	add    r8,0x2
 21f:	49 83 f8 01          	cmp    r8,0x1
 223:	75 8b                	jne    1b0 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x1b0>
 225:	0f 28 34 24          	movaps xmm6,XMMWORD PTR [rsp]
 229:	0f 28 7c 24 10       	movaps xmm7,XMMWORD PTR [rsp+0x10]
 22e:	44 0f 28 44 24 20    	movaps xmm8,XMMWORD PTR [rsp+0x20]
 234:	44 0f 28 4c 24 30    	movaps xmm9,XMMWORD PTR [rsp+0x30]
 23a:	48 83 c4 40          	add    rsp,0x40
 23e:	5b                   	pop    rbx
 23f:	5f                   	pop    rdi
 240:	5e                   	pop    rsi
 241:	c3                   	ret
