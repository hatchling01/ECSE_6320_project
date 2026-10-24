; Targeted disassembly: gcc-native
; Object file: 
C:\Users\CHOUDN3\Downloads\EcSE_4320\ecse6320-project1-simd\build-gcc-native\CMakeFiles\project_kernels.dir\src\kernels.cpp.obj
; GNU objdump -d -C -Mintel; project_kernels symbols only.

0000000000000000 <void project::axpy<float>(float, float const*, float*, unsigned long long)>:
   0:	62 f2 7d 48 18 c8    	vbroadcastss zmm1,xmm0
   6:	4d 85 c9             	test   r9,r9
   9:	0f 84 99 00 00 00    	je     a8 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xa8>
   f:	49 8d 40 fc          	lea    rax,[r8-0x4]
  13:	48 29 d0             	sub    rax,rdx
  16:	48 83 f8 38          	cmp    rax,0x38
  1a:	0f 86 90 00 00 00    	jbe    b0 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xb0>
  20:	49 8d 41 ff          	lea    rax,[r9-0x1]
  24:	48 83 f8 0e          	cmp    rax,0xe
  28:	0f 86 af 00 00 00    	jbe    dd <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xdd>
  2e:	4d 89 ca             	mov    r10,r9
  31:	49 c1 ea 04          	shr    r10,0x4
  35:	4c 89 d1             	mov    rcx,r10
  38:	48 c1 e1 06          	shl    rcx,0x6
  3c:	31 c0                	xor    eax,eax
  3e:	66 90                	xchg   ax,ax
  40:	62 f1 7c 48 10 04 02 	vmovups zmm0,ZMMWORD PTR [rdx+rax*1]
  47:	62 d2 75 48 a8 04 00 	vfmadd213ps zmm0,zmm1,ZMMWORD PTR [r8+rax*1]
  4e:	62 d1 7c 48 11 04 00 	vmovups ZMMWORD PTR [r8+rax*1],zmm0
  55:	48 83 c0 40          	add    rax,0x40
  59:	48 39 c8             	cmp    rax,rcx
  5c:	75 e2                	jne    40 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x40>
  5e:	4c 89 d0             	mov    rax,r10
  61:	48 c1 e0 04          	shl    rax,0x4
  65:	49 39 c1             	cmp    r9,rax
  68:	74 3e                	je     a8 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xa8>
  6a:	49 8d 0c 80          	lea    rcx,[r8+rax*4]
  6e:	49 29 c1             	sub    r9,rax
  71:	41 b8 10 00 00 00    	mov    r8d,0x10
  77:	4d 39 c1             	cmp    r9,r8
  7a:	4d 0f 47 c8          	cmova  r9,r8
  7e:	62 d2 7d 08 7a c1    	vpbroadcastb xmm0,r9d
  84:	62 f3 7d 08 3e 0d ff 	vpcmpnleub k1,xmm0,XMMWORD PTR [rip+0xffffffffffffffff]        # 8e <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x8e>
  8b:	ff ff ff 06 
  8f:	62 f1 7c c9 10 14 82 	vmovups zmm2{k1}{z},ZMMWORD PTR [rdx+rax*4]
  96:	62 f1 7c c9 10 01    	vmovups zmm0{k1}{z},ZMMWORD PTR [rcx]
  9c:	62 f2 7d c9 98 ca    	vfmadd132ps zmm1{k1}{z},zmm0,zmm2
  a2:	62 f1 7c 49 11 09    	vmovups ZMMWORD PTR [rcx]{k1},zmm1
  a8:	c5 f8 77             	vzeroupper
  ab:	c3                   	ret
  ac:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
  b0:	31 c0                	xor    eax,eax
  b2:	0f 1f 00             	nop    DWORD PTR [rax]
  b5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  bc:	00 00 00 00 
  c0:	c5 fa 10 0c 82       	vmovss xmm1,DWORD PTR [rdx+rax*4]
  c5:	c4 c2 79 a9 0c 80    	vfmadd213ss xmm1,xmm0,DWORD PTR [r8+rax*4]
  cb:	c4 c1 7a 11 0c 80    	vmovss DWORD PTR [r8+rax*4],xmm1
  d1:	48 ff c0             	inc    rax
  d4:	49 39 c1             	cmp    r9,rax
  d7:	75 e7                	jne    c0 <void project::axpy<float>(float, float const*, float*, unsigned long long)+0xc0>
  d9:	c5 f8 77             	vzeroupper
  dc:	c3                   	ret
  dd:	31 c0                	xor    eax,eax
  df:	eb 89                	jmp    6a <void project::axpy<float>(float, float const*, float*, unsigned long long)+0x6a>
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

Disassembly of section .text$_ZN7project4axpyIdEEvT_PKS1_PS1_y:


0000000000000000 <void project::axpy<double>(double, double const*, double*, unsigned long long)>:
   0:	62 f2 fd 48 19 c8    	vbroadcastsd zmm1,xmm0
   6:	4d 85 c9             	test   r9,r9
   9:	0f 84 8b 00 00 00    	je     9a <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x9a>
   f:	49 8d 40 f8          	lea    rax,[r8-0x8]
  13:	48 29 d0             	sub    rax,rdx
  16:	48 83 f8 30          	cmp    rax,0x30
  1a:	0f 86 80 00 00 00    	jbe    a0 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xa0>
  20:	49 8d 41 ff          	lea    rax,[r9-0x1]
  24:	48 83 f8 06          	cmp    rax,0x6
  28:	0f 86 af 00 00 00    	jbe    dd <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xdd>
  2e:	4d 89 ca             	mov    r10,r9
  31:	49 c1 ea 03          	shr    r10,0x3
  35:	4c 89 d1             	mov    rcx,r10
  38:	48 c1 e1 06          	shl    rcx,0x6
  3c:	31 c0                	xor    eax,eax
  3e:	66 90                	xchg   ax,ax
  40:	62 f1 fd 48 10 04 02 	vmovupd zmm0,ZMMWORD PTR [rdx+rax*1]
  47:	62 d2 f5 48 a8 04 00 	vfmadd213pd zmm0,zmm1,ZMMWORD PTR [r8+rax*1]
  4e:	62 d1 fd 48 11 04 00 	vmovupd ZMMWORD PTR [r8+rax*1],zmm0
  55:	48 83 c0 40          	add    rax,0x40
  59:	48 39 c8             	cmp    rax,rcx
  5c:	75 e2                	jne    40 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x40>
  5e:	4a 8d 04 d5 00 00 00 	lea    rax,[r10*8+0x0]
  65:	00 
  66:	49 39 c1             	cmp    r9,rax
  69:	74 2f                	je     9a <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x9a>
  6b:	49 29 c1             	sub    r9,rax
  6e:	62 d2 fd 48 7c c1    	vpbroadcastq zmm0,r9
  74:	62 f3 fd 48 1e 0d 3f 	vpcmpnleuq k1,zmm0,ZMMWORD PTR [rip+0x3f]        # be <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xbe>
  7b:	00 00 00 06 
  7f:	62 f1 fd c9 10 14 c2 	vmovupd zmm2{k1}{z},ZMMWORD PTR [rdx+rax*8]
  86:	62 d1 fd c9 10 04 c0 	vmovupd zmm0{k1}{z},ZMMWORD PTR [r8+rax*8]
  8d:	62 f2 fd c9 98 ca    	vfmadd132pd zmm1{k1}{z},zmm0,zmm2
  93:	62 d1 fd 49 11 0c c0 	vmovupd ZMMWORD PTR [r8+rax*8]{k1},zmm1
  9a:	c5 f8 77             	vzeroupper
  9d:	c3                   	ret
  9e:	66 90                	xchg   ax,ax
  a0:	31 c0                	xor    eax,eax
  a2:	0f 1f 84 00 00 00 00 	nop    DWORD PTR [rax+rax*1+0x0]
  a9:	00 
  aa:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  b1:	00 00 00 00 
  b5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  bc:	00 00 00 00 
  c0:	c5 fb 10 0c c2       	vmovsd xmm1,QWORD PTR [rdx+rax*8]
  c5:	c4 c2 f9 a9 0c c0    	vfmadd213sd xmm1,xmm0,QWORD PTR [r8+rax*8]
  cb:	c4 c1 7b 11 0c c0    	vmovsd QWORD PTR [r8+rax*8],xmm1
  d1:	48 ff c0             	inc    rax
  d4:	49 39 c1             	cmp    r9,rax
  d7:	75 e7                	jne    c0 <void project::axpy<double>(double, double const*, double*, unsigned long long)+0xc0>
  d9:	c5 f8 77             	vzeroupper
  dc:	c3                   	ret
  dd:	31 c0                	xor    eax,eax
  df:	eb 8a                	jmp    6b <void project::axpy<double>(double, double const*, double*, unsigned long long)+0x6b>
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

Disassembly of section .text$_ZN7project11dot_productIfEET_PKS1_S3_y:


0000000000000000 <float project::dot_product<float>(float const*, float const*, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4d 85 c0             	test   r8,r8
   4:	0f 84 06 02 00 00    	je     210 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x210>
   a:	49 8d 40 ff          	lea    rax,[r8-0x1]
   e:	48 83 f8 0e          	cmp    rax,0xe
  12:	0f 86 fe 01 00 00    	jbe    216 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x216>
  18:	4d 89 c1             	mov    r9,r8
  1b:	49 c1 e9 04          	shr    r9,0x4
  1f:	c5 f8 57 c0          	vxorps xmm0,xmm0,xmm0
  23:	4d 89 ca             	mov    r10,r9
  26:	49 c1 e2 06          	shl    r10,0x6
  2a:	31 c0                	xor    eax,eax
  2c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
  30:	62 f1 7c 48 10 0c 02 	vmovups zmm1,ZMMWORD PTR [rdx+rax*1]
  37:	62 f1 74 48 59 0c 01 	vmulps zmm1,zmm1,ZMMWORD PTR [rcx+rax*1]
  3e:	48 83 c0 40          	add    rax,0x40
  42:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
  46:	c5 f0 c6 e1 55       	vshufps xmm4,xmm1,xmm1,0x55
  4b:	c5 f0 c6 d9 ff       	vshufps xmm3,xmm1,xmm1,0xff
  50:	62 f3 75 28 03 d1 07 	valignd ymm2,ymm1,ymm1,0x7
  57:	c5 fa 58 c4          	vaddss xmm0,xmm0,xmm4
  5b:	c5 f0 15 e1          	vunpckhps xmm4,xmm1,xmm1
  5f:	c5 fa 58 c4          	vaddss xmm0,xmm0,xmm4
  63:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
  67:	62 f3 7d 28 19 cb 01 	vextractf32x4 xmm3,ymm1,0x1
  6e:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
  72:	62 f3 75 28 03 d9 05 	valignd ymm3,ymm1,ymm1,0x5
  79:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
  7d:	62 f3 75 28 03 d9 06 	valignd ymm3,ymm1,ymm1,0x6
  84:	62 f3 7d 48 1b c9 01 	vextractf32x8 ymm1,zmm1,0x1
  8b:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
  8f:	c5 f0 c6 d9 55       	vshufps xmm3,xmm1,xmm1,0x55
  94:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
  98:	c5 f0 c6 d1 ff       	vshufps xmm2,xmm1,xmm1,0xff
  9d:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
  a1:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
  a5:	c5 f0 15 d9          	vunpckhps xmm3,xmm1,xmm1
  a9:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
  ad:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
  b1:	62 f3 7d 28 19 ca 01 	vextractf32x4 xmm2,ymm1,0x1
  b8:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
  bc:	62 f3 75 28 03 d1 05 	valignd ymm2,ymm1,ymm1,0x5
  c3:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
  c7:	62 f3 75 28 03 d1 06 	valignd ymm2,ymm1,ymm1,0x6
  ce:	62 f3 75 28 03 c9 07 	valignd ymm1,ymm1,ymm1,0x7
  d5:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
  d9:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
  dd:	4c 39 d0             	cmp    rax,r10
  e0:	0f 85 4a ff ff ff    	jne    30 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x30>
  e6:	4c 89 c8             	mov    rax,r9
  e9:	48 c1 e0 04          	shl    rax,0x4
  ed:	49 39 c0             	cmp    r8,rax
  f0:	0f 84 0a 01 00 00    	je     200 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x200>
  f6:	4d 89 c1             	mov    r9,r8
  f9:	49 29 c1             	sub    r9,rax
  fc:	4d 8d 51 ff          	lea    r10,[r9-0x1]
 100:	49 83 fa 06          	cmp    r10,0x6
 104:	0f 86 17 01 00 00    	jbe    221 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x221>
 10a:	c5 fc 10 0c 81       	vmovups ymm1,YMMWORD PTR [rcx+rax*4]
 10f:	c5 f4 59 0c 82       	vmulps ymm1,ymm1,YMMWORD PTR [rdx+rax*4]
 114:	4d 89 cb             	mov    r11,r9
 117:	49 83 e3 f8          	and    r11,0xfffffffffffffff8
 11b:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
 11f:	c5 f0 c6 d9 55       	vshufps xmm3,xmm1,xmm1,0x55
 124:	c5 f0 c6 d1 ff       	vshufps xmm2,xmm1,xmm1,0xff
 129:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
 12d:	c5 f0 15 d9          	vunpckhps xmm3,xmm1,xmm1
 131:	c5 fa 58 c3          	vaddss xmm0,xmm0,xmm3
 135:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
 139:	62 f3 7d 28 19 ca 01 	vextractf32x4 xmm2,ymm1,0x1
 140:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
 144:	62 f3 75 28 03 d1 05 	valignd ymm2,ymm1,ymm1,0x5
 14b:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
 14f:	62 f3 75 28 03 d1 06 	valignd ymm2,ymm1,ymm1,0x6
 156:	62 f3 75 28 03 c9 07 	valignd ymm1,ymm1,ymm1,0x7
 15d:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
 161:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
 165:	41 f6 c1 07          	test   r9b,0x7
 169:	0f 84 91 00 00 00    	je     200 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x200>
 16f:	4e 8d 14 18          	lea    r10,[rax+r11*1]
 173:	4d 29 d9             	sub    r9,r11
 176:	49 8d 59 ff          	lea    rbx,[r9-0x1]
 17a:	48 83 fb 02          	cmp    rbx,0x2
 17e:	76 3b                	jbe    1bb <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x1bb>
 180:	4c 01 d8             	add    rax,r11
 183:	c5 f8 10 0c 81       	vmovups xmm1,XMMWORD PTR [rcx+rax*4]
 188:	c5 f0 59 0c 82       	vmulps xmm1,xmm1,XMMWORD PTR [rdx+rax*4]
 18d:	4c 89 c8             	mov    rax,r9
 190:	48 83 e0 fc          	and    rax,0xfffffffffffffffc
 194:	41 83 e1 03          	and    r9d,0x3
 198:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
 19c:	c5 f0 c6 d1 55       	vshufps xmm2,xmm1,xmm1,0x55
 1a1:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
 1a5:	c5 f0 15 d1          	vunpckhps xmm2,xmm1,xmm1
 1a9:	c5 f0 c6 c9 ff       	vshufps xmm1,xmm1,xmm1,0xff
 1ae:	c5 fa 58 c2          	vaddss xmm0,xmm0,xmm2
 1b2:	c5 fa 58 c1          	vaddss xmm0,xmm0,xmm1
 1b6:	74 48                	je     200 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x200>
 1b8:	49 01 c2             	add    r10,rax
 1bb:	4d 8d 4a 01          	lea    r9,[r10+0x1]
 1bf:	c4 a1 7a 10 2c 91    	vmovss xmm5,DWORD PTR [rcx+r10*4]
 1c5:	4a 8d 04 95 00 00 00 	lea    rax,[r10*4+0x0]
 1cc:	00 
 1cd:	c4 a2 51 b9 04 92    	vfmadd231ss xmm0,xmm5,DWORD PTR [rdx+r10*4]
 1d3:	4d 39 c1             	cmp    r9,r8
 1d6:	73 28                	jae    200 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x200>
 1d8:	49 83 c2 02          	add    r10,0x2
 1dc:	c5 fa 10 6c 02 04    	vmovss xmm5,DWORD PTR [rdx+rax*1+0x4]
 1e2:	c4 e2 51 b9 44 01 04 	vfmadd231ss xmm0,xmm5,DWORD PTR [rcx+rax*1+0x4]
 1e9:	4d 39 c2             	cmp    r10,r8
 1ec:	73 12                	jae    200 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x200>
 1ee:	c5 fa 10 6c 01 08    	vmovss xmm5,DWORD PTR [rcx+rax*1+0x8]
 1f4:	c4 e2 51 b9 44 02 08 	vfmadd231ss xmm0,xmm5,DWORD PTR [rdx+rax*1+0x8]
 1fb:	c5 f8 77             	vzeroupper
 1fe:	5b                   	pop    rbx
 1ff:	c3                   	ret
 200:	c5 f8 77             	vzeroupper
 203:	5b                   	pop    rbx
 204:	c3                   	ret
 205:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 20c:	00 00 00 00 
 210:	c5 f8 57 c0          	vxorps xmm0,xmm0,xmm0
 214:	5b                   	pop    rbx
 215:	c3                   	ret
 216:	c5 f8 57 c0          	vxorps xmm0,xmm0,xmm0
 21a:	31 c0                	xor    eax,eax
 21c:	e9 d5 fe ff ff       	jmp    f6 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0xf6>
 221:	49 89 c2             	mov    r10,rax
 224:	45 31 db             	xor    r11d,r11d
 227:	e9 47 ff ff ff       	jmp    173 <float project::dot_product<float>(float const*, float const*, unsigned long long)+0x173>
 22c:	90                   	nop
 22d:	90                   	nop
 22e:	90                   	nop
 22f:	90                   	nop

Disassembly of section .text$_ZN7project11dot_productIdEET_PKS1_S3_y:


0000000000000000 <double project::dot_product<double>(double const*, double const*, unsigned long long)>:
   0:	49 89 ca             	mov    r10,rcx
   3:	4d 85 c0             	test   r8,r8
   6:	0f 84 44 01 00 00    	je     150 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x150>
   c:	49 8d 40 ff          	lea    rax,[r8-0x1]
  10:	48 83 f8 06          	cmp    rax,0x6
  14:	0f 86 3b 01 00 00    	jbe    155 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x155>
  1a:	4c 89 c1             	mov    rcx,r8
  1d:	48 c1 e9 03          	shr    rcx,0x3
  21:	c5 f9 57 c0          	vxorpd xmm0,xmm0,xmm0
  25:	49 89 c9             	mov    r9,rcx
  28:	49 c1 e1 06          	shl    r9,0x6
  2c:	31 c0                	xor    eax,eax
  2e:	66 90                	xchg   ax,ax
  30:	62 f1 fd 48 10 0c 02 	vmovupd zmm1,ZMMWORD PTR [rdx+rax*1]
  37:	62 d1 f5 48 59 0c 02 	vmulpd zmm1,zmm1,ZMMWORD PTR [r10+rax*1]
  3e:	48 83 c0 40          	add    rax,0x40
  42:	c5 fb 58 c1          	vaddsd xmm0,xmm0,xmm1
  46:	c5 f1 15 d9          	vunpckhpd xmm3,xmm1,xmm1
  4a:	62 f3 f5 28 03 d1 03 	valignq ymm2,ymm1,ymm1,0x3
  51:	c5 fb 58 c3          	vaddsd xmm0,xmm0,xmm3
  55:	62 f3 fd 28 19 cb 01 	vextractf64x2 xmm3,ymm1,0x1
  5c:	62 f3 fd 48 1b c9 01 	vextractf64x4 ymm1,zmm1,0x1
  63:	c5 fb 58 c3          	vaddsd xmm0,xmm0,xmm3
  67:	c5 fb 58 c2          	vaddsd xmm0,xmm0,xmm2
  6b:	c5 f1 15 d1          	vunpckhpd xmm2,xmm1,xmm1
  6f:	c5 fb 58 c1          	vaddsd xmm0,xmm0,xmm1
  73:	c5 fb 58 c2          	vaddsd xmm0,xmm0,xmm2
  77:	62 f3 fd 28 19 ca 01 	vextractf64x2 xmm2,ymm1,0x1
  7e:	62 f3 f5 28 03 c9 03 	valignq ymm1,ymm1,ymm1,0x3
  85:	c5 fb 58 c2          	vaddsd xmm0,xmm0,xmm2
  89:	c5 fb 58 c1          	vaddsd xmm0,xmm0,xmm1
  8d:	49 39 c1             	cmp    r9,rax
  90:	75 9e                	jne    30 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x30>
  92:	48 8d 04 cd 00 00 00 	lea    rax,[rcx*8+0x0]
  99:	00 
  9a:	49 39 c0             	cmp    r8,rax
  9d:	0f 84 9d 00 00 00    	je     140 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x140>
  a3:	4c 89 c1             	mov    rcx,r8
  a6:	48 29 c1             	sub    rcx,rax
  a9:	4c 8d 49 ff          	lea    r9,[rcx-0x1]
  ad:	49 83 f9 02          	cmp    r9,0x2
  b1:	76 3c                	jbe    ef <double project::dot_product<double>(double const*, double const*, unsigned long long)+0xef>
  b3:	c4 c1 7d 10 0c c2    	vmovupd ymm1,YMMWORD PTR [r10+rax*8]
  b9:	c5 f5 59 0c c2       	vmulpd ymm1,ymm1,YMMWORD PTR [rdx+rax*8]
  be:	49 89 c9             	mov    r9,rcx
  c1:	49 83 e1 fc          	and    r9,0xfffffffffffffffc
  c5:	83 e1 03             	and    ecx,0x3
  c8:	c5 fb 58 c1          	vaddsd xmm0,xmm0,xmm1
  cc:	c5 f1 15 d1          	vunpckhpd xmm2,xmm1,xmm1
  d0:	c5 fb 58 c2          	vaddsd xmm0,xmm0,xmm2
  d4:	62 f3 fd 28 19 ca 01 	vextractf64x2 xmm2,ymm1,0x1
  db:	62 f3 f5 28 03 c9 03 	valignq ymm1,ymm1,ymm1,0x3
  e2:	c5 fb 58 c2          	vaddsd xmm0,xmm0,xmm2
  e6:	c5 fb 58 c1          	vaddsd xmm0,xmm0,xmm1
  ea:	74 54                	je     140 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x140>
  ec:	4c 01 c8             	add    rax,r9
  ef:	4c 8d 48 01          	lea    r9,[rax+0x1]
  f3:	c4 c1 7b 10 2c c2    	vmovsd xmm5,QWORD PTR [r10+rax*8]
  f9:	48 8d 0c c5 00 00 00 	lea    rcx,[rax*8+0x0]
 100:	00 
 101:	c4 e2 d1 b9 04 c2    	vfmadd231sd xmm0,xmm5,QWORD PTR [rdx+rax*8]
 107:	4d 39 c1             	cmp    r9,r8
 10a:	73 34                	jae    140 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x140>
 10c:	48 83 c0 02          	add    rax,0x2
 110:	c5 fb 10 6c 0a 08    	vmovsd xmm5,QWORD PTR [rdx+rcx*1+0x8]
 116:	c4 c2 d1 b9 44 0a 08 	vfmadd231sd xmm0,xmm5,QWORD PTR [r10+rcx*1+0x8]
 11d:	4c 39 c0             	cmp    rax,r8
 120:	73 1e                	jae    140 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0x140>
 122:	c4 c1 7b 10 6c 0a 10 	vmovsd xmm5,QWORD PTR [r10+rcx*1+0x10]
 129:	c4 e2 d1 b9 44 0a 10 	vfmadd231sd xmm0,xmm5,QWORD PTR [rdx+rcx*1+0x10]
 130:	c5 f8 77             	vzeroupper
 133:	c3                   	ret
 134:	90                   	nop
 135:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 13c:	00 00 00 00 
 140:	c5 f8 77             	vzeroupper
 143:	c3                   	ret
 144:	90                   	nop
 145:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 14c:	00 00 00 00 
 150:	c5 f9 57 c0          	vxorpd xmm0,xmm0,xmm0
 154:	c3                   	ret
 155:	c5 f9 57 c0          	vxorpd xmm0,xmm0,xmm0
 159:	31 c0                	xor    eax,eax
 15b:	e9 43 ff ff ff       	jmp    a3 <double project::dot_product<double>(double const*, double const*, unsigned long long)+0xa3>

Disassembly of section .text$_ZN7project20elementwise_multiplyIfEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 c0 00 00 00    	je     c9 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc9>
   9:	49 8d 40 fc          	lea    rax,[r8-0x4]
   d:	49 89 c2             	mov    r10,rax
  10:	49 29 ca             	sub    r10,rcx
  13:	49 83 fa 38          	cmp    r10,0x38
  17:	0f 86 b3 00 00 00    	jbe    d0 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xd0>
  1d:	48 29 d0             	sub    rax,rdx
  20:	48 83 f8 38          	cmp    rax,0x38
  24:	0f 86 a6 00 00 00    	jbe    d0 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xd0>
  2a:	49 8d 41 ff          	lea    rax,[r9-0x1]
  2e:	48 83 f8 0e          	cmp    rax,0xe
  32:	0f 86 c1 00 00 00    	jbe    f9 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xf9>
  38:	4d 89 ca             	mov    r10,r9
  3b:	49 c1 ea 04          	shr    r10,0x4
  3f:	4d 89 d3             	mov    r11,r10
  42:	49 c1 e3 06          	shl    r11,0x6
  46:	31 c0                	xor    eax,eax
  48:	66 90                	xchg   ax,ax
  4a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  51:	00 00 00 00 
  55:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  5c:	00 00 00 00 
  60:	62 f1 7c 48 10 04 02 	vmovups zmm0,ZMMWORD PTR [rdx+rax*1]
  67:	62 f1 7c 48 59 04 01 	vmulps zmm0,zmm0,ZMMWORD PTR [rcx+rax*1]
  6e:	62 d1 7c 48 11 04 00 	vmovups ZMMWORD PTR [r8+rax*1],zmm0
  75:	48 83 c0 40          	add    rax,0x40
  79:	4c 39 d8             	cmp    rax,r11
  7c:	75 e2                	jne    60 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x60>
  7e:	4c 89 d0             	mov    rax,r10
  81:	48 c1 e0 04          	shl    rax,0x4
  85:	49 39 c1             	cmp    r9,rax
  88:	74 3c                	je     c6 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xc6>
  8a:	49 29 c1             	sub    r9,rax
  8d:	41 ba 10 00 00 00    	mov    r10d,0x10
  93:	4d 39 d1             	cmp    r9,r10
  96:	4d 0f 47 ca          	cmova  r9,r10
  9a:	62 d2 7d 08 7a c1    	vpbroadcastb xmm0,r9d
  a0:	62 f3 7d 08 3e 0d ff 	vpcmpnleub k1,xmm0,XMMWORD PTR [rip+0xffffffffffffffff]        # aa <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xaa>
  a7:	ff ff ff 06 
  ab:	62 f1 7c c9 10 14 81 	vmovups zmm2{k1}{z},ZMMWORD PTR [rcx+rax*4]
  b2:	62 f1 7c c9 10 0c 82 	vmovups zmm1{k1}{z},ZMMWORD PTR [rdx+rax*4]
  b9:	62 f1 6c c9 59 c1    	vmulps zmm0{k1}{z},zmm2,zmm1
  bf:	62 d1 7c 49 11 04 80 	vmovups ZMMWORD PTR [r8+rax*4]{k1},zmm0
  c6:	c5 f8 77             	vzeroupper
  c9:	c3                   	ret
  ca:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  d0:	31 c0                	xor    eax,eax
  d2:	0f 1f 00             	nop    DWORD PTR [rax]
  d5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  dc:	00 00 00 00 
  e0:	c5 fa 10 04 81       	vmovss xmm0,DWORD PTR [rcx+rax*4]
  e5:	c5 fa 59 04 82       	vmulss xmm0,xmm0,DWORD PTR [rdx+rax*4]
  ea:	c4 c1 7a 11 04 80    	vmovss DWORD PTR [r8+rax*4],xmm0
  f0:	48 ff c0             	inc    rax
  f3:	49 39 c1             	cmp    r9,rax
  f6:	75 e8                	jne    e0 <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0xe0>
  f8:	c3                   	ret
  f9:	31 c0                	xor    eax,eax
  fb:	eb 8d                	jmp    8a <void project::elementwise_multiply<float>(float const*, float const*, float*, unsigned long long)+0x8a>
  fd:	90                   	nop
  fe:	90                   	nop
  ff:	90                   	nop

Disassembly of section .text$_ZN7project20elementwise_multiplyIdEEvPKT_S3_PS1_y:


0000000000000000 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)>:
   0:	4d 85 c9             	test   r9,r9
   3:	0f 84 b4 00 00 00    	je     bd <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xbd>
   9:	49 8d 40 f8          	lea    rax,[r8-0x8]
   d:	49 89 c2             	mov    r10,rax
  10:	49 29 ca             	sub    r10,rcx
  13:	49 83 fa 30          	cmp    r10,0x30
  17:	0f 86 a3 00 00 00    	jbe    c0 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xc0>
  1d:	48 29 d0             	sub    rax,rdx
  20:	48 83 f8 30          	cmp    rax,0x30
  24:	0f 86 96 00 00 00    	jbe    c0 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xc0>
  2a:	49 8d 41 ff          	lea    rax,[r9-0x1]
  2e:	48 83 f8 06          	cmp    rax,0x6
  32:	0f 86 c1 00 00 00    	jbe    f9 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xf9>
  38:	4d 89 cb             	mov    r11,r9
  3b:	49 c1 eb 03          	shr    r11,0x3
  3f:	4d 89 da             	mov    r10,r11
  42:	49 c1 e2 06          	shl    r10,0x6
  46:	31 c0                	xor    eax,eax
  48:	66 90                	xchg   ax,ax
  4a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  51:	00 00 00 00 
  55:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  5c:	00 00 00 00 
  60:	62 f1 fd 48 10 04 02 	vmovupd zmm0,ZMMWORD PTR [rdx+rax*1]
  67:	62 f1 fd 48 59 04 01 	vmulpd zmm0,zmm0,ZMMWORD PTR [rcx+rax*1]
  6e:	62 d1 fd 48 11 04 00 	vmovupd ZMMWORD PTR [r8+rax*1],zmm0
  75:	48 83 c0 40          	add    rax,0x40
  79:	4c 39 d0             	cmp    rax,r10
  7c:	75 e2                	jne    60 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x60>
  7e:	4a 8d 04 dd 00 00 00 	lea    rax,[r11*8+0x0]
  85:	00 
  86:	49 39 c1             	cmp    r9,rax
  89:	74 2f                	je     ba <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xba>
  8b:	49 29 c1             	sub    r9,rax
  8e:	62 d2 fd 48 7c c1    	vpbroadcastq zmm0,r9
  94:	62 f3 fd 48 1e 0d 3f 	vpcmpnleuq k1,zmm0,ZMMWORD PTR [rip+0x3f]        # de <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xde>
  9b:	00 00 00 06 
  9f:	62 f1 fd c9 10 14 c1 	vmovupd zmm2{k1}{z},ZMMWORD PTR [rcx+rax*8]
  a6:	62 f1 fd c9 10 0c c2 	vmovupd zmm1{k1}{z},ZMMWORD PTR [rdx+rax*8]
  ad:	62 f1 ed c9 59 c1    	vmulpd zmm0{k1}{z},zmm2,zmm1
  b3:	62 d1 fd 49 11 04 c0 	vmovupd ZMMWORD PTR [r8+rax*8]{k1},zmm0
  ba:	c5 f8 77             	vzeroupper
  bd:	c3                   	ret
  be:	66 90                	xchg   ax,ax
  c0:	31 c0                	xor    eax,eax
  c2:	0f 1f 84 00 00 00 00 	nop    DWORD PTR [rax+rax*1+0x0]
  c9:	00 
  ca:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  d1:	00 00 00 00 
  d5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  dc:	00 00 00 00 
  e0:	c5 fb 10 04 c1       	vmovsd xmm0,QWORD PTR [rcx+rax*8]
  e5:	c5 fb 59 04 c2       	vmulsd xmm0,xmm0,QWORD PTR [rdx+rax*8]
  ea:	c4 c1 7b 11 04 c0    	vmovsd QWORD PTR [r8+rax*8],xmm0
  f0:	48 ff c0             	inc    rax
  f3:	49 39 c1             	cmp    r9,rax
  f6:	75 e8                	jne    e0 <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0xe0>
  f8:	c3                   	ret
  f9:	31 c0                	xor    eax,eax
  fb:	eb 8e                	jmp    8b <void project::elementwise_multiply<double>(double const*, double const*, double*, unsigned long long)+0x8b>
  fd:	90                   	nop
  fe:	90                   	nop
  ff:	90                   	nop

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIfEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4c 8b 5c 24 40       	mov    r11,QWORD PTR [rsp+0x40]
   6:	4c 8b 54 24 30       	mov    r10,QWORD PTR [rsp+0x30]
   b:	4d 85 db             	test   r11,r11
   e:	0f 84 d4 00 00 00    	je     e8 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xe8>
  14:	48 83 7c 24 38 01    	cmp    QWORD PTR [rsp+0x38],0x1
  1a:	0f 95 c3             	setne  bl
  1d:	49 83 f9 01          	cmp    r9,0x1
  21:	0f 95 c0             	setne  al
  24:	08 c3                	or     bl,al
  26:	0f 85 c4 00 00 00    	jne    f0 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xf0>
  2c:	48 83 fa 01          	cmp    rdx,0x1
  30:	0f 85 ba 00 00 00    	jne    f0 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xf0>
  36:	49 8d 42 fc          	lea    rax,[r10-0x4]
  3a:	48 89 c2             	mov    rdx,rax
  3d:	48 29 ca             	sub    rdx,rcx
  40:	48 83 fa 38          	cmp    rdx,0x38
  44:	0f 86 26 01 00 00    	jbe    170 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x170>
  4a:	4c 29 c0             	sub    rax,r8
  4d:	48 83 f8 38          	cmp    rax,0x38
  51:	0f 86 19 01 00 00    	jbe    170 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x170>
  57:	49 8d 43 ff          	lea    rax,[r11-0x1]
  5b:	48 83 f8 0e          	cmp    rax,0xe
  5f:	0f 86 36 01 00 00    	jbe    19b <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x19b>
  65:	4c 89 da             	mov    rdx,r11
  68:	48 c1 ea 04          	shr    rdx,0x4
  6c:	49 89 d1             	mov    r9,rdx
  6f:	49 c1 e1 06          	shl    r9,0x6
  73:	31 c0                	xor    eax,eax
  75:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  7c:	00 00 00 00 
  80:	62 d1 7c 48 10 04 00 	vmovups zmm0,ZMMWORD PTR [r8+rax*1]
  87:	62 f1 7c 48 59 04 01 	vmulps zmm0,zmm0,ZMMWORD PTR [rcx+rax*1]
  8e:	62 d1 7c 48 11 04 02 	vmovups ZMMWORD PTR [r10+rax*1],zmm0
  95:	48 83 c0 40          	add    rax,0x40
  99:	4c 39 c8             	cmp    rax,r9
  9c:	75 e2                	jne    80 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x80>
  9e:	48 89 d0             	mov    rax,rdx
  a1:	48 c1 e0 04          	shl    rax,0x4
  a5:	49 39 c3             	cmp    r11,rax
  a8:	74 3b                	je     e5 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xe5>
  aa:	49 29 c3             	sub    r11,rax
  ad:	ba 10 00 00 00       	mov    edx,0x10
  b2:	49 39 d3             	cmp    r11,rdx
  b5:	4c 0f 47 da          	cmova  r11,rdx
  b9:	62 d2 7d 08 7a c3    	vpbroadcastb xmm0,r11d
  bf:	62 f3 7d 08 3e 0d ff 	vpcmpnleub k1,xmm0,XMMWORD PTR [rip+0xffffffffffffffff]        # c9 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xc9>
  c6:	ff ff ff 06 
  ca:	62 f1 7c c9 10 14 81 	vmovups zmm2{k1}{z},ZMMWORD PTR [rcx+rax*4]
  d1:	62 d1 7c c9 10 0c 80 	vmovups zmm1{k1}{z},ZMMWORD PTR [r8+rax*4]
  d8:	62 f1 6c c9 59 c1    	vmulps zmm0{k1}{z},zmm2,zmm1
  de:	62 d1 7c 49 11 04 82 	vmovups ZMMWORD PTR [r10+rax*4]{k1},zmm0
  e5:	c5 f8 77             	vzeroupper
  e8:	5b                   	pop    rbx
  e9:	c3                   	ret
  ea:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
  f0:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
  f5:	48 c1 e2 02          	shl    rdx,0x2
  f9:	49 c1 e1 02          	shl    r9,0x2
  fd:	48 8d 1c 85 00 00 00 	lea    rbx,[rax*4+0x0]
 104:	00 
 105:	31 c0                	xor    eax,eax
 107:	66 90                	xchg   ax,ax
 109:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 110:	00 00 00 00 
 114:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 11b:	00 00 00 00 
 11f:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 126:	00 00 00 00 
 12a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 131:	00 00 00 00 
 135:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 13c:	00 00 00 00 
 140:	c5 fa 10 01          	vmovss xmm0,DWORD PTR [rcx]
 144:	c4 c1 7a 59 00       	vmulss xmm0,xmm0,DWORD PTR [r8]
 149:	48 ff c0             	inc    rax
 14c:	48 01 d1             	add    rcx,rdx
 14f:	4d 01 c8             	add    r8,r9
 152:	c4 c1 7a 11 02       	vmovss DWORD PTR [r10],xmm0
 157:	49 01 da             	add    r10,rbx
 15a:	49 39 c3             	cmp    r11,rax
 15d:	75 e1                	jne    140 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x140>
 15f:	5b                   	pop    rbx
 160:	c3                   	ret
 161:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
 165:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 16c:	00 00 00 00 
 170:	31 c0                	xor    eax,eax
 172:	0f 1f 00             	nop    DWORD PTR [rax]
 175:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 17c:	00 00 00 00 
 180:	c5 fa 10 04 81       	vmovss xmm0,DWORD PTR [rcx+rax*4]
 185:	c4 c1 7a 59 04 80    	vmulss xmm0,xmm0,DWORD PTR [r8+rax*4]
 18b:	c4 c1 7a 11 04 82    	vmovss DWORD PTR [r10+rax*4],xmm0
 191:	48 ff c0             	inc    rax
 194:	49 39 c3             	cmp    r11,rax
 197:	75 e7                	jne    180 <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0x180>
 199:	5b                   	pop    rbx
 19a:	c3                   	ret
 19b:	31 c0                	xor    eax,eax
 19d:	e9 08 ff ff ff       	jmp    aa <void project::elementwise_multiply_strided<float>(float const*, unsigned long long, float const*, unsigned long long, float*, unsigned long long, unsigned long long)+0xaa>
 1a2:	90                   	nop
 1a3:	90                   	nop
 1a4:	90                   	nop
 1a5:	90                   	nop
 1a6:	90                   	nop
 1a7:	90                   	nop
 1a8:	90                   	nop
 1a9:	90                   	nop
 1aa:	90                   	nop
 1ab:	90                   	nop
 1ac:	90                   	nop
 1ad:	90                   	nop
 1ae:	90                   	nop
 1af:	90                   	nop
 1b0:	90                   	nop
 1b1:	90                   	nop
 1b2:	90                   	nop
 1b3:	90                   	nop
 1b4:	90                   	nop
 1b5:	90                   	nop
 1b6:	90                   	nop
 1b7:	90                   	nop
 1b8:	90                   	nop
 1b9:	90                   	nop
 1ba:	90                   	nop
 1bb:	90                   	nop
 1bc:	90                   	nop
 1bd:	90                   	nop
 1be:	90                   	nop
 1bf:	90                   	nop

Disassembly of section .text$_ZN7project28elementwise_multiply_stridedIdEEvPKT_yS3_yPS1_yy:


0000000000000000 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)>:
   0:	53                   	push   rbx
   1:	4c 8b 5c 24 40       	mov    r11,QWORD PTR [rsp+0x40]
   6:	4c 8b 54 24 30       	mov    r10,QWORD PTR [rsp+0x30]
   b:	4d 85 db             	test   r11,r11
   e:	0f 84 c9 00 00 00    	je     dd <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xdd>
  14:	48 83 7c 24 38 01    	cmp    QWORD PTR [rsp+0x38],0x1
  1a:	0f 95 c3             	setne  bl
  1d:	49 83 f9 01          	cmp    r9,0x1
  21:	0f 95 c0             	setne  al
  24:	08 c3                	or     bl,al
  26:	0f 85 b4 00 00 00    	jne    e0 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xe0>
  2c:	48 83 fa 01          	cmp    rdx,0x1
  30:	0f 85 aa 00 00 00    	jne    e0 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xe0>
  36:	49 8d 42 f8          	lea    rax,[r10-0x8]
  3a:	48 89 c2             	mov    rdx,rax
  3d:	48 29 ca             	sub    rdx,rcx
  40:	48 83 fa 30          	cmp    rdx,0x30
  44:	0f 86 e6 00 00 00    	jbe    130 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x130>
  4a:	4c 29 c0             	sub    rax,r8
  4d:	48 83 f8 30          	cmp    rax,0x30
  51:	0f 86 d9 00 00 00    	jbe    130 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x130>
  57:	49 8d 43 ff          	lea    rax,[r11-0x1]
  5b:	48 83 f8 06          	cmp    rax,0x6
  5f:	0f 86 f6 00 00 00    	jbe    15b <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x15b>
  65:	4d 89 d9             	mov    r9,r11
  68:	49 c1 e9 03          	shr    r9,0x3
  6c:	4c 89 ca             	mov    rdx,r9
  6f:	48 c1 e2 06          	shl    rdx,0x6
  73:	31 c0                	xor    eax,eax
  75:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  7c:	00 00 00 00 
  80:	62 d1 fd 48 10 04 00 	vmovupd zmm0,ZMMWORD PTR [r8+rax*1]
  87:	62 f1 fd 48 59 04 01 	vmulpd zmm0,zmm0,ZMMWORD PTR [rcx+rax*1]
  8e:	62 d1 fd 48 11 04 02 	vmovupd ZMMWORD PTR [r10+rax*1],zmm0
  95:	48 83 c0 40          	add    rax,0x40
  99:	48 39 d0             	cmp    rax,rdx
  9c:	75 e2                	jne    80 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x80>
  9e:	4a 8d 04 cd 00 00 00 	lea    rax,[r9*8+0x0]
  a5:	00 
  a6:	49 39 c3             	cmp    r11,rax
  a9:	74 2f                	je     da <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xda>
  ab:	49 29 c3             	sub    r11,rax
  ae:	62 d2 fd 48 7c c3    	vpbroadcastq zmm0,r11
  b4:	62 f3 fd 48 1e 0d 3f 	vpcmpnleuq k1,zmm0,ZMMWORD PTR [rip+0x3f]        # fe <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xfe>
  bb:	00 00 00 06 
  bf:	62 f1 fd c9 10 14 c1 	vmovupd zmm2{k1}{z},ZMMWORD PTR [rcx+rax*8]
  c6:	62 d1 fd c9 10 0c c0 	vmovupd zmm1{k1}{z},ZMMWORD PTR [r8+rax*8]
  cd:	62 f1 ed c9 59 c1    	vmulpd zmm0{k1}{z},zmm2,zmm1
  d3:	62 d1 fd 49 11 04 c2 	vmovupd ZMMWORD PTR [r10+rax*8]{k1},zmm0
  da:	c5 f8 77             	vzeroupper
  dd:	5b                   	pop    rbx
  de:	c3                   	ret
  df:	90                   	nop
  e0:	48 8b 44 24 38       	mov    rax,QWORD PTR [rsp+0x38]
  e5:	48 c1 e2 03          	shl    rdx,0x3
  e9:	49 c1 e1 03          	shl    r9,0x3
  ed:	48 8d 1c c5 00 00 00 	lea    rbx,[rax*8+0x0]
  f4:	00 
  f5:	31 c0                	xor    eax,eax
  f7:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  fe:	00 00 
 100:	c5 fb 10 01          	vmovsd xmm0,QWORD PTR [rcx]
 104:	c4 c1 7b 59 00       	vmulsd xmm0,xmm0,QWORD PTR [r8]
 109:	48 ff c0             	inc    rax
 10c:	48 01 d1             	add    rcx,rdx
 10f:	4d 01 c8             	add    r8,r9
 112:	c4 c1 7b 11 02       	vmovsd QWORD PTR [r10],xmm0
 117:	49 01 da             	add    r10,rbx
 11a:	49 39 c3             	cmp    r11,rax
 11d:	75 e1                	jne    100 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x100>
 11f:	5b                   	pop    rbx
 120:	c3                   	ret
 121:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
 125:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 12c:	00 00 00 00 
 130:	31 c0                	xor    eax,eax
 132:	0f 1f 00             	nop    DWORD PTR [rax]
 135:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 13c:	00 00 00 00 
 140:	c5 fb 10 04 c1       	vmovsd xmm0,QWORD PTR [rcx+rax*8]
 145:	c4 c1 7b 59 04 c0    	vmulsd xmm0,xmm0,QWORD PTR [r8+rax*8]
 14b:	c4 c1 7b 11 04 c2    	vmovsd QWORD PTR [r10+rax*8],xmm0
 151:	48 ff c0             	inc    rax
 154:	49 39 c3             	cmp    r11,rax
 157:	75 e7                	jne    140 <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0x140>
 159:	5b                   	pop    rbx
 15a:	c3                   	ret
 15b:	31 c0                	xor    eax,eax
 15d:	e9 49 ff ff ff       	jmp    ab <void project::elementwise_multiply_strided<double>(double const*, unsigned long long, double const*, unsigned long long, double*, unsigned long long, unsigned long long)+0xab>
 162:	90                   	nop
 163:	90                   	nop
 164:	90                   	nop
 165:	90                   	nop
 166:	90                   	nop
 167:	90                   	nop
 168:	90                   	nop
 169:	90                   	nop
 16a:	90                   	nop
 16b:	90                   	nop
 16c:	90                   	nop
 16d:	90                   	nop
 16e:	90                   	nop
 16f:	90                   	nop
 170:	90                   	nop
 171:	90                   	nop
 172:	90                   	nop
 173:	90                   	nop
 174:	90                   	nop
 175:	90                   	nop
 176:	90                   	nop
 177:	90                   	nop
 178:	90                   	nop
 179:	90                   	nop
 17a:	90                   	nop
 17b:	90                   	nop
 17c:	90                   	nop
 17d:	90                   	nop
 17e:	90                   	nop
 17f:	90                   	nop

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIfEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)>:
   0:	48 8b 44 24 30       	mov    rax,QWORD PTR [rsp+0x30]
   5:	48 8b 54 24 28       	mov    rdx,QWORD PTR [rsp+0x28]
   a:	62 f2 7d 48 18 e0    	vbroadcastss zmm4,xmm0
  10:	62 f2 7d 48 18 e9    	vbroadcastss zmm5,xmm1
  16:	62 f2 7d 48 18 da    	vbroadcastss zmm3,xmm2
  1c:	48 85 c0             	test   rax,rax
  1f:	0f 84 32 01 00 00    	je     157 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x157>
  25:	62 c1 7e 08 10 01    	vmovss xmm16,DWORD PTR [r9]
  2b:	62 e1 7e 08 11 02    	vmovss DWORD PTR [rdx],xmm16
  31:	48 83 f8 01          	cmp    rax,0x1
  35:	0f 84 1c 01 00 00    	je     157 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x157>
  3b:	48 8d 0c 85 fc ff ff 	lea    rcx,[rax*4-0x4]
  42:	ff 
  43:	62 c1 7e 08 10 04 09 	vmovss xmm16,DWORD PTR [r9+rcx*1]
  4a:	62 e1 7e 08 11 04 0a 	vmovss DWORD PTR [rdx+rcx*1],xmm16
  51:	48 83 f8 02          	cmp    rax,0x2
  55:	0f 84 fc 00 00 00    	je     157 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x157>
  5b:	49 89 d0             	mov    r8,rdx
  5e:	4d 29 c8             	sub    r8,r9
  61:	49 83 f8 40          	cmp    r8,0x40
  65:	0f 86 f5 00 00 00    	jbe    160 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x160>
  6b:	48 8d 48 fe          	lea    rcx,[rax-0x2]
  6f:	48 83 e8 03          	sub    rax,0x3
  73:	48 83 f8 0e          	cmp    rax,0xe
  77:	0f 86 28 01 00 00    	jbe    1a5 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x1a5>
  7d:	49 89 c8             	mov    r8,rcx
  80:	49 c1 e8 04          	shr    r8,0x4
  84:	62 f1 7c 48 28 d4    	vmovaps zmm2,zmm4
  8a:	62 f1 7c 48 28 cb    	vmovaps zmm1,zmm3
  90:	62 f1 7c 48 28 e5    	vmovaps zmm4,zmm5
  96:	4d 89 c2             	mov    r10,r8
  99:	49 c1 e2 06          	shl    r10,0x6
  9d:	31 c0                	xor    eax,eax
  9f:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  a6:	00 00 00 00 
  aa:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  b1:	00 00 00 00 
  b5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  bc:	00 00 00 00 
  c0:	62 d1 5c 48 59 84 01 	vmulps zmm0,zmm4,ZMMWORD PTR [r9+rax*1+0x4]
  c7:	04 00 00 00 
  cb:	62 d2 6d 48 b8 04 01 	vfmadd231ps zmm0,zmm2,ZMMWORD PTR [r9+rax*1]
  d2:	62 d2 75 48 b8 84 01 	vfmadd231ps zmm0,zmm1,ZMMWORD PTR [r9+rax*1+0x8]
  d9:	08 00 00 00 
  dd:	62 f1 7c 48 11 84 02 	vmovups ZMMWORD PTR [rdx+rax*1+0x4],zmm0
  e4:	04 00 00 00 
  e8:	48 83 c0 40          	add    rax,0x40
  ec:	4c 39 d0             	cmp    rax,r10
  ef:	75 cf                	jne    c0 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0xc0>
  f1:	49 c1 e0 04          	shl    r8,0x4
  f5:	4c 39 c1             	cmp    rcx,r8
  f8:	74 5d                	je     157 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x157>
  fa:	48 89 c8             	mov    rax,rcx
  fd:	4c 29 c0             	sub    rax,r8
 100:	b9 10 00 00 00       	mov    ecx,0x10
 105:	48 39 c8             	cmp    rax,rcx
 108:	48 0f 47 c1          	cmova  rax,rcx
 10c:	62 f2 7d 08 7a c0    	vpbroadcastb xmm0,eax
 112:	62 f3 7d 08 3e 0d ff 	vpcmpnleub k1,xmm0,XMMWORD PTR [rip+0xffffffffffffffff]        # 11c <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x11c>
 119:	ff ff ff 06 
 11d:	62 91 7c c9 10 ac 81 	vmovups zmm5{k1}{z},ZMMWORD PTR [r9+r8*4+0x4]
 124:	04 00 00 00 
 128:	62 91 7c c9 10 1c 81 	vmovups zmm3{k1}{z},ZMMWORD PTR [r9+r8*4]
 12f:	62 f1 5c c9 59 c5    	vmulps zmm0{k1}{z},zmm4,zmm5
 135:	62 f2 7d c9 98 d3    	vfmadd132ps zmm2{k1}{z},zmm0,zmm3
 13b:	62 91 7c c9 10 84 81 	vmovups zmm0{k1}{z},ZMMWORD PTR [r9+r8*4+0x8]
 142:	08 00 00 00 
 146:	62 f2 6d c9 98 c8    	vfmadd132ps zmm1{k1}{z},zmm2,zmm0
 14c:	62 b1 7c 49 11 8c 82 	vmovups ZMMWORD PTR [rdx+r8*4+0x4]{k1},zmm1
 153:	04 00 00 00 
 157:	c5 f8 77             	vzeroupper
 15a:	c3                   	ret
 15b:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
 160:	48 83 e9 04          	sub    rcx,0x4
 164:	31 c0                	xor    eax,eax
 166:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
 16a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 171:	00 00 00 00 
 175:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 17c:	00 00 00 00 
 180:	c4 c1 72 59 5c 01 04 	vmulss xmm3,xmm1,DWORD PTR [r9+rax*1+0x4]
 187:	c4 c2 79 b9 1c 01    	vfmadd231ss xmm3,xmm0,DWORD PTR [r9+rax*1]
 18d:	c4 c2 69 b9 5c 01 08 	vfmadd231ss xmm3,xmm2,DWORD PTR [r9+rax*1+0x8]
 194:	c5 fa 11 5c 02 04    	vmovss DWORD PTR [rdx+rax*1+0x4],xmm3
 19a:	48 83 c0 04          	add    rax,0x4
 19e:	48 39 c8             	cmp    rax,rcx
 1a1:	75 dd                	jne    180 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x180>
 1a3:	eb b2                	jmp    157 <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0x157>
 1a5:	62 f1 7c 48 28 d4    	vmovaps zmm2,zmm4
 1ab:	45 31 c0             	xor    r8d,r8d
 1ae:	62 f1 7c 48 28 e5    	vmovaps zmm4,zmm5
 1b4:	62 f1 7c 48 28 cb    	vmovaps zmm1,zmm3
 1ba:	e9 3b ff ff ff       	jmp    fa <void project::stencil_1d_three_point<float>(float, float, float, float const*, float*, unsigned long long)+0xfa>
 1bf:	90                   	nop

Disassembly of section .text$_ZN7project22stencil_1d_three_pointIdEEvT_S1_S1_PKS1_PS1_y:


0000000000000000 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)>:
   0:	48 8b 44 24 30       	mov    rax,QWORD PTR [rsp+0x30]
   5:	48 8b 54 24 28       	mov    rdx,QWORD PTR [rsp+0x28]
   a:	62 f2 fd 48 19 e0    	vbroadcastsd zmm4,xmm0
  10:	62 f2 fd 48 19 e9    	vbroadcastsd zmm5,xmm1
  16:	62 f2 fd 48 19 da    	vbroadcastsd zmm3,xmm2
  1c:	48 85 c0             	test   rax,rax
  1f:	0f 84 27 01 00 00    	je     14c <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x14c>
  25:	62 c1 ff 08 10 01    	vmovsd xmm16,QWORD PTR [r9]
  2b:	62 e1 ff 08 11 02    	vmovsd QWORD PTR [rdx],xmm16
  31:	48 83 f8 01          	cmp    rax,0x1
  35:	0f 84 11 01 00 00    	je     14c <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x14c>
  3b:	48 8d 0c c5 f8 ff ff 	lea    rcx,[rax*8-0x8]
  42:	ff 
  43:	62 c1 ff 08 10 04 09 	vmovsd xmm16,QWORD PTR [r9+rcx*1]
  4a:	62 e1 ff 08 11 04 0a 	vmovsd QWORD PTR [rdx+rcx*1],xmm16
  51:	48 83 f8 02          	cmp    rax,0x2
  55:	0f 84 f1 00 00 00    	je     14c <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x14c>
  5b:	49 89 d0             	mov    r8,rdx
  5e:	4d 29 c8             	sub    r8,r9
  61:	49 83 f8 40          	cmp    r8,0x40
  65:	0f 86 e5 00 00 00    	jbe    150 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x150>
  6b:	4c 8d 50 fe          	lea    r10,[rax-0x2]
  6f:	48 83 e8 03          	sub    rax,0x3
  73:	48 83 f8 06          	cmp    rax,0x6
  77:	0f 86 28 01 00 00    	jbe    1a5 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x1a5>
  7d:	4c 89 d1             	mov    rcx,r10
  80:	48 c1 e9 03          	shr    rcx,0x3
  84:	62 f1 fd 48 28 d4    	vmovapd zmm2,zmm4
  8a:	62 f1 fd 48 28 cb    	vmovapd zmm1,zmm3
  90:	62 f1 fd 48 28 e5    	vmovapd zmm4,zmm5
  96:	49 89 c8             	mov    r8,rcx
  99:	49 c1 e0 06          	shl    r8,0x6
  9d:	31 c0                	xor    eax,eax
  9f:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  a6:	00 00 00 00 
  aa:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  b1:	00 00 00 00 
  b5:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  bc:	00 00 00 00 
  c0:	62 d1 dd 48 59 84 01 	vmulpd zmm0,zmm4,ZMMWORD PTR [r9+rax*1+0x8]
  c7:	08 00 00 00 
  cb:	62 d2 ed 48 b8 04 01 	vfmadd231pd zmm0,zmm2,ZMMWORD PTR [r9+rax*1]
  d2:	62 d2 f5 48 b8 84 01 	vfmadd231pd zmm0,zmm1,ZMMWORD PTR [r9+rax*1+0x10]
  d9:	10 00 00 00 
  dd:	62 f1 fd 48 11 84 02 	vmovupd ZMMWORD PTR [rdx+rax*1+0x8],zmm0
  e4:	08 00 00 00 
  e8:	48 83 c0 40          	add    rax,0x40
  ec:	4c 39 c0             	cmp    rax,r8
  ef:	75 cf                	jne    c0 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0xc0>
  f1:	48 8d 04 cd 00 00 00 	lea    rax,[rcx*8+0x0]
  f8:	00 
  f9:	49 39 c2             	cmp    r10,rax
  fc:	74 4e                	je     14c <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x14c>
  fe:	49 29 c2             	sub    r10,rax
 101:	62 d2 fd 48 7c c2    	vpbroadcastq zmm0,r10
 107:	62 f3 fd 48 1e 0d 3f 	vpcmpnleuq k1,zmm0,ZMMWORD PTR [rip+0x3f]        # 151 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x151>
 10e:	00 00 00 06 
 112:	62 d1 fd c9 10 ac c1 	vmovupd zmm5{k1}{z},ZMMWORD PTR [r9+rax*8+0x8]
 119:	08 00 00 00 
 11d:	62 d1 fd c9 10 1c c1 	vmovupd zmm3{k1}{z},ZMMWORD PTR [r9+rax*8]
 124:	62 f1 dd c9 59 c5    	vmulpd zmm0{k1}{z},zmm4,zmm5
 12a:	62 f2 fd c9 98 d3    	vfmadd132pd zmm2{k1}{z},zmm0,zmm3
 130:	62 d1 fd c9 10 84 c1 	vmovupd zmm0{k1}{z},ZMMWORD PTR [r9+rax*8+0x10]
 137:	10 00 00 00 
 13b:	62 f2 ed c9 98 c8    	vfmadd132pd zmm1{k1}{z},zmm2,zmm0
 141:	62 f1 fd 49 11 8c c2 	vmovupd ZMMWORD PTR [rdx+rax*8+0x8]{k1},zmm1
 148:	08 00 00 00 
 14c:	c5 f8 77             	vzeroupper
 14f:	c3                   	ret
 150:	48 83 e9 08          	sub    rcx,0x8
 154:	31 c0                	xor    eax,eax
 156:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
 15d:	00 00 
 15f:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 166:	00 00 00 00 
 16a:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 171:	00 00 00 00 
 175:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
 17c:	00 00 00 00 
 180:	c4 c1 73 59 5c 01 08 	vmulsd xmm3,xmm1,QWORD PTR [r9+rax*1+0x8]
 187:	c4 c2 f9 b9 1c 01    	vfmadd231sd xmm3,xmm0,QWORD PTR [r9+rax*1]
 18d:	c4 c2 e9 b9 5c 01 10 	vfmadd231sd xmm3,xmm2,QWORD PTR [r9+rax*1+0x10]
 194:	c5 fb 11 5c 02 08    	vmovsd QWORD PTR [rdx+rax*1+0x8],xmm3
 19a:	48 83 c0 08          	add    rax,0x8
 19e:	48 39 c8             	cmp    rax,rcx
 1a1:	75 dd                	jne    180 <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x180>
 1a3:	eb a7                	jmp    14c <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0x14c>
 1a5:	62 f1 fd 48 28 d4    	vmovapd zmm2,zmm4
 1ab:	31 c0                	xor    eax,eax
 1ad:	62 f1 fd 48 28 e5    	vmovapd zmm4,zmm5
 1b3:	62 f1 fd 48 28 cb    	vmovapd zmm1,zmm3
 1b9:	e9 40 ff ff ff       	jmp    fe <void project::stencil_1d_three_point<double>(double, double, double, double const*, double*, unsigned long long)+0xfe>
 1be:	90                   	nop
 1bf:	90                   	nop
