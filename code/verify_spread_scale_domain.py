#!/usr/bin/env python3
"""Verify the PAI spread-scale solution-support and positive-input-domain thresholds."""
import argparse, json
from pathlib import Path
import numpy as np

ap=argparse.ArgumentParser()
ap.add_argument('results_json', type=Path)
ap.add_argument('--out', type=Path)
a=ap.parse_args()
D=json.loads(a.results_json.read_text())['primary']
A=np.array(D['A'],float); M=np.array(D['M'],float)
b=np.array(D['b'],float); h=np.array(D['h'],float)
x=np.array(D['x'],float)
yM=np.array(D['M_solution']['y'],float); yT=np.array(D['TA_solution']['y'],float)

def sol_thr(y):
    vals=[x[i]/y[i] for i in range(len(x)) if y[i]>0]
    return min(vals) if vals else float('inf')

rho_M_sol=float(sol_thr(yM)); rho_TA_sol=float(sol_thr(yT))
rho_A=float(np.min((A/M)[M>0]))
rho_b=float(np.min((b/h)[h>0]))
rho_in=min(rho_A,rho_b)
out={
    'rho_TA_solution_support':rho_TA_sol,
    'rho_M_solution_support':rho_M_sol,
    'rho_input_coefficient_side':rho_A,
    'rho_input_rhs_side':rho_b,
    'rho_input_domain':rho_in,
    'rho_TA_valid_positive_model':min(rho_TA_sol,rho_in),
    'rho_M_valid_positive_model':min(rho_M_sol,rho_in),
    'primary_rho':1.0,
}
# Locked regression values from the full-precision primary PAI replay.
assert abs(out['rho_TA_solution_support']-0.5107362661540621)<1e-12
assert abs(out['rho_M_solution_support']-2.1826396942801725)<1e-12
assert abs(out['rho_input_domain']-2.0954925900630714)<1e-12
assert out['rho_TA_valid_positive_model'] < 1 < out['rho_M_valid_positive_model']
text=json.dumps(out,indent=2)
print(text)
if a.out:
    a.out.write_text(text+'\n',encoding='utf-8')
