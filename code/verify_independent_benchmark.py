#!/usr/bin/env python3
from fractions import Fraction as F
from itertools import product
import json

# Nasseri et al. (2012), Example 4.2, center-spread triangular representation.
A = [
    [F(19), F(12), F(6)],
    [F(2), F(4), F(3,2)],
    [F(2), F(2), F(9,2)],
]
M = [
    [F(1), F(3,2), F(1,2)],
    [F(1,10), F(1,10), F(1,5)],
    [F(1,10), F(1,10), F(1,10)],
]
N = [
    [F(1), F(3,2), F(1,5)],
    [F(1,10), F(2,5), F(1,5)],
    [F(1,5), F(3,10), F(1,10)],
]
b = [F(1897), F(869,2), F(1071,2)]
h = [F(4277,10), F(381,5), F(883,10)]
g = [F(2681,5), F(1093,10), F(1319,10)]

x = [F(37), F(62), F(75)]
y = [F(7), F(11,2), F(51,5)]
z = [F(838,63), F(577,126), F(13154,945)]

def det3(B):
    return (B[0][0]*(B[1][1]*B[2][2]-B[1][2]*B[2][1])
           -B[0][1]*(B[1][0]*B[2][2]-B[1][2]*B[2][0])
           +B[0][2]*(B[1][0]*B[2][1]-B[1][1]*B[2][0]))

def matvec(B, v):
    return [sum(B[i][j]*v[j] for j in range(len(v))) for i in range(len(B))]

def add(u,v): return [a+b for a,b in zip(u,v)]

def tfn_from_center_spread(c,l,r):
    return (c-l,c,c+r)

def cut_tfn(t, alpha):
    L,C,U=t
    return (L + alpha*(C-L), U - alpha*(U-C))

def interval_product(I,J):
    vals=[I[0]*J[0], I[0]*J[1], I[1]*J[0], I[1]*J[1]]
    return (min(vals),max(vals))

def interval_sum(items):
    return (sum(v[0] for v in items), sum(v[1] for v in items))

assert det3(A) == 189
assert matvec(A,x) == b
assert add(matvec(A,y),matvec(M,x)) == h
assert add(matvec(A,z),matvec(N,x)) == g
assert all(xi-yi >= 0 for xi,yi in zip(x,y))
assert all(v >= 0 for v in x+y+z)

alpha=F(1,2)
# Row 1 coefficient TFNs and unknown TFNs.
coefs=[tfn_from_center_spread(A[0][j],M[0][j],N[0][j]) for j in range(3)]
unks=[tfn_from_center_spread(x[j],y[j],z[j]) for j in range(3)]
lhs=interval_sum([interval_product(cut_tfn(coefs[j],alpha),cut_tfn(unks[j],alpha)) for j in range(3)])
rhs=cut_tfn(tfn_from_center_spread(b[0],h[0],g[0]),alpha)
assert lhs == (F(135059,80), F(164115401,75600))
assert rhs == (F(33663,20), F(21651,10))
assert lhs != rhs

out={
 "det_A": str(det3(A)),
 "x": [str(v) for v in x],
 "y": [str(v) for v in y],
 "z": [str(v) for v in z],
 "positive_support": True,
 "alpha": "1/2",
 "row1_EP_LHS_exact": [str(lhs[0]),str(lhs[1])],
 "row1_EP_LHS_decimal": [float(lhs[0]),float(lhs[1])],
 "row1_RHS_cut_exact": [str(rhs[0]),str(rhs[1])],
 "row1_RHS_cut_decimal": [float(rhs[0]),float(rhs[1])],
 "same_cut": False,
 "anchor_cardinality": 1,
 "pairwise_anchor_EP_core_cardinality": 0,
 "claim": "unique associated-system anchor is excluded from exact extension-principle equality"
}
print(json.dumps(out,indent=2))
