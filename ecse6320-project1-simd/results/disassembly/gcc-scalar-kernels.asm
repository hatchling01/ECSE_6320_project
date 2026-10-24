; Targeted disassembly: gcc-scalar
; Object file: 
C:\Users\CHOUDN3\Downloads\EcSE_4320\ecse6320-project1-simd\build-gcc-scalar\CMakeFiles\project_kernels.dir\src\kernels.cpp.obj
; GNU objdump -d -C -Mintel; project_kernels symbols only.

0000000000000000 <void project::axpy<float>(float, float const*, float*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	74 39                	je     3e <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x3e>
   5:	31 c0                	xor    eax,eax
   7:	0f 1f 00             	nop    DWORD PTR [rax]
   a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  11:	00 00 00 00 
  15:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  1c:	00 00 00 00 
  20:	f3 0f 10 0c 82       	movss  xmm1,DWORD PTR [rdx+rax*4]
  25:	f3 0f 59 c8          	mulss  xmm1,xmm0
  29:	f3 41 0f 58 0c 80    	addss  xmm1,DWORD PTR [r8+rax*4]
  2f:	f3 41 0f 11 0c 80    	movss  DWORD PTR [r8+rax*4],xmm1
  35:	48 83 c0 01          	add    rax,0x1
  39:	49 39 c1             	cmp    r9,rax
  3c:	75 e2                	jne    20 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x20>
  3e:	c3                   	ret
  3f:	90                   	nop

Disassembly of section .text$_ZN7project4axpyIdEEvT_PKS1_PS1_y:


0000000000000000 <void project::axpy<double>(double, double const*, double*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	74 39                	je     3e <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x3e>
   5:	31 c0                	xor    eax,eax
   7:	0f 1f 00             	nop    DWORD PTR [rax]
   a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  11:	00 00 00 00 
  15:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  1c:	00 00 00 00 
  20:	f2 0f 10 0c c2       	movsd  xmm1,QWORD PTR [rdx+rax*8]
  25:	f2 0f 59 c8          	mulsd  xmm1,xmm0
  29:	f2 41 0f 58 0c c0    	addsd  xmm1,QWORD PTR [r8+rax*8]
  2f:	f2 41 0f 11 0c c0    	movsd  QWORD PTR [r8+rax*8],xmm1
  35:	48 83 c0 01          	add    rax,0x1
  39:	49 39 c1             	cmp    r9,rax
  3c:	75 e2                	jne    20 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x20>
  3e:	c3                   	ret
  3f:	90                   	nop

Disassembly of section .text$_ZN7project11dot_productIfEET_PKS1_S3_y:


0000000000000000 <float project::dot_product<float>(float const*, float const*, unsigned long long)>:
   0:	66 0f ef c9          	pxor   xmm1,xmm1
   4:	4d 85 c0             	test   r8,r8
   7:	74 2e                	je     37 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x37>
   9:	31 c0                	xor    eax,eax
   b:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  12:	00 00 00 
  15:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  1c:	00 00 00 00 
  20:	f3 0f 10 04 81       	movss  xmm0,DWORD PTR [rcx+rax*4]
  25:	f3 0f 59 04 82       	mulss  xmm0,DWORD PTR [rdx+rax*4]
  2a:	48 83 c0 01          	add    rax,0x1
  2e:	f3 0f 58 c8          	addss  xmm1,xmm0
  32:	49 39 c0             	cmp    r8,rax
  35:	75 e9                	jne    20 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x20>
  37:	0f 28 c1             	movaps xmm0,xmm1
  3a:	c3                   	ret
  3b:	90                   	nop
  3c:	90                   	nop
  3d:	90                   	nop
  3e:	90                   	nop
  3f:	90                   	nop

Disassembly of section .text$_ZN7project11dot_productIdEET_PKS1_S3_y:


0000000000000000 <double project::dot_product<double>(double const*, double const*, unsigned long long)>:
   0:	66 0f ef c9          	pxor   xmm1,xmm1
   4:	4d 85 c0             	test   r8,r8
   7:	74 2e                	je     37 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x37>
   9:	31 c0                	xor    eax,eax
   b:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  12:	00 00 00 
  15:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  1c:	00 00 00 00 
  20:	f2 0f 10 04 c1       	movsd  xmm0,QWORD PTR [rcx+rax*8]
  25:	f2 0f 59 04 c2       	mulsd  xmm0,QWORD PTR [rdx+rax*8]
  2a:	48 83 c0 01          	add    rax,0x1
  2e:	f2 0f 58 c8          	addsd  xmm1,xmm0
  32:	49 39 c0             	cmp    r8,rax
  35:	75 e9                	jne    20 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x20>
  37:	66 0f 28 c1          	movapd xmm0,xmm1
  3b:	c3                   	ret
  3c:	90                   	nop
  3d:	90                   	nop
  3e:	90                   	nop
  3f:	90                   	nop

Disassembly of section .text$_ZN7project20elementwise_multiplyIfEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	74 34                	je     39 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x39>
   5:	31 c0                	xor    eax,eax
   7:	0f 1f 00             	nop    DWORD PTR [rax]
   a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  11:	00 00 00 00 
  15:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  1c:	00 00 00 00 
  20:	f3 0f 10 04 81       	movss  xmm0,DWORD PTR [rcx+rax*4]
  25:	f3 0f 59 04 82       	mulss  xmm0,DWORD PTR [rdx+rax*4]
  2a:	f3 41 0f 11 04 80    	movss  DWORD PTR [r8+rax*4],xmm0
  30:	48 83 c0 01          	add    rax,0x1
  34:	49 39 c1             	cmp    r9,rax
  37:	75 e7                	jne    20 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x20>
  39:	c3                   	ret
  3a:	90                   	nop
  3b:	90                   	nop
  3c:	90                   	nop
  3d:	90                   	nop
  3e:	90                   	nop
  3f:	90                   	nop

Disassembly of section .text$_ZN7project20elementwise_multiplyIdEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	74 34                	je     39 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x39>
   5:	31 c0                	xor    eax,eax
   7:	0f 1f 00             	nop    DWORD PTR [rax]
   a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  11:	00 00 00 00 
  15:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  1c:	00 00 00 00 
  20:	f2 0f 10 04 c1       	movsd  xmm0,QWORD PTR [rcx+rax*8]
  25:	f2 0f 59 04 c2       	mulsd  xmm0,QWORD PTR [rdx+rax*8]
  2a:	f2 41 0f 11 04 c0    	movsd  QWORD PTR [r8+rax*8],xmm0
  30:	48 83 c0 01          	add    rax,0x1
  34:	49 39 c1             	cmp    r9,rax
  37:	75 e7                	jne    20 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x20>
  39:	c3                   	ret
  3a:	90                   	nop
  3b:	90                   	nop
  3c:	90                   	nop
  3d:	90                   	nop
  3e:	90                   	nop
  3f:	90                   	nop

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIfEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4c 8b 5c 24 40       	mov    r11,QWORD PTR [rsp+0x40]
   6:	49 89 ca             	mov    r10,rcx
   9:	48 8b 4c 24 30       	mov    rcx,QWORD PTR [rsp+0x30]
   e:	4d 85 db             	test   r11,r11
  11:	74 47                	je     5a <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x5a>
  13:	48 83 7c 24 38 01    	cmp    QWORD PTR [rsp+0x38],0x1
  19:	0f 95 c0             	setne  al
  1c:	49 83 f9 01          	cmp    r9,0x1
  20:	0f 95 c3             	setne  bl
  23:	08 d8                	or     al,bl
  25:	75 39                	jne    60 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x60>
  27:	31 c0                	xor    eax,eax
  29:	48 83 fa 01          	cmp    rdx,0x1
  2d:	75 31                	jne    60 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x60>
  2f:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  35:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  3c:	00 00 00 00 
  40:	f3 41 0f 10 04 80    	movss  xmm0,DWORD PTR [r8+rax*4]
  46:	f3 41 0f 59 04 82    	mulss  xmm0,DWORD PTR [r10+rax*4]
  4c:	f3 0f 11 04 81       	movss  DWORD PTR [rcx+rax*4],xmm0
  51:	48 83 c0 01          	add    rax,0x1
  55:	49 39 c3             	cmp    r11,rax
  58:	75 e6                	jne    40 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x40>
  5a:	5b                   	pop    rbx
  5b:	c3                   	ret
  5c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
  60:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
  65:	48 c1 e2 02          	shl    rdx,0x2
  69:	49 c1 e1 02          	shl    r9,0x2
  6d:	48 8d 1c 85 00 00 00 	lea    rbx,[rax*4+0x0]
  74:	00 
  75:	31 c0                	xor    eax,eax
  77:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  7e:	00 00 
  80:	f3 41 0f 10 02       	movss  xmm0,DWORD PTR [r10]
  85:	f3 41 0f 59 00       	mulss  xmm0,DWORD PTR [r8]
  8a:	48 83 c0 01          	add    rax,0x1
  8e:	49 01 d2             	add    r10,rdx
  91:	4d 01 c8             	add    r8,r9
  94:	f3 0f 11 01          	movss  DWORD PTR [rcx],xmm0
  98:	48 01 d9             	add    rcx,rbx
  9b:	49 39 c3             	cmp    r11,rax
  9e:	75 e0                	jne    80 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x80>
  a0:	5b                   	pop    rbx
  a1:	c3                   	ret
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

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIdEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4c 8b 5c 24 40       	mov    r11,QWORD PTR [rsp+0x40]
   6:	49 89 ca             	mov    r10,rcx
   9:	48 8b 4c 24 30       	mov    rcx,QWORD PTR [rsp+0x30]
   e:	4d 85 db             	test   r11,r11
  11:	74 47                	je     5a <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x5a>
  13:	48 83 7c 24 38 01    	cmp    QWORD PTR [rsp+0x38],0x1
  19:	0f 95 c0             	setne  al
  1c:	49 83 f9 01          	cmp    r9,0x1
  20:	0f 95 c3             	setne  bl
  23:	08 d8                	or     al,bl
  25:	75 39                	jne    60 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x60>
  27:	31 c0                	xor    eax,eax
  29:	48 83 fa 01          	cmp    rdx,0x1
  2d:	75 31                	jne    60 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x60>
  2f:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  35:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  3c:	00 00 00 00 
  40:	f2 41 0f 10 04 c0    	movsd  xmm0,QWORD PTR [r8+rax*8]
  46:	f2 41 0f 59 04 c2    	mulsd  xmm0,QWORD PTR [r10+rax*8]
  4c:	f2 0f 11 04 c1       	movsd  QWORD PTR [rcx+rax*8],xmm0
  51:	48 83 c0 01          	add    rax,0x1
  55:	49 39 c3             	cmp    r11,rax
  58:	75 e6                	jne    40 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x40>
  5a:	5b                   	pop    rbx
  5b:	c3                   	ret
  5c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
  60:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
  65:	48 c1 e2 03          	shl    rdx,0x3
  69:	49 c1 e1 03          	shl    r9,0x3
  6d:	48 8d 1c c5 00 00 00 	lea    rbx,[rax*8+0x0]
  74:	00 
  75:	31 c0                	xor    eax,eax
  77:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  7e:	00 00 
  80:	f2 41 0f 10 02       	movsd  xmm0,QWORD PTR [r10]
  85:	f2 41 0f 59 00       	mulsd  xmm0,QWORD PTR [r8]
  8a:	48 83 c0 01          	add    rax,0x1
  8e:	49 01 d2             	add    r10,rdx
  91:	4d 01 c8             	add    r8,r9
  94:	f2 0f 11 01          	movsd  QWORD PTR [rcx],xmm0
  98:	48 01 d9             	add    rcx,rbx
  9b:	49 39 c3             	cmp    r11,rax
  9e:	75 e0                	jne    80 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x80>
  a0:	5b                   	pop    rbx
  a1:	c3                   	ret
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

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIfEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)>:
   0:	48 8b 44 24 30       	mov    rax,QWORD PTR [rsp+0x30]
   5:	48 8b 54 24 28       	mov    rdx,QWORD PTR [rsp+0x28]
   a:	48 85 c0             	test   rax,rax
   d:	74 68                	je     77 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x77>
   f:	f3 41 0f 10 19       	movss  xmm3,DWORD PTR [r9]
  14:	f3 0f 11 1a          	movss  DWORD PTR [rdx],xmm3
  18:	48 83 f8 01          	cmp    rax,0x1
  1c:	74 59                	je     77 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x77>
  1e:	48 8d 48 ff          	lea    rcx,[rax-0x1]
  22:	f3 41 0f 10 1c 89    	movss  xmm3,DWORD PTR [r9+rcx*4]
  28:	f3 0f 11 1c 8a       	movss  DWORD PTR [rdx+rcx*4],xmm3
  2d:	48 83 f8 02          	cmp    rax,0x2
  31:	74 44                	je     77 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x77>
  33:	48 8d 0c 8d fc ff ff 	lea    rcx,[rcx*4-0x4]
  3a:	ff 
  3b:	31 c0                	xor    eax,eax
  3d:	0f 1f 00             	nop    DWORD PTR [rax]
  40:	f3 41 0f 10 1c 01    	movss  xmm3,DWORD PTR [r9+rax*1]
  46:	f3 41 0f 10 64 01 04 	movss  xmm4,DWORD PTR [r9+rax*1+0x4]
  4d:	f3 0f 59 d8          	mulss  xmm3,xmm0
  51:	f3 0f 59 e1          	mulss  xmm4,xmm1
  55:	f3 0f 58 dc          	addss  xmm3,xmm4
  59:	f3 41 0f 10 64 01 08 	movss  xmm4,DWORD PTR [r9+rax*1+0x8]
  60:	f3 0f 59 e2          	mulss  xmm4,xmm2
  64:	f3 0f 58 dc          	addss  xmm3,xmm4
  68:	f3 0f 11 5c 02 04    	movss  DWORD PTR [rdx+rax*1+0x4],xmm3
  6e:	48 83 c0 04          	add    rax,0x4
  72:	48 39 c1             	cmp    rcx,rax
  75:	75 c9                	jne    40 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x40>
  77:	c3                   	ret
  78:	90                   	nop
  79:	90                   	nop
  7a:	90                   	nop
  7b:	90                   	nop
  7c:	90                   	nop
  7d:	90                   	nop
  7e:	90                   	nop
  7f:	90                   	nop

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIdEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)>:
   0:	48 8b 44 24 30       	mov    rax,QWORD PTR [rsp+0x30]
   5:	48 8b 54 24 28       	mov    rdx,QWORD PTR [rsp+0x28]
   a:	48 85 c0             	test   rax,rax
   d:	74 68                	je     77 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x77>
   f:	f2 41 0f 10 19       	movsd  xmm3,QWORD PTR [r9]
  14:	f2 0f 11 1a          	movsd  QWORD PTR [rdx],xmm3
  18:	48 83 f8 01          	cmp    rax,0x1
  1c:	74 59                	je     77 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x77>
  1e:	48 8d 48 ff          	lea    rcx,[rax-0x1]
  22:	f2 41 0f 10 1c c9    	movsd  xmm3,QWORD PTR [r9+rcx*8]
  28:	f2 0f 11 1c ca       	movsd  QWORD PTR [rdx+rcx*8],xmm3
  2d:	48 83 f8 02          	cmp    rax,0x2
  31:	74 44                	je     77 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x77>
  33:	48 8d 0c cd f8 ff ff 	lea    rcx,[rcx*8-0x8]
  3a:	ff 
  3b:	31 c0                	xor    eax,eax
  3d:	0f 1f 00             	nop    DWORD PTR [rax]
  40:	f2 41 0f 10 1c 01    	movsd  xmm3,QWORD PTR [r9+rax*1]
  46:	f2 41 0f 10 64 01 08 	movsd  xmm4,QWORD PTR [r9+rax*1+0x8]
  4d:	f2 0f 59 d8          	mulsd  xmm3,xmm0
  51:	f2 0f 59 e1          	mulsd  xmm4,xmm1
  55:	f2 0f 58 dc          	addsd  xmm3,xmm4
  59:	f2 41 0f 10 64 01 10 	movsd  xmm4,QWORD PTR [r9+rax*1+0x10]
  60:	f2 0f 59 e2          	mulsd  xmm4,xmm2
  64:	f2 0f 58 dc          	addsd  xmm3,xmm4
  68:	f2 0f 11 5c 02 08    	movsd  QWORD PTR [rdx+rax*1+0x8],xmm3
  6e:	48 83 c0 08          	add    rax,0x8
  72:	48 39 c1             	cmp    rcx,rax
  75:	75 c9                	jne    40 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x40>
  77:	c3                   	ret
  78:	90                   	nop
  79:	90                   	nop
  7a:	90                   	nop
  7b:	90                   	nop
  7c:	90                   	nop
  7d:	90                   	nop
  7e:	90                   	nop
  7f:	90                   	nop
