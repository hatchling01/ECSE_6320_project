# Phase 3B Residual Variability

190/360 merged configurations remain above 10% CV; 100 remain above 20% CV.
No residual point was rerun more than once. Original and rerun samples are preserved separately.

| Kernel | Type | Build | N | Target bytes | CV | Median ns/element | Min | Max | Source |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| elementwise_multiply | float64 | gcc-native | 1048576 | 25,165,824 | 111.854% | 0.291204 | 0.226974 | 2.37093 | phase3b_targeted_rerun |
| axpy | float32 | gcc-native | 3145728 | 25,165,824 | 98.123% | 0.172631 | 0.121975 | 0.975545 | phase3b_targeted_rerun |
| axpy | float32 | gcc-auto | 3145728 | 25,165,824 | 73.033% | 0.153669 | 0.0998497 | 0.535425 | phase3b_targeted_rerun |
| axpy | float64 | gcc-native | 2097152 | 33,554,432 | 72.635% | 0.292778 | 0.212812 | 1.10192 | phase3b_targeted_rerun |
| stencil_1d_three_point | float32 | gcc-native | 6291456 | 50,331,648 | 62.366% | 0.188764 | 0.182009 | 0.700188 | phase3b_targeted_rerun |
| stencil_1d_three_point | float32 | gcc-auto | 6291456 | 50,331,648 | 61.775% | 0.197816 | 0.187969 | 0.701427 | phase3b_targeted_rerun |
| stencil_1d_three_point | float32 | gcc-native | 8192 | 65,536 | 57.416% | 0.0520706 | 0.0518799 | 0.170135 | phase3b_targeted_rerun |
| axpy | float64 | gcc-native | 1048576 | 16,777,216 | 49.433% | 0.282907 | 0.205708 | 0.743961 | phase3b_targeted_rerun |
| axpy | float64 | gcc-native | 2621440 | 41,943,040 | 49.330% | 0.322399 | 0.234566 | 0.852242 | phase3b_targeted_rerun |
| axpy | float32 | gcc-native | 5242880 | 41,943,040 | 48.402% | 0.188684 | 0.147152 | 0.501499 | phase3b_targeted_rerun |
| stencil_1d_three_point | float32 | gcc-auto | 131072 | 1,048,576 | 46.164% | 0.0976562 | 0.0968933 | 0.267029 | phase3b_targeted_rerun |
| axpy | float64 | gcc-auto | 16384 | 262,144 | 44.866% | 0.138664 | 0.138474 | 0.370407 | phase3b_targeted_rerun |
| axpy | float32 | gcc-auto | 6291456 | 50,331,648 | 41.782% | 0.260083 | 0.211684 | 0.590626 | phase3b_targeted_rerun |
| dot_product | float64 | gcc-scalar | 3145728 | 50,331,648 | 37.152% | 0.465631 | 0.411987 | 1.0766 | phase3_raw_v3_original |
| axpy | float32 | gcc-auto | 5242880 | 41,943,040 | 36.957% | 0.166521 | 0.130501 | 0.370941 | phase3_raw_v3_original |
| axpy | float64 | gcc-native | 4194304 | 67,108,864 | 36.781% | 0.448394 | 0.362563 | 1.01335 | phase3_raw_v3_original |
| axpy | float32 | gcc-scalar | 131072 | 1,048,576 | 35.919% | 0.186157 | 0.183868 | 0.421906 | phase3b_targeted_rerun |
| axpy | float32 | gcc-scalar | 5242880 | 41,943,040 | 35.426% | 0.226269 | 0.208912 | 0.507221 | phase3_raw_v3_original |
| axpy | float64 | gcc-native | 1572864 | 25,165,824 | 35.182% | 0.136375 | 0.117938 | 0.28801 | phase3_raw_v3_original |
| dot_product | float64 | gcc-native | 1536 | 24,576 | 35.147% | 0.349426 | 0.343831 | 0.791423 | phase3_raw_v3_original |
| axpy | float32 | gcc-auto | 4194304 | 33,554,432 | 35.081% | 0.218856 | 0.128651 | 0.345421 | phase3b_targeted_rerun |
| stencil_1d_three_point | float32 | gcc-scalar | 5242880 | 41,943,040 | 35.069% | 0.361843 | 0.305233 | 0.802364 | phase3_raw_v3_original |
| axpy | float32 | gcc-auto | 8192 | 65,536 | 34.466% | 0.0553131 | 0.0545502 | 0.123596 | phase3_raw_v3_original |
| axpy | float64 | gcc-auto | 2621440 | 41,943,040 | 34.357% | 0.397358 | 0.32341 | 0.866394 | phase3b_targeted_rerun |
| dot_product | float64 | gcc-auto | 3145728 | 50,331,648 | 34.126% | 0.439962 | 0.380262 | 0.941594 | phase3_raw_v3_original |
| axpy | float64 | gcc-native | 3145728 | 50,331,648 | 33.947% | 0.334835 | 0.286261 | 0.694784 | phase3_raw_v3_original |
| elementwise_multiply | float32 | gcc-auto | 8388608 | 100,663,296 | 33.890% | 0.387812 | 0.326025 | 0.785542 | phase3_raw_v3_original |
| elementwise_multiply | float64 | gcc-auto | 2796202 | 67,108,864 | 33.600% | 0.745046 | 0.64584 | 1.60646 | phase3b_targeted_rerun |
| axpy | float64 | gcc-auto | 3145728 | 50,331,648 | 33.504% | 0.41124 | 0.3081 | 0.817076 | phase3_raw_v3_original |
| elementwise_multiply | float32 | gcc-native | 2097152 | 25,165,824 | 33.493% | 0.0713587 | 0.0688076 | 0.146294 | phase3_raw_v3_original |
