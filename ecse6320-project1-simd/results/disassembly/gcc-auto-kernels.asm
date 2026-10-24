; Targeted disassembly: gcc-auto
; Object file: 
C:\Users\CHOUDN3\Downloads\EcSE_4320\ecse6320-project1-simd\build-gcc-auto\CMakeFiles\project_kernels.dir\src\kernels.cpp.obj
; GNU objdump -d -C -Mintel; project_kernels symbols only.

0000000000000000 <void project::axpy<float>(float, float const*, float*, unsigned long long)>:
   0:	0f 28 d8             	movaps xmm3,xmm0
   3:	0f c6 db 00          	shufps xmm3,xmm3,0x0
   7:	4d 85 c9             	test   r9,r9
   a:	0f 84 c2 00 00 00    	je     d2 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xd2>
  10:	49 83 f9 01          	cmp    r9,0x1
  14:	0f 84 be 00 00 00    	je     d8 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xd8>
  1a:	49 8d 40 fc          	lea    rax,[r8-0x4]
  1e:	48 29 d0             	sub    rax,rdx
  21:	48 83 f8 08          	cmp    rax,0x8
  25:	0f 86 ad 00 00 00    	jbe    d8 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xd8>
  2b:	49 8d 41 ff          	lea    rax,[r9-0x1]
  2f:	48 83 f8 02          	cmp    rax,0x2
  33:	0f 86 c6 00 00 00    	jbe    ff <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xff>
  39:	4c 89 c9             	mov    rcx,r9
  3c:	0f 28 d3             	movaps xmm2,xmm3
  3f:	31 c0                	xor    eax,eax
  41:	48 c1 e9 02          	shr    rcx,0x2
  45:	49 89 ca             	mov    r10,rcx
  48:	49 c1 e2 04          	shl    r10,0x4
  4c:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  53:	00 00 
  55:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  5c:	00 00 00 00 
  60:	0f 10 0c 02          	movups xmm1,XMMWORD PTR [rdx+rax*1]
  64:	41 0f 10 24 00       	movups xmm4,XMMWORD PTR [r8+rax*1]
  69:	0f 59 ca             	mulps  xmm1,xmm2
  6c:	0f 58 cc             	addps  xmm1,xmm4
  6f:	41 0f 11 0c 00       	movups XMMWORD PTR [r8+rax*1],xmm1
  74:	48 83 c0 10          	add    rax,0x10
  78:	4c 39 d0             	cmp    rax,r10
  7b:	75 e3                	jne    60 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x60>
  7d:	48 8d 04 8d 00 00 00 	lea    rax,[rcx*4+0x0]
  84:	00 
  85:	49 39 c1             	cmp    r9,rax
  88:	74 48                	je     d2 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xd2>
  8a:	49 29 c1             	sub    r9,rax
  8d:	49 83 f9 01          	cmp    r9,0x1
  91:	74 2e                	je     c1 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xc1>
  93:	f3 0f 7e 0c 82       	movq   xmm1,QWORD PTR [rdx+rax*4]
  98:	f3 0f 7e db          	movq   xmm3,xmm3
  9c:	f3 41 0f 7e 14 80    	movq   xmm2,QWORD PTR [r8+rax*4]
  a2:	4c 89 c9             	mov    rcx,r9
  a5:	48 83 e1 fe          	and    rcx,0xfffffffffffffffe
  a9:	41 83 e1 01          	and    r9d,0x1
  ad:	0f 59 cb             	mulps  xmm1,xmm3
  b0:	f3 0f 7e c9          	movq   xmm1,xmm1
  b4:	0f 58 ca             	addps  xmm1,xmm2
  b7:	41 0f 13 0c 80       	movlps QWORD PTR [r8+rax*4],xmm1
  bc:	74 14                	je     d2 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xd2>
  be:	48 01 c8             	add    rax,rcx
  c1:	f3 0f 59 04 82       	mulss  xmm0,DWORD PTR [rdx+rax*4]
  c6:	f3 41 0f 58 04 80    	addss  xmm0,DWORD PTR [r8+rax*4]
  cc:	f3 41 0f 11 04 80    	movss  DWORD PTR [r8+rax*4],xmm0
  d2:	c3                   	ret
  d3:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
  d8:	31 c0                	xor    eax,eax
  da:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  e0:	f3 0f 10 0c 82       	movss  xmm1,DWORD PTR [rdx+rax*4]
  e5:	f3 0f 59 c8          	mulss  xmm1,xmm0
  e9:	f3 41 0f 58 0c 80    	addss  xmm1,DWORD PTR [r8+rax*4]
  ef:	f3 41 0f 11 0c 80    	movss  DWORD PTR [r8+rax*4],xmm1
  f5:	48 83 c0 01          	add    rax,0x1
  f9:	49 39 c1             	cmp    r9,rax
  fc:	75 e2                	jne    e0 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xe0>
  fe:	c3                   	ret
  ff:	31 c0                	xor    eax,eax
 101:	eb 90                	jmp    93 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x93>
 103:	90                   	nop
 104:	90                   	nop
 105:	90                   	nop
 106:	90                   	nop
 107:	90                   	nop
 108:	90                   	nop
 109:	90                   	nop
 10a:	90                   	nop
 10b:	90                   	nop
 10c:	90                   	nop
 10d:	90                   	nop
 10e:	90                   	nop
 10f:	90                   	nop
 110:	90                   	nop
 111:	90                   	nop
 112:	90                   	nop
 113:	90                   	nop
 114:	90                   	nop
 115:	90                   	nop
 116:	90                   	nop
 117:	90                   	nop
 118:	90                   	nop
 119:	90                   	nop
 11a:	90                   	nop
 11b:	90                   	nop
 11c:	90                   	nop
 11d:	90                   	nop
 11e:	90                   	nop
 11f:	90                   	nop

Disassembly of section .text$_ZN7project4axpyIdEEvT_PKS1_PS1_y:


0000000000000000 <void project::axpy<double>(double, double const*, double*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	74 75                	je     7a <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x7a>
   5:	49 83 f9 01          	cmp    r9,0x1
   9:	74 75                	je     80 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x80>
   b:	4c 89 c0             	mov    rax,r8
   e:	48 29 d0             	sub    rax,rdx
  11:	48 83 f8 08          	cmp    rax,0x8
  15:	74 69                	je     80 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x80>
  17:	4d 89 ca             	mov    r10,r9
  1a:	f2 0f 12 d0          	movddup xmm2,xmm0
  1e:	31 c0                	xor    eax,eax
  20:	49 d1 ea             	shr    r10,1
  23:	4c 89 d1             	mov    rcx,r10
  26:	48 c1 e1 04          	shl    rcx,0x4
  2a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  31:	00 00 00 00 
  35:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  3c:	00 00 00 00 
  40:	66 0f 10 0c 02       	movupd xmm1,XMMWORD PTR [rdx+rax*1]
  45:	66 41 0f 10 1c 00    	movupd xmm3,XMMWORD PTR [r8+rax*1]
  4b:	66 0f 59 ca          	mulpd  xmm1,xmm2
  4f:	66 0f 58 cb          	addpd  xmm1,xmm3
  53:	41 0f 11 0c 00       	movups XMMWORD PTR [r8+rax*1],xmm1
  58:	48 83 c0 10          	add    rax,0x10
  5c:	48 39 c1             	cmp    rcx,rax
  5f:	75 df                	jne    40 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x40>
  61:	4d 01 d2             	add    r10,r10
  64:	4d 39 d1             	cmp    r9,r10
  67:	74 11                	je     7a <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x7a>
  69:	f2 0f 59 04 0a       	mulsd  xmm0,QWORD PTR [rdx+rcx*1]
  6e:	f2 41 0f 58 04 08    	addsd  xmm0,QWORD PTR [r8+rcx*1]
  74:	f2 41 0f 11 04 08    	movsd  QWORD PTR [r8+rcx*1],xmm0
  7a:	c3                   	ret
  7b:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
  80:	31 c0                	xor    eax,eax
  82:	0f 1f 84 00 00 00 00 	nop    DWORD PTR [rax+rax*1+0x0]
  89:	00 
  8a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  91:	00 00 00 00 
  95:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  9c:	00 00 00 00 
  a0:	f2 0f 10 0c c2       	movsd  xmm1,QWORD PTR [rdx+rax*8]
  a5:	f2 0f 59 c8          	mulsd  xmm1,xmm0
  a9:	f2 41 0f 58 0c c0    	addsd  xmm1,QWORD PTR [r8+rax*8]
  af:	f2 41 0f 11 0c c0    	movsd  QWORD PTR [r8+rax*8],xmm1
  b5:	48 83 c0 01          	add    rax,0x1
  b9:	49 39 c1             	cmp    r9,rax
  bc:	75 e2                	jne    a0 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xa0>
  be:	c3                   	ret
  bf:	90                   	nop

Disassembly of section .text$_ZN7project11dot_productIfEET_PKS1_S3_y:


0000000000000000 <float project::dot_product<float>(float const*, float const*, unsigned long long)>:
   0:	4d 85 c0             	test   r8,r8
   3:	0f 84 bf 00 00 00    	je     c8 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xc8>
   9:	49 8d 40 ff          	lea    rax,[r8-0x1]
   d:	48 83 f8 02          	cmp    rax,0x2
  11:	0f 86 b6 00 00 00    	jbe    cd <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xcd>
  17:	4d 89 c1             	mov    r9,r8
  1a:	31 c0                	xor    eax,eax
  1c:	66 0f ef c0          	pxor   xmm0,xmm0
  20:	49 c1 e9 02          	shr    r9,0x2
  24:	4d 89 ca             	mov    r10,r9
  27:	49 c1 e2 04          	shl    r10,0x4
  2b:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  32:	00 00 00 
  35:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  3c:	00 00 00 00 
  40:	0f 10 0c 01          	movups xmm1,XMMWORD PTR [rcx+rax*1]
  44:	0f 10 1c 02          	movups xmm3,XMMWORD PTR [rdx+rax*1]
  48:	48 83 c0 10          	add    rax,0x10
  4c:	0f 59 cb             	mulps  xmm1,xmm3
  4f:	f3 0f 58 c1          	addss  xmm0,xmm1
  53:	0f 28 d1             	movaps xmm2,xmm1
  56:	0f c6 d1 55          	shufps xmm2,xmm1,0x55
  5a:	f3 0f 58 c2          	addss  xmm0,xmm2
  5e:	0f 28 d1             	movaps xmm2,xmm1
  61:	0f 15 d1             	unpckhps xmm2,xmm1
  64:	0f c6 c9 ff          	shufps xmm1,xmm1,0xff
  68:	f3 0f 58 c2          	addss  xmm0,xmm2
  6c:	f3 0f 58 c1          	addss  xmm0,xmm1
  70:	4c 39 d0             	cmp    rax,r10
  73:	75 cb                	jne    40 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x40>
  75:	4a 8d 04 8d 00 00 00 	lea    rax,[r9*4+0x0]
  7c:	00 
  7d:	49 39 c0             	cmp    r8,rax
  80:	74 40                	je     c2 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xc2>
  82:	f3 0f 10 0c 81       	movss  xmm1,DWORD PTR [rcx+rax*4]
  87:	f3 0f 59 0c 82       	mulss  xmm1,DWORD PTR [rdx+rax*4]
  8c:	4c 8d 48 01          	lea    r9,[rax+0x1]
  90:	f3 0f 58 c1          	addss  xmm0,xmm1
  94:	4d 39 c1             	cmp    r9,r8
  97:	73 29                	jae    c2 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xc2>
  99:	f3 0f 10 4c 81 04    	movss  xmm1,DWORD PTR [rcx+rax*4+0x4]
  9f:	f3 0f 59 4c 82 04    	mulss  xmm1,DWORD PTR [rdx+rax*4+0x4]
  a5:	4c 8d 48 02          	lea    r9,[rax+0x2]
  a9:	f3 0f 58 c1          	addss  xmm0,xmm1
  ad:	4d 39 c1             	cmp    r9,r8
  b0:	73 10                	jae    c2 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xc2>
  b2:	f3 0f 10 4c 82 08    	movss  xmm1,DWORD PTR [rdx+rax*4+0x8]
  b8:	f3 0f 59 4c 81 08    	mulss  xmm1,DWORD PTR [rcx+rax*4+0x8]
  be:	f3 0f 58 c1          	addss  xmm0,xmm1
  c2:	c3                   	ret
  c3:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
  c8:	66 0f ef c0          	pxor   xmm0,xmm0
  cc:	c3                   	ret
  cd:	66 0f ef c0          	pxor   xmm0,xmm0
  d1:	31 c0                	xor    eax,eax
  d3:	eb ad                	jmp    82 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x82>
  d5:	90                   	nop
  d6:	90                   	nop
  d7:	90                   	nop
  d8:	90                   	nop
  d9:	90                   	nop
  da:	90                   	nop
  db:	90                   	nop
  dc:	90                   	nop
  dd:	90                   	nop
  de:	90                   	nop
  df:	90                   	nop
  e0:	90                   	nop
  e1:	90                   	nop
  e2:	90                   	nop
  e3:	90                   	nop
  e4:	90                   	nop
  e5:	90                   	nop
  e6:	90                   	nop
  e7:	90                   	nop
  e8:	90                   	nop
  e9:	90                   	nop
  ea:	90                   	nop
  eb:	90                   	nop
  ec:	90                   	nop
  ed:	90                   	nop
  ee:	90                   	nop
  ef:	90                   	nop
  f0:	90                   	nop
  f1:	90                   	nop
  f2:	90                   	nop
  f3:	90                   	nop
  f4:	90                   	nop
  f5:	90                   	nop
  f6:	90                   	nop
  f7:	90                   	nop
  f8:	90                   	nop
  f9:	90                   	nop
  fa:	90                   	nop
  fb:	90                   	nop
  fc:	90                   	nop
  fd:	90                   	nop
  fe:	90                   	nop
  ff:	90                   	nop

Disassembly of section .text$_ZN7project11dot_productIdEET_PKS1_S3_y:


0000000000000000 <double project::dot_product<double>(double const*, double const*, unsigned long long)>:
   0:	4d 85 c0             	test   r8,r8
   3:	74 7b                	je     80 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x80>
   5:	49 83 f8 01          	cmp    r8,0x1
   9:	74 7a                	je     85 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x85>
   b:	4d 89 c2             	mov    r10,r8
   e:	31 c0                	xor    eax,eax
  10:	66 0f ef c0          	pxor   xmm0,xmm0
  14:	49 d1 ea             	shr    r10,1
  17:	4d 89 d1             	mov    r9,r10
  1a:	49 c1 e1 04          	shl    r9,0x4
  1e:	90                   	nop
  1f:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  26:	00 00 00 00 
  2a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  31:	00 00 00 00 
  35:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  3c:	00 00 00 00 
  40:	66 0f 10 0c 01       	movupd xmm1,XMMWORD PTR [rcx+rax*1]
  45:	66 0f 10 1c 02       	movupd xmm3,XMMWORD PTR [rdx+rax*1]
  4a:	48 83 c0 10          	add    rax,0x10
  4e:	66 0f 59 cb          	mulpd  xmm1,xmm3
  52:	f2 0f 58 c1          	addsd  xmm0,xmm1
  56:	66 0f 15 c9          	unpckhpd xmm1,xmm1
  5a:	f2 0f 58 c1          	addsd  xmm0,xmm1
  5e:	4c 39 c8             	cmp    rax,r9
  61:	75 dd                	jne    40 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x40>
  63:	4b 8d 04 12          	lea    rax,[r10+r10*1]
  67:	49 39 c0             	cmp    r8,rax
  6a:	74 0e                	je     7a <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x7a>
  6c:	f2 0f 10 0c c2       	movsd  xmm1,QWORD PTR [rdx+rax*8]
  71:	f2 0f 59 0c c1       	mulsd  xmm1,QWORD PTR [rcx+rax*8]
  76:	f2 0f 58 c1          	addsd  xmm0,xmm1
  7a:	c3                   	ret
  7b:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
  80:	66 0f ef c0          	pxor   xmm0,xmm0
  84:	c3                   	ret
  85:	66 0f ef c0          	pxor   xmm0,xmm0
  89:	31 c0                	xor    eax,eax
  8b:	eb df                	jmp    6c <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x6c>
  8d:	90                   	nop
  8e:	90                   	nop
  8f:	90                   	nop
  90:	90                   	nop
  91:	90                   	nop
  92:	90                   	nop
  93:	90                   	nop
  94:	90                   	nop
  95:	90                   	nop
  96:	90                   	nop
  97:	90                   	nop
  98:	90                   	nop
  99:	90                   	nop
  9a:	90                   	nop
  9b:	90                   	nop
  9c:	90                   	nop
  9d:	90                   	nop
  9e:	90                   	nop
  9f:	90                   	nop
  a0:	90                   	nop
  a1:	90                   	nop
  a2:	90                   	nop
  a3:	90                   	nop
  a4:	90                   	nop
  a5:	90                   	nop
  a6:	90                   	nop
  a7:	90                   	nop
  a8:	90                   	nop
  a9:	90                   	nop
  aa:	90                   	nop
  ab:	90                   	nop
  ac:	90                   	nop
  ad:	90                   	nop
  ae:	90                   	nop
  af:	90                   	nop
  b0:	90                   	nop
  b1:	90                   	nop
  b2:	90                   	nop
  b3:	90                   	nop
  b4:	90                   	nop
  b5:	90                   	nop
  b6:	90                   	nop
  b7:	90                   	nop
  b8:	90                   	nop
  b9:	90                   	nop
  ba:	90                   	nop
  bb:	90                   	nop
  bc:	90                   	nop
  bd:	90                   	nop
  be:	90                   	nop
  bf:	90                   	nop

Disassembly of section .text$_ZN7project20elementwise_multiplyIfEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 b8 00 00 00    	je     c1 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc1>
   9:	49 83 f9 01          	cmp    r9,0x1
   d:	0f 84 b5 00 00 00    	je     c8 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc8>
  13:	49 8d 40 fc          	lea    rax,[r8-0x4]
  17:	49 89 c2             	mov    r10,rax
  1a:	49 29 ca             	sub    r10,rcx
  1d:	49 83 fa 08          	cmp    r10,0x8
  21:	0f 86 a1 00 00 00    	jbe    c8 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc8>
  27:	48 29 d0             	sub    rax,rdx
  2a:	48 83 f8 08          	cmp    rax,0x8
  2e:	0f 86 94 00 00 00    	jbe    c8 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc8>
  34:	49 8d 41 ff          	lea    rax,[r9-0x1]
  38:	48 83 f8 02          	cmp    rax,0x2
  3c:	0f 86 b8 00 00 00    	jbe    fa <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xfa>
  42:	4d 89 ca             	mov    r10,r9
  45:	31 c0                	xor    eax,eax
  47:	49 c1 ea 02          	shr    r10,0x2
  4b:	4d 89 d3             	mov    r11,r10
  4e:	49 c1 e3 04          	shl    r11,0x4
  52:	0f 1f 00             	nop    DWORD PTR [rax]
  55:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  5c:	00 00 00 00 
  60:	0f 10 04 01          	movups xmm0,XMMWORD PTR [rcx+rax*1]
  64:	0f 10 14 02          	movups xmm2,XMMWORD PTR [rdx+rax*1]
  68:	0f 59 c2             	mulps  xmm0,xmm2
  6b:	41 0f 11 04 00       	movups XMMWORD PTR [r8+rax*1],xmm0
  70:	48 83 c0 10          	add    rax,0x10
  74:	4c 39 d8             	cmp    rax,r11
  77:	75 e7                	jne    60 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x60>
  79:	4a 8d 04 95 00 00 00 	lea    rax,[r10*4+0x0]
  80:	00 
  81:	49 39 c1             	cmp    r9,rax
  84:	74 3b                	je     c1 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc1>
  86:	49 29 c1             	sub    r9,rax
  89:	49 83 f9 01          	cmp    r9,0x1
  8d:	74 22                	je     b1 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xb1>
  8f:	f3 0f 7e 0c 82       	movq   xmm1,QWORD PTR [rdx+rax*4]
  94:	f3 0f 7e 04 81       	movq   xmm0,QWORD PTR [rcx+rax*4]
  99:	4d 89 ca             	mov    r10,r9
  9c:	49 83 e2 fe          	and    r10,0xfffffffffffffffe
  a0:	41 83 e1 01          	and    r9d,0x1
  a4:	0f 59 c1             	mulps  xmm0,xmm1
  a7:	41 0f 13 04 80       	movlps QWORD PTR [r8+rax*4],xmm0
  ac:	74 13                	je     c1 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc1>
  ae:	4c 01 d0             	add    rax,r10
  b1:	f3 0f 10 04 81       	movss  xmm0,DWORD PTR [rcx+rax*4]
  b6:	f3 0f 59 04 82       	mulss  xmm0,DWORD PTR [rdx+rax*4]
  bb:	f3 41 0f 11 04 80    	movss  DWORD PTR [r8+rax*4],xmm0
  c1:	c3                   	ret
  c2:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  c8:	31 c0                	xor    eax,eax
  ca:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  d1:	00 00 00 00 
  d5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  dc:	00 00 00 00 
  e0:	f3 0f 10 04 81       	movss  xmm0,DWORD PTR [rcx+rax*4]
  e5:	f3 0f 59 04 82       	mulss  xmm0,DWORD PTR [rdx+rax*4]
  ea:	f3 41 0f 11 04 80    	movss  DWORD PTR [r8+rax*4],xmm0
  f0:	48 83 c0 01          	add    rax,0x1
  f4:	49 39 c1             	cmp    r9,rax
  f7:	75 e7                	jne    e0 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xe0>
  f9:	c3                   	ret
  fa:	31 c0                	xor    eax,eax
  fc:	eb 91                	jmp    8f <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x8f>
  fe:	90                   	nop
  ff:	90                   	nop

Disassembly of section .text$_ZN7project20elementwise_multiplyIdEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)>:
   0:	49 89 ca             	mov    r10,rcx
   3:	49 89 d3             	mov    r11,rdx
   6:	4d 85 c9             	test   r9,r9
   9:	74 72                	je     7d <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x7d>
   b:	49 8d 41 ff          	lea    rax,[r9-0x1]
   f:	48 83 f8 01          	cmp    rax,0x1
  13:	76 6b                	jbe    80 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x80>
  15:	4c 89 c0             	mov    rax,r8
  18:	48 29 c8             	sub    rax,rcx
  1b:	48 83 f8 08          	cmp    rax,0x8
  1f:	74 5f                	je     80 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x80>
  21:	4c 89 c0             	mov    rax,r8
  24:	48 29 d0             	sub    rax,rdx
  27:	48 83 f8 08          	cmp    rax,0x8
  2b:	74 53                	je     80 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x80>
  2d:	4c 89 c9             	mov    rcx,r9
  30:	31 c0                	xor    eax,eax
  32:	48 d1 e9             	shr    rcx,1
  35:	48 89 ca             	mov    rdx,rcx
  38:	48 c1 e2 04          	shl    rdx,0x4
  3c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
  40:	66 41 0f 10 04 02    	movupd xmm0,XMMWORD PTR [r10+rax*1]
  46:	66 41 0f 10 0c 03    	movupd xmm1,XMMWORD PTR [r11+rax*1]
  4c:	66 0f 59 c1          	mulpd  xmm0,xmm1
  50:	41 0f 11 04 00       	movups XMMWORD PTR [r8+rax*1],xmm0
  55:	48 83 c0 10          	add    rax,0x10
  59:	48 39 c2             	cmp    rdx,rax
  5c:	75 e2                	jne    40 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x40>
  5e:	48 8d 04 09          	lea    rax,[rcx+rcx*1]
  62:	49 39 c1             	cmp    r9,rax
  65:	74 16                	je     7d <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x7d>
  67:	48 c1 e1 04          	shl    rcx,0x4
  6b:	f2 41 0f 10 04 0a    	movsd  xmm0,QWORD PTR [r10+rcx*1]
  71:	f2 41 0f 59 04 0b    	mulsd  xmm0,QWORD PTR [r11+rcx*1]
  77:	f2 41 0f 11 04 08    	movsd  QWORD PTR [r8+rcx*1],xmm0
  7d:	c3                   	ret
  7e:	66 90                	xchg   ax,ax
  80:	31 c0                	xor    eax,eax
  82:	0f 1f 84 00 00 00 00 	nop    DWORD PTR [rax+rax*1+0x0]
  89:	00 
  8a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  91:	00 00 00 00 
  95:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  9c:	00 00 00 00 
  a0:	f2 41 0f 10 04 c2    	movsd  xmm0,QWORD PTR [r10+rax*8]
  a6:	f2 41 0f 59 04 c3    	mulsd  xmm0,QWORD PTR [r11+rax*8]
  ac:	f2 41 0f 11 04 c0    	movsd  QWORD PTR [r8+rax*8],xmm0
  b2:	48 83 c0 01          	add    rax,0x1
  b6:	49 39 c1             	cmp    r9,rax
  b9:	75 e5                	jne    a0 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xa0>
  bb:	c3                   	ret
  bc:	90                   	nop
  bd:	90                   	nop
  be:	90                   	nop
  bf:	90                   	nop

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIfEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4c 8b 5c 24 40       	mov    r11,QWORD PTR [rsp+0x40]
   6:	4c 8b 54 24 30       	mov    r10,QWORD PTR [rsp+0x30]
   b:	4d 85 db             	test   r11,r11
   e:	0f 84 d0 00 00 00    	je     e4 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xe4>
  14:	48 83 7c 24 38 01    	cmp    QWORD PTR [rsp+0x38],0x1
  1a:	0f 95 c0             	setne  al
  1d:	49 83 f9 01          	cmp    r9,0x1
  21:	0f 95 c3             	setne  bl
  24:	08 d8                	or     al,bl
  26:	0f 85 c4 00 00 00    	jne    f0 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xf0>
  2c:	48 83 fa 01          	cmp    rdx,0x1
  30:	0f 85 ba 00 00 00    	jne    f0 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xf0>
  36:	49 83 fb 01          	cmp    r11,0x1
  3a:	0f 84 08 01 00 00    	je     148 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x148>
  40:	49 8d 42 fc          	lea    rax,[r10-0x4]
  44:	48 89 c2             	mov    rdx,rax
  47:	48 29 ca             	sub    rdx,rcx
  4a:	48 83 fa 08          	cmp    rdx,0x8
  4e:	0f 86 f4 00 00 00    	jbe    148 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x148>
  54:	4c 29 c0             	sub    rax,r8
  57:	48 83 f8 08          	cmp    rax,0x8
  5b:	0f 86 e7 00 00 00    	jbe    148 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x148>
  61:	49 8d 43 ff          	lea    rax,[r11-0x1]
  65:	48 83 f8 02          	cmp    rax,0x2
  69:	0f 86 0d 01 00 00    	jbe    17c <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x17c>
  6f:	4c 89 da             	mov    rdx,r11
  72:	31 c0                	xor    eax,eax
  74:	48 c1 ea 02          	shr    rdx,0x2
  78:	49 89 d1             	mov    r9,rdx
  7b:	49 c1 e1 04          	shl    r9,0x4
  7f:	90                   	nop
  80:	0f 10 04 01          	movups xmm0,XMMWORD PTR [rcx+rax*1]
  84:	41 0f 10 14 00       	movups xmm2,XMMWORD PTR [r8+rax*1]
  89:	0f 59 c2             	mulps  xmm0,xmm2
  8c:	41 0f 11 04 02       	movups XMMWORD PTR [r10+rax*1],xmm0
  91:	48 83 c0 10          	add    rax,0x10
  95:	4c 39 c8             	cmp    rax,r9
  98:	75 e6                	jne    80 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x80>
  9a:	48 8d 04 95 00 00 00 	lea    rax,[rdx*4+0x0]
  a1:	00 
  a2:	49 39 c3             	cmp    r11,rax
  a5:	74 3d                	je     e4 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xe4>
  a7:	49 29 c3             	sub    r11,rax
  aa:	49 83 fb 01          	cmp    r11,0x1
  ae:	74 23                	je     d3 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xd3>
  b0:	f3 41 0f 7e 0c 80    	movq   xmm1,QWORD PTR [r8+rax*4]
  b6:	f3 0f 7e 04 81       	movq   xmm0,QWORD PTR [rcx+rax*4]
  bb:	4c 89 da             	mov    rdx,r11
  be:	48 83 e2 fe          	and    rdx,0xfffffffffffffffe
  c2:	41 83 e3 01          	and    r11d,0x1
  c6:	0f 59 c1             	mulps  xmm0,xmm1
  c9:	41 0f 13 04 82       	movlps QWORD PTR [r10+rax*4],xmm0
  ce:	74 14                	je     e4 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xe4>
  d0:	48 01 d0             	add    rax,rdx
  d3:	f3 0f 10 04 81       	movss  xmm0,DWORD PTR [rcx+rax*4]
  d8:	f3 41 0f 59 04 80    	mulss  xmm0,DWORD PTR [r8+rax*4]
  de:	f3 41 0f 11 04 82    	movss  DWORD PTR [r10+rax*4],xmm0
  e4:	5b                   	pop    rbx
  e5:	c3                   	ret
  e6:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  ed:	00 00 00 
  f0:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
  f5:	48 c1 e2 02          	shl    rdx,0x2
  f9:	49 c1 e1 02          	shl    r9,0x2
  fd:	48 8d 1c 85 00 00 00 	lea    rbx,[rax*4+0x0]
 104:	00 
 105:	31 c0                	xor    eax,eax
 107:	0f 1f 00             	nop    DWORD PTR [rax]
 10a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 111:	00 00 00 00 
 115:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 11c:	00 00 00 00 
 120:	f3 0f 10 01          	movss  xmm0,DWORD PTR [rcx]
 124:	f3 41 0f 59 00       	mulss  xmm0,DWORD PTR [r8]
 129:	48 83 c0 01          	add    rax,0x1
 12d:	48 01 d1             	add    rcx,rdx
 130:	4d 01 c8             	add    r8,r9
 133:	f3 41 0f 11 02       	movss  DWORD PTR [r10],xmm0
 138:	49 01 da             	add    r10,rbx
 13b:	49 39 c3             	cmp    r11,rax
 13e:	75 e0                	jne    120 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x120>
 140:	5b                   	pop    rbx
 141:	c3                   	ret
 142:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
 148:	31 c0                	xor    eax,eax
 14a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 151:	00 00 00 00 
 155:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 15c:	00 00 00 00 
 160:	f3 0f 10 04 81       	movss  xmm0,DWORD PTR [rcx+rax*4]
 165:	f3 41 0f 59 04 80    	mulss  xmm0,DWORD PTR [r8+rax*4]
 16b:	f3 41 0f 11 04 82    	movss  DWORD PTR [r10+rax*4],xmm0
 171:	48 83 c0 01          	add    rax,0x1
 175:	49 39 c3             	cmp    r11,rax
 178:	75 e6                	jne    160 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x160>
 17a:	5b                   	pop    rbx
 17b:	c3                   	ret
 17c:	31 c0                	xor    eax,eax
 17e:	e9 2d ff ff ff       	jmp    b0 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xb0>
 183:	90                   	nop
 184:	90                   	nop
 185:	90                   	nop
 186:	90                   	nop
 187:	90                   	nop
 188:	90                   	nop
 189:	90                   	nop
 18a:	90                   	nop
 18b:	90                   	nop
 18c:	90                   	nop
 18d:	90                   	nop
 18e:	90                   	nop
 18f:	90                   	nop
 190:	90                   	nop
 191:	90                   	nop
 192:	90                   	nop
 193:	90                   	nop
 194:	90                   	nop
 195:	90                   	nop
 196:	90                   	nop
 197:	90                   	nop
 198:	90                   	nop
 199:	90                   	nop
 19a:	90                   	nop
 19b:	90                   	nop
 19c:	90                   	nop
 19d:	90                   	nop
 19e:	90                   	nop
 19f:	90                   	nop

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIdEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4c 8b 5c 24 40       	mov    r11,QWORD PTR [rsp+0x40]
   6:	4c 8b 54 24 30       	mov    r10,QWORD PTR [rsp+0x30]
   b:	4d 85 db             	test   r11,r11
   e:	0f 84 a8 00 00 00    	je     bc <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xbc>
  14:	48 83 7c 24 38 01    	cmp    QWORD PTR [rsp+0x38],0x1
  1a:	0f 95 c0             	setne  al
  1d:	49 83 f9 01          	cmp    r9,0x1
  21:	0f 95 c3             	setne  bl
  24:	08 d8                	or     al,bl
  26:	0f 85 94 00 00 00    	jne    c0 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xc0>
  2c:	48 83 fa 01          	cmp    rdx,0x1
  30:	0f 85 8a 00 00 00    	jne    c0 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xc0>
  36:	49 8d 43 ff          	lea    rax,[r11-0x1]
  3a:	48 83 f8 01          	cmp    rax,0x1
  3e:	0f 86 c4 00 00 00    	jbe    108 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x108>
  44:	4c 89 d0             	mov    rax,r10
  47:	48 29 c8             	sub    rax,rcx
  4a:	48 83 f8 08          	cmp    rax,0x8
  4e:	0f 84 b4 00 00 00    	je     108 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x108>
  54:	4c 89 d0             	mov    rax,r10
  57:	4c 29 c0             	sub    rax,r8
  5a:	48 83 f8 08          	cmp    rax,0x8
  5e:	0f 84 a4 00 00 00    	je     108 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x108>
  64:	4d 89 d9             	mov    r9,r11
  67:	31 c0                	xor    eax,eax
  69:	49 d1 e9             	shr    r9,1
  6c:	4c 89 ca             	mov    rdx,r9
  6f:	48 c1 e2 04          	shl    rdx,0x4
  73:	66 90                	xchg   ax,ax
  75:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  7c:	00 00 00 00 
  80:	66 0f 10 04 01       	movupd xmm0,XMMWORD PTR [rcx+rax*1]
  85:	66 41 0f 10 0c 00    	movupd xmm1,XMMWORD PTR [r8+rax*1]
  8b:	66 0f 59 c1          	mulpd  xmm0,xmm1
  8f:	41 0f 11 04 02       	movups XMMWORD PTR [r10+rax*1],xmm0
  94:	48 83 c0 10          	add    rax,0x10
  98:	48 39 d0             	cmp    rax,rdx
  9b:	75 e3                	jne    80 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x80>
  9d:	4b 8d 04 09          	lea    rax,[r9+r9*1]
  a1:	49 39 c3             	cmp    r11,rax
  a4:	74 16                	je     bc <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xbc>
  a6:	49 c1 e1 04          	shl    r9,0x4
  aa:	f2 42 0f 10 04 09    	movsd  xmm0,QWORD PTR [rcx+r9*1]
  b0:	f2 43 0f 59 04 08    	mulsd  xmm0,QWORD PTR [r8+r9*1]
  b6:	f2 43 0f 11 04 0a    	movsd  QWORD PTR [r10+r9*1],xmm0
  bc:	5b                   	pop    rbx
  bd:	c3                   	ret
  be:	66 90                	xchg   ax,ax
  c0:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
  c5:	48 c1 e2 03          	shl    rdx,0x3
  c9:	49 c1 e1 03          	shl    r9,0x3
  cd:	48 8d 1c c5 00 00 00 	lea    rbx,[rax*8+0x0]
  d4:	00 
  d5:	31 c0                	xor    eax,eax
  d7:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  de:	00 00 
  e0:	f2 0f 10 01          	movsd  xmm0,QWORD PTR [rcx]
  e4:	f2 41 0f 59 00       	mulsd  xmm0,QWORD PTR [r8]
  e9:	48 83 c0 01          	add    rax,0x1
  ed:	48 01 d1             	add    rcx,rdx
  f0:	4d 01 c8             	add    r8,r9
  f3:	f2 41 0f 11 02       	movsd  QWORD PTR [r10],xmm0
  f8:	49 01 da             	add    r10,rbx
  fb:	49 39 c3             	cmp    r11,rax
  fe:	75 e0                	jne    e0 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xe0>
 100:	5b                   	pop    rbx
 101:	c3                   	ret
 102:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
 108:	31 c0                	xor    eax,eax
 10a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 111:	00 00 00 00 
 115:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 11c:	00 00 00 00 
 120:	f2 0f 10 04 c1       	movsd  xmm0,QWORD PTR [rcx+rax*8]
 125:	f2 41 0f 59 04 c0    	mulsd  xmm0,QWORD PTR [r8+rax*8]
 12b:	f2 41 0f 11 04 c2    	movsd  QWORD PTR [r10+rax*8],xmm0
 131:	48 83 c0 01          	add    rax,0x1
 135:	49 39 c3             	cmp    r11,rax
 138:	75 e6                	jne    120 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x120>
 13a:	5b                   	pop    rbx
 13b:	c3                   	ret
 13c:	90                   	nop
 13d:	90                   	nop
 13e:	90                   	nop
 13f:	90                   	nop

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIfEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)>:
   0:	48 83 ec 58          	sub    rsp,0x58
   4:	0f 11 34 24          	movups XMMWORD PTR [rsp],xmm6
   8:	0f 11 7c 24 10       	movups XMMWORD PTR [rsp+0x10],xmm7
   d:	44 0f 11 44 24 20    	movups XMMWORD PTR [rsp+0x20],xmm8
  13:	44 0f 11 4c 24 30    	movups XMMWORD PTR [rsp+0x30],xmm9
  19:	44 0f 11 54 24 40    	movups XMMWORD PTR [rsp+0x40],xmm10
  1f:	48 8b 94 24 88 00 00 	mov    rdx,QWORD PTR [rsp+0x88]
  26:	00 
  27:	4c 8b 94 24 80 00 00 	mov    r10,QWORD PTR [rsp+0x80]
  2e:	00 
  2f:	0f 28 f8             	movaps xmm7,xmm0
  32:	0f 28 f1             	movaps xmm6,xmm1
  35:	44 0f 28 c2          	movaps xmm8,xmm2
  39:	0f c6 d2 00          	shufps xmm2,xmm2,0x0
  3d:	0f c6 ff 00          	shufps xmm7,xmm7,0x0
  41:	0f c6 f6 00          	shufps xmm6,xmm6,0x0
  45:	0f 28 e0             	movaps xmm4,xmm0
  48:	44 0f 28 cf          	movaps xmm9,xmm7
  4c:	44 0f 28 d6          	movaps xmm10,xmm6
  50:	48 85 d2             	test   rdx,rdx
  53:	0f 84 77 01 00 00    	je     1d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1d0>
  59:	f3 41 0f 10 01       	movss  xmm0,DWORD PTR [r9]
  5e:	f3 41 0f 11 02       	movss  DWORD PTR [r10],xmm0
  63:	48 83 fa 01          	cmp    rdx,0x1
  67:	0f 84 63 01 00 00    	je     1d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1d0>
  6d:	48 8d 42 ff          	lea    rax,[rdx-0x1]
  71:	f3 41 0f 10 04 81    	movss  xmm0,DWORD PTR [r9+rax*4]
  77:	f3 41 0f 11 04 82    	movss  DWORD PTR [r10+rax*4],xmm0
  7d:	48 83 fa 02          	cmp    rdx,0x2
  81:	0f 84 49 01 00 00    	je     1d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1d0>
  87:	48 83 fa 03          	cmp    rdx,0x3
  8b:	0f 84 5f 01 00 00    	je     1f0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1f0>
  91:	4c 89 d1             	mov    rcx,r10
  94:	4c 29 c9             	sub    rcx,r9
  97:	48 83 f9 10          	cmp    rcx,0x10
  9b:	0f 86 4f 01 00 00    	jbe    1f0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1f0>
  a1:	48 8d 42 fd          	lea    rax,[rdx-0x3]
  a5:	48 83 f8 02          	cmp    rax,0x2
  a9:	0f 86 8c 01 00 00    	jbe    23b <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x23b>
  af:	4c 8d 5a fe          	lea    r11,[rdx-0x2]
  b3:	0f 28 ea             	movaps xmm5,xmm2
  b6:	31 c0                	xor    eax,eax
  b8:	4c 89 d9             	mov    rcx,r11
  bb:	48 c1 e9 02          	shr    rcx,0x2
  bf:	49 89 c8             	mov    r8,rcx
  c2:	49 c1 e0 04          	shl    r8,0x4
  c6:	0f 1f 00             	nop    DWORD PTR [rax]
  c9:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  d0:	00 00 00 00 
  d4:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  db:	00 00 00 00 
  df:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  e6:	00 00 00 00 
  ea:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  f1:	00 00 00 00 
  f5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  fc:	00 00 00 00 
 100:	41 0f 10 04 01       	movups xmm0,XMMWORD PTR [r9+rax*1]
 105:	41 0f 10 5c 01 04    	movups xmm3,XMMWORD PTR [r9+rax*1+0x4]
 10b:	0f 59 c7             	mulps  xmm0,xmm7
 10e:	0f 59 de             	mulps  xmm3,xmm6
 111:	0f 58 c3             	addps  xmm0,xmm3
 114:	41 0f 10 5c 01 08    	movups xmm3,XMMWORD PTR [r9+rax*1+0x8]
 11a:	0f 59 dd             	mulps  xmm3,xmm5
 11d:	0f 58 c3             	addps  xmm0,xmm3
 120:	41 0f 11 44 02 04    	movups XMMWORD PTR [r10+rax*1+0x4],xmm0
 126:	48 83 c0 10          	add    rax,0x10
 12a:	49 39 c0             	cmp    r8,rax
 12d:	75 d1                	jne    100 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x100>
 12f:	48 8d 04 8d 00 00 00 	lea    rax,[rcx*4+0x0]
 136:	00 
 137:	49 39 c3             	cmp    r11,rax
 13a:	0f 84 90 00 00 00    	je     1d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1d0>
 140:	48 29 c2             	sub    rdx,rax
 143:	48 8d 48 01          	lea    rcx,[rax+0x1]
 147:	4c 8d 40 02          	lea    r8,[rax+0x2]
 14b:	48 83 fa 03          	cmp    rdx,0x3
 14f:	74 5d                	je     1ae <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1ae>
 151:	48 83 ea 02          	sub    rdx,0x2
 155:	f3 41 0f 7e 04 81    	movq   xmm0,QWORD PTR [r9+rax*4]
 15b:	f3 41 0f 7e d9       	movq   xmm3,xmm9
 160:	f3 41 0f 7e ea       	movq   xmm5,xmm10
 165:	0f 59 c3             	mulps  xmm0,xmm3
 168:	f3 41 0f 7e 5c 81 04 	movq   xmm3,QWORD PTR [r9+rax*4+0x4]
 16f:	0f 59 dd             	mulps  xmm3,xmm5
 172:	f3 0f 7e c0          	movq   xmm0,xmm0
 176:	f3 0f 7e db          	movq   xmm3,xmm3
 17a:	0f 58 c3             	addps  xmm0,xmm3
 17d:	f3 0f 7e da          	movq   xmm3,xmm2
 181:	f3 41 0f 7e 54 81 08 	movq   xmm2,QWORD PTR [r9+rax*4+0x8]
 188:	0f 59 d3             	mulps  xmm2,xmm3
 18b:	f3 0f 7e c0          	movq   xmm0,xmm0
 18f:	f3 0f 7e d2          	movq   xmm2,xmm2
 193:	0f 58 c2             	addps  xmm0,xmm2
 196:	41 0f 13 44 82 04    	movlps QWORD PTR [r10+rax*4+0x4],xmm0
 19c:	48 89 d0             	mov    rax,rdx
 19f:	48 83 e0 fe          	and    rax,0xfffffffffffffffe
 1a3:	83 e2 01             	and    edx,0x1
 1a6:	74 28                	je     1d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1d0>
 1a8:	48 01 c1             	add    rcx,rax
 1ab:	49 01 c0             	add    r8,rax
 1ae:	f3 41 0f 59 64 89 fc 	mulss  xmm4,DWORD PTR [r9+rcx*4-0x4]
 1b5:	f3 41 0f 59 0c 89    	mulss  xmm1,DWORD PTR [r9+rcx*4]
 1bb:	f3 47 0f 59 04 81    	mulss  xmm8,DWORD PTR [r9+r8*4]
 1c1:	f3 0f 58 e1          	addss  xmm4,xmm1
 1c5:	f3 41 0f 58 e0       	addss  xmm4,xmm8
 1ca:	f3 41 0f 11 24 8a    	movss  DWORD PTR [r10+rcx*4],xmm4
 1d0:	0f 10 34 24          	movups xmm6,XMMWORD PTR [rsp]
 1d4:	0f 10 7c 24 10       	movups xmm7,XMMWORD PTR [rsp+0x10]
 1d9:	44 0f 10 44 24 20    	movups xmm8,XMMWORD PTR [rsp+0x20]
 1df:	44 0f 10 4c 24 30    	movups xmm9,XMMWORD PTR [rsp+0x30]
 1e5:	44 0f 10 54 24 40    	movups xmm10,XMMWORD PTR [rsp+0x40]
 1eb:	48 83 c4 58          	add    rsp,0x58
 1ef:	c3                   	ret
 1f0:	48 8d 14 85 fc ff ff 	lea    rdx,[rax*4-0x4]
 1f7:	ff 
 1f8:	31 c0                	xor    eax,eax
 1fa:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
 200:	f3 41 0f 10 44 01 04 	movss  xmm0,DWORD PTR [r9+rax*1+0x4]
 207:	f3 41 0f 10 14 01    	movss  xmm2,DWORD PTR [r9+rax*1]
 20d:	f3 0f 59 c1          	mulss  xmm0,xmm1
 211:	f3 0f 59 d4          	mulss  xmm2,xmm4
 215:	f3 0f 58 c2          	addss  xmm0,xmm2
 219:	f3 41 0f 10 54 01 08 	movss  xmm2,DWORD PTR [r9+rax*1+0x8]
 220:	f3 41 0f 59 d0       	mulss  xmm2,xmm8
 225:	f3 0f 58 c2          	addss  xmm0,xmm2
 229:	f3 41 0f 11 44 02 04 	movss  DWORD PTR [r10+rax*1+0x4],xmm0
 230:	48 83 c0 04          	add    rax,0x4
 234:	48 39 d0             	cmp    rax,rdx
 237:	75 c7                	jne    200 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x200>
 239:	eb 95                	jmp    1d0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1d0>
 23b:	48 83 ea 02          	sub    rdx,0x2
 23f:	31 c0                	xor    eax,eax
 241:	41 b8 02 00 00 00    	mov    r8d,0x2
 247:	b9 01 00 00 00       	mov    ecx,0x1
 24c:	e9 04 ff ff ff       	jmp    155 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x155>
 251:	90                   	nop
 252:	90                   	nop
 253:	90                   	nop
 254:	90                   	nop
 255:	90                   	nop
 256:	90                   	nop
 257:	90                   	nop
 258:	90                   	nop
 259:	90                   	nop
 25a:	90                   	nop
 25b:	90                   	nop
 25c:	90                   	nop
 25d:	90                   	nop
 25e:	90                   	nop
 25f:	90                   	nop
 260:	90                   	nop
 261:	90                   	nop
 262:	90                   	nop
 263:	90                   	nop
 264:	90                   	nop
 265:	90                   	nop
 266:	90                   	nop
 267:	90                   	nop
 268:	90                   	nop
 269:	90                   	nop
 26a:	90                   	nop
 26b:	90                   	nop
 26c:	90                   	nop
 26d:	90                   	nop
 26e:	90                   	nop
 26f:	90                   	nop
 270:	90                   	nop
 271:	90                   	nop
 272:	90                   	nop
 273:	90                   	nop
 274:	90                   	nop
 275:	90                   	nop
 276:	90                   	nop
 277:	90                   	nop
 278:	90                   	nop
 279:	90                   	nop
 27a:	90                   	nop
 27b:	90                   	nop
 27c:	90                   	nop
 27d:	90                   	nop
 27e:	90                   	nop
 27f:	90                   	nop

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIdEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)>:
   0:	48 83 ec 28          	sub    rsp,0x28
   4:	0f 11 34 24          	movups XMMWORD PTR [rsp],xmm6
   8:	0f 11 7c 24 10       	movups XMMWORD PTR [rsp+0x10],xmm7
   d:	48 8b 44 24 58       	mov    rax,QWORD PTR [rsp+0x58]
  12:	48 8b 54 24 50       	mov    rdx,QWORD PTR [rsp+0x50]
  17:	66 0f 28 e0          	movapd xmm4,xmm0
  1b:	48 85 c0             	test   rax,rax
  1e:	0f 84 fe 00 00 00    	je     122 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x122>
  24:	f2 41 0f 10 01       	movsd  xmm0,QWORD PTR [r9]
  29:	f2 0f 11 02          	movsd  QWORD PTR [rdx],xmm0
  2d:	48 83 f8 01          	cmp    rax,0x1
  31:	0f 84 eb 00 00 00    	je     122 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x122>
  37:	48 8d 48 ff          	lea    rcx,[rax-0x1]
  3b:	f2 41 0f 10 04 c9    	movsd  xmm0,QWORD PTR [r9+rcx*8]
  41:	f2 0f 11 04 ca       	movsd  QWORD PTR [rdx+rcx*8],xmm0
  46:	48 83 f8 02          	cmp    rax,0x2
  4a:	0f 84 d2 00 00 00    	je     122 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x122>
  50:	48 83 f8 03          	cmp    rax,0x3
  54:	0f 84 d6 00 00 00    	je     130 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x130>
  5a:	49 89 d0             	mov    r8,rdx
  5d:	4d 29 c8             	sub    r8,r9
  60:	49 83 f8 10          	cmp    r8,0x10
  64:	0f 86 c6 00 00 00    	jbe    130 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x130>
  6a:	48 8d 48 fe          	lea    rcx,[rax-0x2]
  6e:	f2 0f 12 fc          	movddup xmm7,xmm4
  72:	f2 0f 12 f1          	movddup xmm6,xmm1
  76:	31 c0                	xor    eax,eax
  78:	49 89 ca             	mov    r10,rcx
  7b:	f2 0f 12 ea          	movddup xmm5,xmm2
  7f:	49 d1 ea             	shr    r10,1
  82:	4d 89 d0             	mov    r8,r10
  85:	49 c1 e0 04          	shl    r8,0x4
  89:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  90:	00 00 00 00 
  94:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  9b:	00 00 00 00 
  9f:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  a6:	00 00 00 00 
  aa:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  b1:	00 00 00 00 
  b5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  bc:	00 00 00 00 
  c0:	66 41 0f 10 04 01    	movupd xmm0,XMMWORD PTR [r9+rax*1]
  c6:	66 41 0f 10 5c 01 08 	movupd xmm3,XMMWORD PTR [r9+rax*1+0x8]
  cd:	66 0f 59 c7          	mulpd  xmm0,xmm7
  d1:	66 0f 59 de          	mulpd  xmm3,xmm6
  d5:	66 0f 58 c3          	addpd  xmm0,xmm3
  d9:	66 41 0f 10 5c 01 10 	movupd xmm3,XMMWORD PTR [r9+rax*1+0x10]
  e0:	66 0f 59 dd          	mulpd  xmm3,xmm5
  e4:	66 0f 58 c3          	addpd  xmm0,xmm3
  e8:	0f 11 44 02 08       	movups XMMWORD PTR [rdx+rax*1+0x8],xmm0
  ed:	48 83 c0 10          	add    rax,0x10
  f1:	4c 39 c0             	cmp    rax,r8
  f4:	75 ca                	jne    c0 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0xc0>
  f6:	4f 8d 04 12          	lea    r8,[r10+r10*1]
  fa:	4c 39 c1             	cmp    rcx,r8
  fd:	74 23                	je     122 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x122>
  ff:	f2 41 0f 59 24 01    	mulsd  xmm4,QWORD PTR [r9+rax*1]
 105:	f2 43 0f 59 4c c1 08 	mulsd  xmm1,QWORD PTR [r9+r8*8+0x8]
 10c:	f2 41 0f 59 54 01 10 	mulsd  xmm2,QWORD PTR [r9+rax*1+0x10]
 113:	f2 0f 58 e1          	addsd  xmm4,xmm1
 117:	f2 0f 58 e2          	addsd  xmm4,xmm2
 11b:	f2 42 0f 11 64 c2 08 	movsd  QWORD PTR [rdx+r8*8+0x8],xmm4
 122:	0f 10 34 24          	movups xmm6,XMMWORD PTR [rsp]
 126:	0f 10 7c 24 10       	movups xmm7,XMMWORD PTR [rsp+0x10]
 12b:	48 83 c4 28          	add    rsp,0x28
 12f:	c3                   	ret
 130:	48 8d 0c cd f8 ff ff 	lea    rcx,[rcx*8-0x8]
 137:	ff 
 138:	31 c0                	xor    eax,eax
 13a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
 140:	f2 41 0f 10 44 01 08 	movsd  xmm0,QWORD PTR [r9+rax*1+0x8]
 147:	f2 41 0f 10 1c 01    	movsd  xmm3,QWORD PTR [r9+rax*1]
 14d:	f2 0f 59 c1          	mulsd  xmm0,xmm1
 151:	f2 0f 59 dc          	mulsd  xmm3,xmm4
 155:	f2 0f 58 c3          	addsd  xmm0,xmm3
 159:	f2 41 0f 10 5c 01 10 	movsd  xmm3,QWORD PTR [r9+rax*1+0x10]
 160:	f2 0f 59 da          	mulsd  xmm3,xmm2
 164:	f2 0f 58 c3          	addsd  xmm0,xmm3
 168:	f2 0f 11 44 02 08    	movsd  QWORD PTR [rdx+rax*1+0x8],xmm0
 16e:	48 83 c0 08          	add    rax,0x8
 172:	48 39 c1             	cmp    rcx,rax
 175:	75 c9                	jne    140 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x140>
 177:	eb a9                	jmp    122 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x122>
 179:	90                   	nop
 17a:	90                   	nop
 17b:	90                   	nop
 17c:	90                   	nop
 17d:	90                   	nop
 17e:	90                   	nop
 17f:	90                   	nop
