# pdaggerq - A code for bringing strings of creation / annihilation operators to normal order.
# Copyright (C) 2020 A. Eugene DePrince III
#
# This file is part of the pdaggerq package.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
spin-orbital CCSD amplitude equations
"""
import numpy as np
from numpy import einsum

def coupled_cluster_energy(t1, t2, f, g, o, v):

    #    < 0 | e(-T) H e(T) | 0> :
    
    #	  1.0000 f(i,i)
    energy =  1.000000000000000 * einsum('ii', f[o, o])
    
    #	  1.0000 f(i,a)*t1(a,i)
    energy +=  1.000000000000000 * einsum('ia,ai', f[o, v], t1)
    
    #	 -0.5000 <j,i||j,i>
    energy += -0.500000000000000 * einsum('jiji', g[o, o, o, o])
    
    #	  0.2500 <j,i||a,b>*t2(a,b,j,i)
    energy +=  0.250000000000000 * einsum('jiab,abji', g[o, o, v, v], t2)
    
    #	 -0.5000 <j,i||a,b>*t1(a,i)*t1(b,j)
    energy += -0.500000000000000 * einsum('jiab,ai,bj', g[o, o, v, v], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])

    return energy
    
def ccsd_singles_residual(t1, t2, f, g, o, v):
    
    #    < 0 | m* e e(-T) H e(T) | 0> :
    
    #	  1.0000 f(e,m)
    singles_res =  1.000000000000000 * einsum('em->em', f[v, o])
    
    #	 -1.0000 f(i,m)*t1(e,i)
    singles_res += -1.000000000000000 * einsum('im,ei->em', f[o, o], t1)
    
    #	  1.0000 f(e,a)*t1(a,m)
    singles_res +=  1.000000000000000 * einsum('ea,am->em', f[v, v], t1)
    
    #	 -1.0000 f(i,a)*t2(a,e,m,i)
    singles_res += -1.000000000000000 * einsum('ia,aemi->em', f[o, v], t2)
    
    #	 -1.0000 f(i,a)*t1(a,m)*t1(e,i)
    singles_res += -1.000000000000000 * einsum('ia,am,ei->em', f[o, v], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	  1.0000 <i,e||a,m>*t1(a,i)
    singles_res +=  1.000000000000000 * einsum('ieam,ai->em', g[o, v, v, o], t1)
    
    #	 -0.5000 <j,i||a,m>*t2(a,e,j,i)
    singles_res += -0.500000000000000 * einsum('jiam,aeji->em', g[o, o, v, o], t2)
    
    #	 -0.5000 <i,e||a,b>*t2(a,b,m,i)
    singles_res += -0.500000000000000 * einsum('ieab,abmi->em', g[o, v, v, v], t2)
    
    #	  1.0000 <j,i||a,b>*t1(a,i)*t2(b,e,m,j)
    singles_res +=  1.000000000000000 * einsum('jiab,ai,bemj->em', g[o, o, v, v], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	  0.5000 <j,i||a,b>*t1(a,m)*t2(b,e,j,i)
    singles_res +=  0.500000000000000 * einsum('jiab,am,beji->em', g[o, o, v, v], t1, t2, optimize=['einsum_path', (0, 2), (0, 1)])
    
    #	  0.5000 <j,i||a,b>*t1(e,i)*t2(a,b,m,j)
    singles_res +=  0.500000000000000 * einsum('jiab,ei,abmj->em', g[o, o, v, v], t1, t2, optimize=['einsum_path', (0, 2), (0, 1)])
    
    #	  1.0000 <j,i||a,m>*t1(a,i)*t1(e,j)
    singles_res +=  1.000000000000000 * einsum('jiam,ai,ej->em', g[o, o, v, o], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	  1.0000 <i,e||a,b>*t1(a,i)*t1(b,m)
    singles_res +=  1.000000000000000 * einsum('ieab,ai,bm->em', g[o, v, v, v], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	  1.0000 <j,i||a,b>*t1(a,i)*t1(b,m)*t1(e,j)
    singles_res +=  1.000000000000000 * einsum('jiab,ai,bm,ej->em', g[o, o, v, v], t1, t1, t1, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    return singles_res    

def ccsd_doubles_residual(t1, t2, f, g, o, v):
    
    #    < 0 | m* n* f e e(-T) H e(T) | 0> :
    
    #	 -1.0000 P(m,n)f(i,n)*t2(e,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('in,efmi->efmn', f[o, o], t2)
    doubles_res =  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	  1.0000 P(e,f)f(e,a)*t2(a,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ea,afmn->efmn', f[v, v], t2)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	 -1.0000 P(m,n)f(i,a)*t1(a,n)*t2(e,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('ia,an,efmi->efmn', f[o, v], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	 -1.0000 P(e,f)f(i,a)*t1(e,i)*t2(a,f,m,n)
    contracted_intermediate = -1.000000000000000 * einsum('ia,ei,afmn->efmn', f[o, v], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	  1.0000 <e,f||m,n>
    doubles_res +=  1.000000000000000 * einsum('efmn->efmn', g[v, v, o, o])
    
    #	  1.0000 P(e,f)<i,e||m,n>*t1(f,i)
    contracted_intermediate =  1.000000000000000 * einsum('iemn,fi->efmn', g[o, v, o, o], t1)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	  1.0000 P(m,n)<e,f||a,n>*t1(a,m)
    contracted_intermediate =  1.000000000000000 * einsum('efan,am->efmn', g[v, v, v, o], t1)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	  0.5000 <j,i||m,n>*t2(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jimn,efji->efmn', g[o, o, o, o], t2)
    
    #	  1.0000 P(m,n)*P(e,f)<i,e||a,n>*t2(a,f,m,i)
    contracted_intermediate =  1.000000000000000 * einsum('iean,afmi->efmn', g[o, v, v, o], t2)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate) 
    
    #	  0.5000 <e,f||a,b>*t2(a,b,m,n)
    doubles_res +=  0.500000000000000 * einsum('efab,abmn->efmn', g[v, v, v, v], t2)
    
    #	  1.0000 P(m,n)<j,i||a,n>*t1(a,i)*t2(e,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jian,ai,efmj->efmn', g[o, o, v, o], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	  0.5000 P(m,n)<j,i||a,n>*t1(a,m)*t2(e,f,j,i)
    contracted_intermediate =  0.500000000000000 * einsum('jian,am,efji->efmn', g[o, o, v, o], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	 -1.0000 P(m,n)*P(e,f)<j,i||a,n>*t1(e,i)*t2(a,f,m,j)
    contracted_intermediate = -1.000000000000000 * einsum('jian,ei,afmj->efmn', g[o, o, v, o], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate) 
    
    #	  1.0000 P(e,f)<i,e||a,b>*t1(a,i)*t2(b,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ieab,ai,bfmn->efmn', g[o, v, v, v], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	 -1.0000 P(m,n)*P(e,f)<i,e||a,b>*t1(a,n)*t2(b,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('ieab,an,bfmi->efmn', g[o, v, v, v], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate) 
    
    #	  0.5000 P(e,f)<i,e||a,b>*t1(f,i)*t2(a,b,m,n)
    contracted_intermediate =  0.500000000000000 * einsum('ieab,fi,abmn->efmn', g[o, v, v, v], t1, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	 -1.0000 <j,i||m,n>*t1(e,i)*t1(f,j)
    doubles_res += -1.000000000000000 * einsum('jimn,ei,fj->efmn', g[o, o, o, o], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	  1.0000 P(m,n)*P(e,f)<i,e||a,n>*t1(a,m)*t1(f,i)
    contracted_intermediate =  1.000000000000000 * einsum('iean,am,fi->efmn', g[o, v, v, o], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate) 
    
    #	 -1.0000 <e,f||a,b>*t1(a,n)*t1(b,m)
    doubles_res += -1.000000000000000 * einsum('efab,an,bm->efmn', g[v, v, v, v], t1, t1, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	 -0.5000 P(m,n)<j,i||a,b>*t2(a,b,n,i)*t2(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('jiab,abni,efmj->efmn', g[o, o, v, v], t2, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	  0.2500 <j,i||a,b>*t2(a,b,m,n)*t2(e,f,j,i)
    doubles_res +=  0.250000000000000 * einsum('jiab,abmn,efji->efmn', g[o, o, v, v], t2, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	 -0.5000 <j,i||a,b>*t2(a,e,j,i)*t2(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiab,aeji,bfmn->efmn', g[o, o, v, v], t2, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    
    #	  1.0000 P(m,n)<j,i||a,b>*t2(a,e,n,i)*t2(b,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,aeni,bfmj->efmn', g[o, o, v, v], t2, t2, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	 -0.5000 <j,i||a,b>*t2(a,e,m,n)*t2(b,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiab,aemn,bfji->efmn', g[o, o, v, v], t2, t2, optimize=['einsum_path', (0, 2), (0, 1)])
    
    #	  1.0000 P(m,n)<j,i||a,b>*t1(a,i)*t1(b,n)*t2(e,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,ai,bn,efmj->efmn', g[o, o, v, v], t1, t1, t2, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	  1.0000 P(e,f)<j,i||a,b>*t1(a,i)*t1(e,j)*t2(b,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,ai,ej,bfmn->efmn', g[o, o, v, v], t1, t1, t2, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	 -0.5000 <j,i||a,b>*t1(a,n)*t1(b,m)*t2(e,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiab,an,bm,efji->efmn', g[o, o, v, v], t1, t1, t2, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    
    #	  1.0000 P(m,n)*P(e,f)<j,i||a,b>*t1(a,n)*t1(e,i)*t2(b,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,an,ei,bfmj->efmn', g[o, o, v, v], t1, t1, t2, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate) 
    
    #	 -0.5000 <j,i||a,b>*t1(e,i)*t1(f,j)*t2(a,b,m,n)
    doubles_res += -0.500000000000000 * einsum('jiab,ei,fj,abmn->efmn', g[o, o, v, v], t1, t1, t2, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    
    #	 -1.0000 P(m,n)<j,i||a,n>*t1(a,m)*t1(e,i)*t1(f,j)
    contracted_intermediate = -1.000000000000000 * einsum('jian,am,ei,fj->efmn', g[o, o, v, o], t1, t1, t1, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate) 
    
    #	 -1.0000 P(e,f)<i,e||a,b>*t1(a,n)*t1(b,m)*t1(f,i)
    contracted_intermediate = -1.000000000000000 * einsum('ieab,an,bm,fi->efmn', g[o, v, v, v], t1, t1, t1, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate) 
    
    #	  1.0000 <j,i||a,b>*t1(a,n)*t1(b,m)*t1(e,i)*t1(f,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,an,bm,ei,fj->efmn', g[o, o, v, v], t1, t1, t1, t1, optimize=['einsum_path', (0, 1), (0, 3), (0, 2), (0, 1)])
    
    return doubles_res

def ccsd_iterations_with_spin(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, 
        oa, ob, va, vb, e_aa_ai, e_bb_ai, e_aaaa_abij, e_bbbb_abij, e_abab_abij, hf_energy, max_iter=500, 
        e_convergence=1e-8,r_convergence=1e-8,diis_size=None, diis_start_cycle=4):
           

    # initialize diis if diis_size is not None
    # else normal scf iterate

    if diis_size is not None:
        from diis import DIIS
        diis_update = DIIS(diis_size, start_iter=diis_start_cycle)
        t1_aa_end = t1_aa.size
        t1_bb_end = t1_aa_end + t1_bb.size
        t2_aaaa_end = t1_bb_end + t2_aaaa.size
        t2_bbbb_end = t2_aaaa_end + t2_bbbb.size
        t2_abab_end = t2_bbbb_end + t2_abab.size
        old_vec = np.hstack((t1_aa.flatten(), t1_bb.flatten(), t2_aaaa.flatten(), t2_bbbb.flatten(), t2_abab.flatten()))

    fock_e_aa_ai = np.reciprocal(e_aa_ai)
    fock_e_bb_ai = np.reciprocal(e_bb_ai)

    fock_e_aaaa_abij = np.reciprocal(e_aaaa_abij)
    fock_e_bbbb_abij = np.reciprocal(e_bbbb_abij)
    fock_e_abab_abij = np.reciprocal(e_abab_abij)

    old_energy = ccsd_energy_with_spin(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)

    print("")
    print("    ==> CCSD amplitude equations <==")
    print("")
    print("     Iter               Energy                 |dE|                 |dT|")
    for idx in range(max_iter):

        residual_t1_aa = ccsd_t1_aa_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)
        residual_t1_bb = ccsd_t1_bb_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)

        residual_t2_aaaa = ccsd_t2_aaaa_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)
        residual_t2_bbbb = ccsd_t2_bbbb_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)
        residual_t2_abab = ccsd_t2_abab_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)

        res_norm = ( np.linalg.norm(residual_t1_aa)
                   + np.linalg.norm(residual_t1_bb)
                   + np.linalg.norm(residual_t2_aaaa)
                   + np.linalg.norm(residual_t2_bbbb)
                   + np.linalg.norm(residual_t2_abab) )

        t1_aa_res = residual_t1_aa + fock_e_aa_ai * t1_aa
        t1_bb_res = residual_t1_bb + fock_e_bb_ai * t1_bb

        t2_aaaa_res = residual_t2_aaaa + fock_e_aaaa_abij * t2_aaaa
        t2_bbbb_res = residual_t2_bbbb + fock_e_bbbb_abij * t2_bbbb
        t2_abab_res = residual_t2_abab + fock_e_abab_abij * t2_abab

        new_t1_aa = t1_aa_res * e_aa_ai
        new_t1_bb = t1_bb_res * e_bb_ai

        new_t2_aaaa = t2_aaaa_res * e_aaaa_abij
        new_t2_bbbb = t2_bbbb_res * e_bbbb_abij
        new_t2_abab = t2_abab_res * e_abab_abij

        # diis update
        if diis_size is not None:
            vectorized_iterate = np.hstack(
                (new_t1_aa.flatten(), new_t1_bb.flatten(), new_t2_aaaa.flatten(), new_t2_bbbb.flatten(), new_t2_abab.flatten()))
            error_vec = old_vec - vectorized_iterate
            new_vectorized_iterate = diis_update.compute_new_vec(vectorized_iterate,
                                                                 error_vec)
            new_t1_aa = new_vectorized_iterate[:t1_aa_end].reshape(t1_aa.shape)
            new_t1_bb = new_vectorized_iterate[t1_aa_end:t1_bb_end].reshape(t1_bb.shape)

            new_t2_aaaa = new_vectorized_iterate[t1_bb_end:t2_aaaa_end].reshape(t2_aaaa.shape)
            new_t2_bbbb = new_vectorized_iterate[t2_aaaa_end:t2_bbbb_end].reshape(t2_bbbb.shape)
            new_t2_abab = new_vectorized_iterate[t2_bbbb_end:t2_abab_end].reshape(t2_abab.shape)

            old_vec = new_vectorized_iterate

        current_energy = ccsd_energy_with_spin(new_t1_aa, new_t1_bb, new_t2_aaaa, new_t2_bbbb, new_t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb)

        delta_e = np.abs(old_energy - current_energy)

        print("    {: 5d} {: 20.12f} {: 20.12f} {: 20.12f}".format(idx, current_energy - hf_energy, delta_e, res_norm))
        if delta_e < e_convergence and res_norm < r_convergence:
            # assign t1 and t2 variables for future use before breaking
            t1_aa = new_t1_aa
            t1_bb = new_t1_bb

            t2_aaaa = new_t2_aaaa
            t2_bbbb = new_t2_bbbb
            t2_abab = new_t2_abab
            break
        else:
            # assign t1 and t2 and old_energy for next iteration
            t1_aa = new_t1_aa
            t1_bb = new_t1_bb

            t2_aaaa = new_t2_aaaa
            t2_bbbb = new_t2_bbbb
            t2_abab = new_t2_abab
            old_energy = current_energy

    else:
        raise ValueError("CCSD iterations did not converge")


    return t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab

def ccsd_iterations(t1, t2, fock, g, o, v, e_ai, e_abij, hf_energy, max_iter=500, 
        e_convergence=1e-8,r_convergence=1e-8,diis_size=None, diis_start_cycle=4):
           

    # initialize diis if diis_size is not None
    # else normal scf iterate

    if diis_size is not None:
        from diis import DIIS
        diis_update = DIIS(diis_size, start_iter=diis_start_cycle)
        t1_dim = t1.size
        old_vec = np.hstack((t1.flatten(), t2.flatten()))

    fock_e_ai = np.reciprocal(e_ai)
    fock_e_abij = np.reciprocal(e_abij)
    old_energy = coupled_cluster_energy(t1, t2, fock, g, o, v)

    print("")
    print("    ==> CCSD amplitude equations <==")
    print("")
    print("     Iter               Energy                 |dE|                 |dT|")
    for idx in range(max_iter):

        residual_singles = ccsd_singles_residual(t1, t2, fock, g, o, v)
        residual_doubles = ccsd_doubles_residual(t1, t2, fock, g, o, v)

        res_norm = np.linalg.norm(residual_singles) + np.linalg.norm(residual_doubles)

        singles_res = residual_singles + fock_e_ai * t1
        doubles_res = residual_doubles + fock_e_abij * t2

        new_singles = singles_res * e_ai
        new_doubles = doubles_res * e_abij

        # diis update
        if diis_size is not None:
            vectorized_iterate = np.hstack(
                (new_singles.flatten(), new_doubles.flatten()))
            error_vec = old_vec - vectorized_iterate
            new_vectorized_iterate = diis_update.compute_new_vec(vectorized_iterate,
                                                                 error_vec)
            new_singles = new_vectorized_iterate[:t1_dim].reshape(t1.shape)
            new_doubles = new_vectorized_iterate[t1_dim:].reshape(t2.shape)
            old_vec = new_vectorized_iterate

        current_energy = coupled_cluster_energy(new_singles, new_doubles, fock, g, o, v)
        delta_e = np.abs(old_energy - current_energy)

        print("    {: 5d} {: 20.12f} {: 20.12f} {: 20.12f}".format(idx, current_energy - hf_energy, delta_e, res_norm))
        if delta_e < e_convergence and res_norm < r_convergence:
            # assign t1 and t2 variables for future use before breaking
            t1 = new_singles
            t2 = new_doubles
            break
        else:
            # assign t1 and t2 and old_energy for next iteration
            t1 = new_singles
            t2 = new_doubles
            old_energy = current_energy

    else:
        raise ValueError("CCSD iterations did not converge")


    return t1, t2


def ccsd_energy_with_spin(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb):

    #    < 0 | e(-T) H e(T) | 0> :

    #	  1.0000 f_aa(i,i)
    energy  =  1.000000000000000 * einsum('ii', f_aa[oa, oa])

    #	  1.0000 f_bb(i,i)
    energy +=  1.000000000000000 * einsum('ii', f_bb[ob, ob])

    #	  1.0000 f_aa(i,a)*t1_aa(a,i)
    energy +=  1.000000000000000 * einsum('ia,ai', f_aa[oa, va], t1_aa)

    #	  1.0000 f_bb(i,a)*t1_bb(a,i)
    energy +=  1.000000000000000 * einsum('ia,ai', f_bb[ob, vb], t1_bb)

    #	 -0.5000 <j,i||j,i>_aaaa
    energy += -0.500000000000000 * einsum('jiji', g_aaaa[oa, oa, oa, oa])

    #	 -0.5000 <j,i||j,i>_abab
    energy += -0.500000000000000 * einsum('jiji', g_abab[oa, ob, oa, ob])

    #	 -0.5000 <i,j||i,j>_abab
    energy += -0.500000000000000 * einsum('ijij', g_abab[oa, ob, oa, ob])

    #	 -0.5000 <j,i||j,i>_bbbb
    energy += -0.500000000000000 * einsum('jiji', g_bbbb[ob, ob, ob, ob])

    #	  0.2500 <j,i||a,b>_aaaa*t2_aaaa(a,b,j,i)
    energy +=  0.250000000000000 * einsum('jiab,abji', g_aaaa[oa, oa, va, va], t2_aaaa)

    #	  0.2500 <j,i||a,b>_abab*t2_abab(a,b,j,i)
    energy +=  0.250000000000000 * einsum('jiab,abji', g_abab[oa, ob, va, vb], t2_abab)

    #	  0.2500 <i,j||a,b>_abab*t2_abab(a,b,i,j)
    energy +=  0.250000000000000 * einsum('ijab,abij', g_abab[oa, ob, va, vb], t2_abab)

    #	  0.2500 <j,i||b,a>_abab*t2_abab(b,a,j,i)
    energy +=  0.250000000000000 * einsum('jiba,baji', g_abab[oa, ob, va, vb], t2_abab)

    #	  0.2500 <i,j||b,a>_abab*t2_abab(b,a,i,j)
    energy +=  0.250000000000000 * einsum('ijba,baij', g_abab[oa, ob, va, vb], t2_abab)

    #	  0.2500 <j,i||a,b>_bbbb*t2_bbbb(a,b,j,i)
    energy +=  0.250000000000000 * einsum('jiab,abji', g_bbbb[ob, ob, vb, vb], t2_bbbb)

    #	 -0.5000 <j,i||a,b>_aaaa*t1_aa(a,i)*t1_aa(b,j)
    energy += -0.500000000000000 * einsum('jiab,ai,bj', g_aaaa[oa, oa, va, va], t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <i,j||a,b>_abab*t1_aa(a,i)*t1_bb(b,j)
    energy +=  0.500000000000000 * einsum('ijab,ai,bj', g_abab[oa, ob, va, vb], t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <j,i||b,a>_abab*t1_bb(a,i)*t1_aa(b,j)
    energy +=  0.500000000000000 * einsum('jiba,ai,bj', g_abab[oa, ob, va, vb], t1_bb, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_bbbb*t1_bb(a,i)*t1_bb(b,j)
    energy += -0.500000000000000 * einsum('jiab,ai,bj', g_bbbb[ob, ob, vb, vb], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    return energy


def ccsd_t1_aa_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb):

    #    < 0 | m* e e(-T) H e(T) | 0> :

    #	  1.0000 f_aa(e,m)
    singles_res  =  1.000000000000000 * einsum('em->em', f_aa[va, oa])

    #	 -1.0000 f_aa(i,m)*t1_aa(e,i)
    singles_res += -1.000000000000000 * einsum('im,ei->em', f_aa[oa, oa], t1_aa)

    #	  1.0000 f_aa(e,a)*t1_aa(a,m)
    singles_res +=  1.000000000000000 * einsum('ea,am->em', f_aa[va, va], t1_aa)

    #	 -1.0000 f_aa(i,a)*t2_aaaa(a,e,m,i)
    singles_res += -1.000000000000000 * einsum('ia,aemi->em', f_aa[oa, va], t2_aaaa)

    #	  1.0000 f_bb(i,a)*t2_abab(e,a,m,i)
    singles_res +=  1.000000000000000 * einsum('ia,eami->em', f_bb[ob, vb], t2_abab)

    #	 -1.0000 f_aa(i,a)*t1_aa(a,m)*t1_aa(e,i)
    singles_res += -1.000000000000000 * einsum('ia,am,ei->em', f_aa[oa, va], t1_aa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 <i,e||a,m>_aaaa*t1_aa(a,i)
    singles_res +=  1.000000000000000 * einsum('ieam,ai->em', g_aaaa[oa, va, va, oa], t1_aa)

    #	  1.0000 <e,i||m,a>_abab*t1_bb(a,i)
    singles_res +=  1.000000000000000 * einsum('eima,ai->em', g_abab[va, ob, oa, vb], t1_bb)

    #	 -0.5000 <j,i||a,m>_aaaa*t2_aaaa(a,e,j,i)
    singles_res += -0.500000000000000 * einsum('jiam,aeji->em', g_aaaa[oa, oa, va, oa], t2_aaaa)

    #	 -0.5000 <j,i||m,a>_abab*t2_abab(e,a,j,i)
    singles_res += -0.500000000000000 * einsum('jima,eaji->em', g_abab[oa, ob, oa, vb], t2_abab)

    #	 -0.5000 <i,j||m,a>_abab*t2_abab(e,a,i,j)
    singles_res += -0.500000000000000 * einsum('ijma,eaij->em', g_abab[oa, ob, oa, vb], t2_abab)

    #	 -0.5000 <i,e||a,b>_aaaa*t2_aaaa(a,b,m,i)
    singles_res += -0.500000000000000 * einsum('ieab,abmi->em', g_aaaa[oa, va, va, va], t2_aaaa)

    #	  0.5000 <e,i||a,b>_abab*t2_abab(a,b,m,i)
    singles_res +=  0.500000000000000 * einsum('eiab,abmi->em', g_abab[va, ob, va, vb], t2_abab)

    #	  0.5000 <e,i||b,a>_abab*t2_abab(b,a,m,i)
    singles_res +=  0.500000000000000 * einsum('eiba,bami->em', g_abab[va, ob, va, vb], t2_abab)

    #	  1.0000 <j,i||a,b>_aaaa*t1_aa(a,i)*t2_aaaa(b,e,m,j)
    singles_res +=  1.000000000000000 * einsum('jiab,ai,bemj->em', g_aaaa[oa, oa, va, va], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,j||a,b>_abab*t1_aa(a,i)*t2_abab(e,b,m,j)
    singles_res +=  1.000000000000000 * einsum('ijab,ai,ebmj->em', g_abab[oa, ob, va, vb], t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <j,i||b,a>_abab*t1_bb(a,i)*t2_aaaa(b,e,m,j)
    singles_res += -1.000000000000000 * einsum('jiba,ai,bemj->em', g_abab[oa, ob, va, vb], t1_bb, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <j,i||a,b>_bbbb*t1_bb(a,i)*t2_abab(e,b,m,j)
    singles_res += -1.000000000000000 * einsum('jiab,ai,ebmj->em', g_bbbb[ob, ob, vb, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <j,i||a,b>_aaaa*t1_aa(a,m)*t2_aaaa(b,e,j,i)
    singles_res +=  0.500000000000000 * einsum('jiab,am,beji->em', g_aaaa[oa, oa, va, va], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <j,i||a,b>_abab*t1_aa(a,m)*t2_abab(e,b,j,i)
    singles_res += -0.500000000000000 * einsum('jiab,am,ebji->em', g_abab[oa, ob, va, vb], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <i,j||a,b>_abab*t1_aa(a,m)*t2_abab(e,b,i,j)
    singles_res += -0.500000000000000 * einsum('ijab,am,ebij->em', g_abab[oa, ob, va, vb], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <j,i||a,b>_aaaa*t2_aaaa(a,b,m,j)*t1_aa(e,i)
    singles_res +=  0.500000000000000 * einsum('jiab,abmj,ei->em', g_aaaa[oa, oa, va, va], t2_aaaa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <i,j||a,b>_abab*t2_abab(a,b,m,j)*t1_aa(e,i)
    singles_res += -0.500000000000000 * einsum('ijab,abmj,ei->em', g_abab[oa, ob, va, vb], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <i,j||b,a>_abab*t2_abab(b,a,m,j)*t1_aa(e,i)
    singles_res += -0.500000000000000 * einsum('ijba,bamj,ei->em', g_abab[oa, ob, va, vb], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,m>_aaaa*t1_aa(a,i)*t1_aa(e,j)
    singles_res +=  1.000000000000000 * einsum('jiam,ai,ej->em', g_aaaa[oa, oa, va, oa], t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <j,i||m,a>_abab*t1_bb(a,i)*t1_aa(e,j)
    singles_res += -1.000000000000000 * einsum('jima,ai,ej->em', g_abab[oa, ob, oa, vb], t1_bb, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,e||a,b>_aaaa*t1_aa(a,i)*t1_aa(b,m)
    singles_res +=  1.000000000000000 * einsum('ieab,ai,bm->em', g_aaaa[oa, va, va, va], t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <e,i||b,a>_abab*t1_bb(a,i)*t1_aa(b,m)
    singles_res +=  1.000000000000000 * einsum('eiba,ai,bm->em', g_abab[va, ob, va, vb], t1_bb, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,b>_aaaa*t1_aa(a,i)*t1_aa(b,m)*t1_aa(e,j)
    singles_res +=  1.000000000000000 * einsum('jiab,ai,bm,ej->em', g_aaaa[oa, oa, va, va], t1_aa, t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	 -1.0000 <j,i||b,a>_abab*t1_bb(a,i)*t1_aa(b,m)*t1_aa(e,j)
    singles_res += -1.000000000000000 * einsum('jiba,ai,bm,ej->em', g_abab[oa, ob, va, vb], t1_bb, t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    return singles_res


def ccsd_t1_bb_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb):

    #    < 0 | m* e e(-T) H e(T) | 0> :

    #	  1.0000 f_bb(e,m)
    singles_res  =  1.000000000000000 * einsum('em->em', f_bb[vb, ob])

    #	 -1.0000 f_bb(i,m)*t1_bb(e,i)
    singles_res += -1.000000000000000 * einsum('im,ei->em', f_bb[ob, ob], t1_bb)

    #	  1.0000 f_bb(e,a)*t1_bb(a,m)
    singles_res +=  1.000000000000000 * einsum('ea,am->em', f_bb[vb, vb], t1_bb)

    #	  1.0000 f_aa(i,a)*t2_abab(a,e,i,m)
    singles_res +=  1.000000000000000 * einsum('ia,aeim->em', f_aa[oa, va], t2_abab)

    #	 -1.0000 f_bb(i,a)*t2_bbbb(a,e,m,i)
    singles_res += -1.000000000000000 * einsum('ia,aemi->em', f_bb[ob, vb], t2_bbbb)

    #	 -1.0000 f_bb(i,a)*t1_bb(a,m)*t1_bb(e,i)
    singles_res += -1.000000000000000 * einsum('ia,am,ei->em', f_bb[ob, vb], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,e||a,m>_abab*t1_aa(a,i)
    singles_res +=  1.000000000000000 * einsum('ieam,ai->em', g_abab[oa, vb, va, ob], t1_aa)

    #	  1.0000 <i,e||a,m>_bbbb*t1_bb(a,i)
    singles_res +=  1.000000000000000 * einsum('ieam,ai->em', g_bbbb[ob, vb, vb, ob], t1_bb)

    #	 -0.5000 <j,i||a,m>_abab*t2_abab(a,e,j,i)
    singles_res += -0.500000000000000 * einsum('jiam,aeji->em', g_abab[oa, ob, va, ob], t2_abab)

    #	 -0.5000 <i,j||a,m>_abab*t2_abab(a,e,i,j)
    singles_res += -0.500000000000000 * einsum('ijam,aeij->em', g_abab[oa, ob, va, ob], t2_abab)

    #	 -0.5000 <j,i||a,m>_bbbb*t2_bbbb(a,e,j,i)
    singles_res += -0.500000000000000 * einsum('jiam,aeji->em', g_bbbb[ob, ob, vb, ob], t2_bbbb)

    #	  0.5000 <i,e||a,b>_abab*t2_abab(a,b,i,m)
    singles_res +=  0.500000000000000 * einsum('ieab,abim->em', g_abab[oa, vb, va, vb], t2_abab)

    #	  0.5000 <i,e||b,a>_abab*t2_abab(b,a,i,m)
    singles_res +=  0.500000000000000 * einsum('ieba,baim->em', g_abab[oa, vb, va, vb], t2_abab)

    #	 -0.5000 <i,e||a,b>_bbbb*t2_bbbb(a,b,m,i)
    singles_res += -0.500000000000000 * einsum('ieab,abmi->em', g_bbbb[ob, vb, vb, vb], t2_bbbb)

    #	 -1.0000 <j,i||a,b>_aaaa*t1_aa(a,i)*t2_abab(b,e,j,m)
    singles_res += -1.000000000000000 * einsum('jiab,ai,bejm->em', g_aaaa[oa, oa, va, va], t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,j||a,b>_abab*t1_aa(a,i)*t2_bbbb(b,e,m,j)
    singles_res += -1.000000000000000 * einsum('ijab,ai,bemj->em', g_abab[oa, ob, va, vb], t1_aa, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||b,a>_abab*t1_bb(a,i)*t2_abab(b,e,j,m)
    singles_res +=  1.000000000000000 * einsum('jiba,ai,bejm->em', g_abab[oa, ob, va, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,b>_bbbb*t1_bb(a,i)*t2_bbbb(b,e,m,j)
    singles_res +=  1.000000000000000 * einsum('jiab,ai,bemj->em', g_bbbb[ob, ob, vb, vb], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||b,a>_abab*t1_bb(a,m)*t2_abab(b,e,j,i)
    singles_res += -0.500000000000000 * einsum('jiba,am,beji->em', g_abab[oa, ob, va, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,j||b,a>_abab*t1_bb(a,m)*t2_abab(b,e,i,j)
    singles_res += -0.500000000000000 * einsum('ijba,am,beij->em', g_abab[oa, ob, va, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <j,i||a,b>_bbbb*t1_bb(a,m)*t2_bbbb(b,e,j,i)
    singles_res +=  0.500000000000000 * einsum('jiab,am,beji->em', g_bbbb[ob, ob, vb, vb], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_abab*t2_abab(a,b,j,m)*t1_bb(e,i)
    singles_res += -0.500000000000000 * einsum('jiab,abjm,ei->em', g_abab[oa, ob, va, vb], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||b,a>_abab*t2_abab(b,a,j,m)*t1_bb(e,i)
    singles_res += -0.500000000000000 * einsum('jiba,bajm,ei->em', g_abab[oa, ob, va, vb], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <j,i||a,b>_bbbb*t2_bbbb(a,b,m,j)*t1_bb(e,i)
    singles_res +=  0.500000000000000 * einsum('jiab,abmj,ei->em', g_bbbb[ob, ob, vb, vb], t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,j||a,m>_abab*t1_aa(a,i)*t1_bb(e,j)
    singles_res += -1.000000000000000 * einsum('ijam,ai,ej->em', g_abab[oa, ob, va, ob], t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,m>_bbbb*t1_bb(a,i)*t1_bb(e,j)
    singles_res +=  1.000000000000000 * einsum('jiam,ai,ej->em', g_bbbb[ob, ob, vb, ob], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,e||a,b>_abab*t1_aa(a,i)*t1_bb(b,m)
    singles_res +=  1.000000000000000 * einsum('ieab,ai,bm->em', g_abab[oa, vb, va, vb], t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,e||a,b>_bbbb*t1_bb(a,i)*t1_bb(b,m)
    singles_res +=  1.000000000000000 * einsum('ieab,ai,bm->em', g_bbbb[ob, vb, vb, vb], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,j||a,b>_abab*t1_aa(a,i)*t1_bb(b,m)*t1_bb(e,j)
    singles_res += -1.000000000000000 * einsum('ijab,ai,bm,ej->em', g_abab[oa, ob, va, vb], t1_aa, t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_bbbb*t1_bb(a,i)*t1_bb(b,m)*t1_bb(e,j)
    singles_res +=  1.000000000000000 * einsum('jiab,ai,bm,ej->em', g_bbbb[ob, ob, vb, vb], t1_bb, t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    return singles_res


def ccsd_t2_aaaa_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb):

    #    < 0 | m* n* f e e(-T) H e(T) | 0> :

    #	 -1.0000 P(m,n)f_aa(i,n)*t2_aaaa(e,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('in,efmi->efmn', f_aa[oa, oa], t2_aaaa)
    doubles_res  =  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(e,f)f_aa(e,a)*t2_aaaa(a,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ea,afmn->efmn', f_aa[va, va], t2_aaaa)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 P(m,n)f_aa(i,a)*t1_aa(a,n)*t2_aaaa(e,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('ia,an,efmi->efmn', f_aa[oa, va], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(e,f)f_aa(i,a)*t2_aaaa(a,f,m,n)*t1_aa(e,i)
    contracted_intermediate = -1.000000000000000 * einsum('ia,afmn,ei->efmn', f_aa[oa, va], t2_aaaa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 <e,f||m,n>_aaaa
    doubles_res +=  1.000000000000000 * einsum('efmn->efmn', g_aaaa[va, va, oa, oa])

    #	  1.0000 P(e,f)<i,e||m,n>_aaaa*t1_aa(f,i)
    contracted_intermediate =  1.000000000000000 * einsum('iemn,fi->efmn', g_aaaa[oa, va, oa, oa], t1_aa)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 P(m,n)<e,f||a,n>_aaaa*t1_aa(a,m)
    contracted_intermediate =  1.000000000000000 * einsum('efan,am->efmn', g_aaaa[va, va, va, oa], t1_aa)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.5000 <j,i||m,n>_aaaa*t2_aaaa(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jimn,efji->efmn', g_aaaa[oa, oa, oa, oa], t2_aaaa)

    #	  1.0000 P(m,n)*P(e,f)<i,e||a,n>_aaaa*t2_aaaa(a,f,m,i)
    contracted_intermediate =  1.000000000000000 * einsum('iean,afmi->efmn', g_aaaa[oa, va, va, oa], t2_aaaa)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<e,i||n,a>_abab*t2_abab(f,a,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('eina,fami->efmn', g_abab[va, ob, oa, vb], t2_abab)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  0.5000 <e,f||a,b>_aaaa*t2_aaaa(a,b,m,n)
    doubles_res +=  0.500000000000000 * einsum('efab,abmn->efmn', g_aaaa[va, va, va, va], t2_aaaa)

    #	  1.0000 P(m,n)<j,i||a,n>_aaaa*t1_aa(a,i)*t2_aaaa(e,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jian,ai,efmj->efmn', g_aaaa[oa, oa, va, oa], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(m,n)<j,i||n,a>_abab*t1_bb(a,i)*t2_aaaa(e,f,m,j)
    contracted_intermediate = -1.000000000000000 * einsum('jina,ai,efmj->efmn', g_abab[oa, ob, oa, vb], t1_bb, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.5000 P(m,n)<j,i||a,n>_aaaa*t1_aa(a,m)*t2_aaaa(e,f,j,i)
    contracted_intermediate =  0.500000000000000 * einsum('jian,am,efji->efmn', g_aaaa[oa, oa, va, oa], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<j,i||a,n>_aaaa*t2_aaaa(a,f,m,j)*t1_aa(e,i)
    contracted_intermediate = -1.000000000000000 * einsum('jian,afmj,ei->efmn', g_aaaa[oa, oa, va, oa], t2_aaaa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  1.0000 P(m,n)*P(e,f)<i,j||n,a>_abab*t2_abab(f,a,m,j)*t1_aa(e,i)
    contracted_intermediate =  1.000000000000000 * einsum('ijna,famj,ei->efmn', g_abab[oa, ob, oa, vb], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  1.0000 P(e,f)<i,e||a,b>_aaaa*t1_aa(a,i)*t2_aaaa(b,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ieab,ai,bfmn->efmn', g_aaaa[oa, va, va, va], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 P(e,f)<e,i||b,a>_abab*t1_bb(a,i)*t2_aaaa(b,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('eiba,ai,bfmn->efmn', g_abab[va, ob, va, vb], t1_bb, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<i,e||a,b>_aaaa*t1_aa(a,n)*t2_aaaa(b,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('ieab,an,bfmi->efmn', g_aaaa[oa, va, va, va], t1_aa, t2_aaaa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<e,i||a,b>_abab*t1_aa(a,n)*t2_abab(f,b,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('eiab,an,fbmi->efmn', g_abab[va, ob, va, vb], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  0.5000 P(e,f)<i,e||a,b>_aaaa*t2_aaaa(a,b,m,n)*t1_aa(f,i)
    contracted_intermediate =  0.500000000000000 * einsum('ieab,abmn,fi->efmn', g_aaaa[oa, va, va, va], t2_aaaa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 <j,i||m,n>_aaaa*t1_aa(e,i)*t1_aa(f,j)
    doubles_res += -1.000000000000000 * einsum('jimn,ei,fj->efmn', g_aaaa[oa, oa, oa, oa], t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 P(m,n)*P(e,f)<i,e||a,n>_aaaa*t1_aa(a,m)*t1_aa(f,i)
    contracted_intermediate =  1.000000000000000 * einsum('iean,am,fi->efmn', g_aaaa[oa, va, va, oa], t1_aa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -1.0000 <e,f||a,b>_aaaa*t1_aa(a,n)*t1_aa(b,m)
    doubles_res += -1.000000000000000 * einsum('efab,an,bm->efmn', g_aaaa[va, va, va, va], t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 P(m,n)<j,i||a,b>_aaaa*t2_aaaa(a,b,n,i)*t2_aaaa(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('jiab,abni,efmj->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -0.5000 P(m,n)<j,i||a,b>_abab*t2_abab(a,b,n,i)*t2_aaaa(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('jiab,abni,efmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -0.5000 P(m,n)<j,i||b,a>_abab*t2_abab(b,a,n,i)*t2_aaaa(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('jiba,bani,efmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.2500 <j,i||a,b>_aaaa*t2_aaaa(a,b,m,n)*t2_aaaa(e,f,j,i)
    doubles_res +=  0.250000000000000 * einsum('jiab,abmn,efji->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_aaaa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <j,i||a,b>_aaaa*t2_aaaa(a,e,j,i)*t2_aaaa(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiab,aeji,bfmn->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||b,a>_abab*t2_abab(e,a,j,i)*t2_aaaa(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiba,eaji,bfmn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,j||b,a>_abab*t2_abab(e,a,i,j)*t2_aaaa(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('ijba,eaij,bfmn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 P(m,n)<j,i||a,b>_aaaa*t2_aaaa(a,e,n,i)*t2_aaaa(b,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,aeni,bfmj->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<i,j||a,b>_abab*t2_aaaa(a,e,n,i)*t2_abab(f,b,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('ijab,aeni,fbmj->efmn', g_abab[oa, ob, va, vb], t2_aaaa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<j,i||b,a>_abab*t2_abab(e,a,n,i)*t2_aaaa(b,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiba,eani,bfmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<j,i||a,b>_bbbb*t2_abab(e,a,n,i)*t2_abab(f,b,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,eani,fbmj->efmn', g_bbbb[ob, ob, vb, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -0.5000 <j,i||a,b>_aaaa*t2_aaaa(a,e,m,n)*t2_aaaa(b,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiab,aemn,bfji->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_aaaa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <j,i||a,b>_abab*t2_aaaa(a,e,m,n)*t2_abab(f,b,j,i)
    doubles_res +=  0.500000000000000 * einsum('jiab,aemn,fbji->efmn', g_abab[oa, ob, va, vb], t2_aaaa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <i,j||a,b>_abab*t2_aaaa(a,e,m,n)*t2_abab(f,b,i,j)
    doubles_res +=  0.500000000000000 * einsum('ijab,aemn,fbij->efmn', g_abab[oa, ob, va, vb], t2_aaaa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 P(m,n)<j,i||a,b>_aaaa*t1_aa(a,i)*t1_aa(b,n)*t2_aaaa(e,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,ai,bn,efmj->efmn', g_aaaa[oa, oa, va, va], t1_aa, t1_aa, t2_aaaa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(m,n)<j,i||b,a>_abab*t1_bb(a,i)*t1_aa(b,n)*t2_aaaa(e,f,m,j)
    contracted_intermediate = -1.000000000000000 * einsum('jiba,ai,bn,efmj->efmn', g_abab[oa, ob, va, vb], t1_bb, t1_aa, t2_aaaa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(e,f)<j,i||a,b>_aaaa*t1_aa(a,i)*t2_aaaa(b,f,m,n)*t1_aa(e,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,ai,bfmn,ej->efmn', g_aaaa[oa, oa, va, va], t1_aa, t2_aaaa, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 P(e,f)<j,i||b,a>_abab*t1_bb(a,i)*t2_aaaa(b,f,m,n)*t1_aa(e,j)
    contracted_intermediate = -1.000000000000000 * einsum('jiba,ai,bfmn,ej->efmn', g_abab[oa, ob, va, vb], t1_bb, t2_aaaa, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -0.5000 <j,i||a,b>_aaaa*t1_aa(a,n)*t1_aa(b,m)*t2_aaaa(e,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiab,an,bm,efji->efmn', g_aaaa[oa, oa, va, va], t1_aa, t1_aa, t2_aaaa, optimize=['einsum_path', (0, 3), (0, 2), (0, 1)])

    #	  1.0000 P(m,n)*P(e,f)<j,i||a,b>_aaaa*t1_aa(a,n)*t2_aaaa(b,f,m,j)*t1_aa(e,i)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,an,bfmj,ei->efmn', g_aaaa[oa, oa, va, va], t1_aa, t2_aaaa, t1_aa, optimize=['einsum_path', (0, 3), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  1.0000 P(m,n)*P(e,f)<i,j||a,b>_abab*t1_aa(a,n)*t2_abab(f,b,m,j)*t1_aa(e,i)
    contracted_intermediate =  1.000000000000000 * einsum('ijab,an,fbmj,ei->efmn', g_abab[oa, ob, va, vb], t1_aa, t2_abab, t1_aa, optimize=['einsum_path', (0, 3), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -0.5000 <j,i||a,b>_aaaa*t2_aaaa(a,b,m,n)*t1_aa(e,i)*t1_aa(f,j)
    doubles_res += -0.500000000000000 * einsum('jiab,abmn,ei,fj->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t1_aa, t1_aa, optimize=['einsum_path', (0, 2), (1, 2), (0, 1)])

    #	 -1.0000 P(m,n)<j,i||a,n>_aaaa*t1_aa(a,m)*t1_aa(e,i)*t1_aa(f,j)
    contracted_intermediate = -1.000000000000000 * einsum('jian,am,ei,fj->efmn', g_aaaa[oa, oa, va, oa], t1_aa, t1_aa, t1_aa, optimize=['einsum_path', (0, 2), (1, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(e,f)<i,e||a,b>_aaaa*t1_aa(a,n)*t1_aa(b,m)*t1_aa(f,i)
    contracted_intermediate = -1.000000000000000 * einsum('ieab,an,bm,fi->efmn', g_aaaa[oa, va, va, va], t1_aa, t1_aa, t1_aa, optimize=['einsum_path', (0, 3), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 <j,i||a,b>_aaaa*t1_aa(a,n)*t1_aa(b,m)*t1_aa(e,i)*t1_aa(f,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,an,bm,ei,fj->efmn', g_aaaa[oa, oa, va, va], t1_aa, t1_aa, t1_aa, t1_aa, optimize=['einsum_path', (0, 3), (2, 3), (0, 2), (0, 1)])

    return doubles_res


def ccsd_t2_bbbb_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb):

    #    < 0 | m* n* f e e(-T) H e(T) | 0> :

    #	 -1.0000 P(m,n)f_bb(i,n)*t2_bbbb(e,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('in,efmi->efmn', f_bb[ob, ob], t2_bbbb)
    doubles_res  =  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(e,f)f_bb(e,a)*t2_bbbb(a,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ea,afmn->efmn', f_bb[vb, vb], t2_bbbb)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 P(m,n)f_bb(i,a)*t1_bb(a,n)*t2_bbbb(e,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('ia,an,efmi->efmn', f_bb[ob, vb], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(e,f)f_bb(i,a)*t2_bbbb(a,f,m,n)*t1_bb(e,i)
    contracted_intermediate = -1.000000000000000 * einsum('ia,afmn,ei->efmn', f_bb[ob, vb], t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 <e,f||m,n>_bbbb
    doubles_res +=  1.000000000000000 * einsum('efmn->efmn', g_bbbb[vb, vb, ob, ob])

    #	  1.0000 P(e,f)<i,e||m,n>_bbbb*t1_bb(f,i)
    contracted_intermediate =  1.000000000000000 * einsum('iemn,fi->efmn', g_bbbb[ob, vb, ob, ob], t1_bb)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 P(m,n)<e,f||a,n>_bbbb*t1_bb(a,m)
    contracted_intermediate =  1.000000000000000 * einsum('efan,am->efmn', g_bbbb[vb, vb, vb, ob], t1_bb)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.5000 <j,i||m,n>_bbbb*t2_bbbb(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jimn,efji->efmn', g_bbbb[ob, ob, ob, ob], t2_bbbb)

    #	 -1.0000 P(m,n)*P(e,f)<i,e||a,n>_abab*t2_abab(a,f,i,m)
    contracted_intermediate = -1.000000000000000 * einsum('iean,afim->efmn', g_abab[oa, vb, va, ob], t2_abab)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  1.0000 P(m,n)*P(e,f)<i,e||a,n>_bbbb*t2_bbbb(a,f,m,i)
    contracted_intermediate =  1.000000000000000 * einsum('iean,afmi->efmn', g_bbbb[ob, vb, vb, ob], t2_bbbb)
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  0.5000 <e,f||a,b>_bbbb*t2_bbbb(a,b,m,n)
    doubles_res +=  0.500000000000000 * einsum('efab,abmn->efmn', g_bbbb[vb, vb, vb, vb], t2_bbbb)

    #	 -1.0000 P(m,n)<i,j||a,n>_abab*t1_aa(a,i)*t2_bbbb(e,f,m,j)
    contracted_intermediate = -1.000000000000000 * einsum('ijan,ai,efmj->efmn', g_abab[oa, ob, va, ob], t1_aa, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<j,i||a,n>_bbbb*t1_bb(a,i)*t2_bbbb(e,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jian,ai,efmj->efmn', g_bbbb[ob, ob, vb, ob], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.5000 P(m,n)<j,i||a,n>_bbbb*t1_bb(a,m)*t2_bbbb(e,f,j,i)
    contracted_intermediate =  0.500000000000000 * einsum('jian,am,efji->efmn', g_bbbb[ob, ob, vb, ob], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)*P(e,f)<j,i||a,n>_abab*t2_abab(a,f,j,m)*t1_bb(e,i)
    contracted_intermediate =  1.000000000000000 * einsum('jian,afjm,ei->efmn', g_abab[oa, ob, va, ob], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<j,i||a,n>_bbbb*t2_bbbb(a,f,m,j)*t1_bb(e,i)
    contracted_intermediate = -1.000000000000000 * einsum('jian,afmj,ei->efmn', g_bbbb[ob, ob, vb, ob], t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  1.0000 P(e,f)<i,e||a,b>_abab*t1_aa(a,i)*t2_bbbb(b,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ieab,ai,bfmn->efmn', g_abab[oa, vb, va, vb], t1_aa, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 P(e,f)<i,e||a,b>_bbbb*t1_bb(a,i)*t2_bbbb(b,f,m,n)
    contracted_intermediate =  1.000000000000000 * einsum('ieab,ai,bfmn->efmn', g_bbbb[ob, vb, vb, vb], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<i,e||b,a>_abab*t1_bb(a,n)*t2_abab(b,f,i,m)
    contracted_intermediate = -1.000000000000000 * einsum('ieba,an,bfim->efmn', g_abab[oa, vb, va, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -1.0000 P(m,n)*P(e,f)<i,e||a,b>_bbbb*t1_bb(a,n)*t2_bbbb(b,f,m,i)
    contracted_intermediate = -1.000000000000000 * einsum('ieab,an,bfmi->efmn', g_bbbb[ob, vb, vb, vb], t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  0.5000 P(e,f)<i,e||a,b>_bbbb*t2_bbbb(a,b,m,n)*t1_bb(f,i)
    contracted_intermediate =  0.500000000000000 * einsum('ieab,abmn,fi->efmn', g_bbbb[ob, vb, vb, vb], t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -1.0000 <j,i||m,n>_bbbb*t1_bb(e,i)*t1_bb(f,j)
    doubles_res += -1.000000000000000 * einsum('jimn,ei,fj->efmn', g_bbbb[ob, ob, ob, ob], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 P(m,n)*P(e,f)<i,e||a,n>_bbbb*t1_bb(a,m)*t1_bb(f,i)
    contracted_intermediate =  1.000000000000000 * einsum('iean,am,fi->efmn', g_bbbb[ob, vb, vb, ob], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -1.0000 <e,f||a,b>_bbbb*t1_bb(a,n)*t1_bb(b,m)
    doubles_res += -1.000000000000000 * einsum('efab,an,bm->efmn', g_bbbb[vb, vb, vb, vb], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 P(m,n)<i,j||a,b>_abab*t2_abab(a,b,i,n)*t2_bbbb(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('ijab,abin,efmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -0.5000 P(m,n)<i,j||b,a>_abab*t2_abab(b,a,i,n)*t2_bbbb(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('ijba,bain,efmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -0.5000 P(m,n)<j,i||a,b>_bbbb*t2_bbbb(a,b,n,i)*t2_bbbb(e,f,m,j)
    contracted_intermediate = -0.500000000000000 * einsum('jiab,abni,efmj->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.2500 <j,i||a,b>_bbbb*t2_bbbb(a,b,m,n)*t2_bbbb(e,f,j,i)
    doubles_res +=  0.250000000000000 * einsum('jiab,abmn,efji->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_abab*t2_abab(a,e,j,i)*t2_bbbb(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiab,aeji,bfmn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,j||a,b>_abab*t2_abab(a,e,i,j)*t2_bbbb(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('ijab,aeij,bfmn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_bbbb*t2_bbbb(a,e,j,i)*t2_bbbb(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiab,aeji,bfmn->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 P(m,n)<j,i||a,b>_aaaa*t2_abab(a,e,i,n)*t2_abab(b,f,j,m)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,aein,bfjm->efmn', g_aaaa[oa, oa, va, va], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<i,j||a,b>_abab*t2_abab(a,e,i,n)*t2_bbbb(b,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('ijab,aein,bfmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<j,i||b,a>_abab*t2_bbbb(a,e,n,i)*t2_abab(b,f,j,m)
    contracted_intermediate =  1.000000000000000 * einsum('jiba,aeni,bfjm->efmn', g_abab[oa, ob, va, vb], t2_bbbb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<j,i||a,b>_bbbb*t2_bbbb(a,e,n,i)*t2_bbbb(b,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,aeni,bfmj->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  0.5000 <j,i||b,a>_abab*t2_bbbb(a,e,m,n)*t2_abab(b,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jiba,aemn,bfji->efmn', g_abab[oa, ob, va, vb], t2_bbbb, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <i,j||b,a>_abab*t2_bbbb(a,e,m,n)*t2_abab(b,f,i,j)
    doubles_res +=  0.500000000000000 * einsum('ijba,aemn,bfij->efmn', g_abab[oa, ob, va, vb], t2_bbbb, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <j,i||a,b>_bbbb*t2_bbbb(a,e,m,n)*t2_bbbb(b,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiab,aemn,bfji->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t2_bbbb, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 P(m,n)<i,j||a,b>_abab*t1_aa(a,i)*t1_bb(b,n)*t2_bbbb(e,f,m,j)
    contracted_intermediate = -1.000000000000000 * einsum('ijab,ai,bn,efmj->efmn', g_abab[oa, ob, va, vb], t1_aa, t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	  1.0000 P(m,n)<j,i||a,b>_bbbb*t1_bb(a,i)*t1_bb(b,n)*t2_bbbb(e,f,m,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,ai,bn,efmj->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(e,f)<i,j||a,b>_abab*t1_aa(a,i)*t2_bbbb(b,f,m,n)*t1_bb(e,j)
    contracted_intermediate = -1.000000000000000 * einsum('ijab,ai,bfmn,ej->efmn', g_abab[oa, ob, va, vb], t1_aa, t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 P(e,f)<j,i||a,b>_bbbb*t1_bb(a,i)*t2_bbbb(b,f,m,n)*t1_bb(e,j)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,ai,bfmn,ej->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	 -0.5000 <j,i||a,b>_bbbb*t1_bb(a,n)*t1_bb(b,m)*t2_bbbb(e,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiab,an,bm,efji->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t1_bb, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 P(m,n)*P(e,f)<j,i||b,a>_abab*t1_bb(a,n)*t2_abab(b,f,j,m)*t1_bb(e,i)
    contracted_intermediate =  1.000000000000000 * einsum('jiba,an,bfjm,ei->efmn', g_abab[oa, ob, va, vb], t1_bb, t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	  1.0000 P(m,n)*P(e,f)<j,i||a,b>_bbbb*t1_bb(a,n)*t2_bbbb(b,f,m,j)*t1_bb(e,i)
    contracted_intermediate =  1.000000000000000 * einsum('jiab,an,bfmj,ei->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t2_bbbb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)  + -1.00000 * einsum('efmn->femn', contracted_intermediate)  +  1.00000 * einsum('efmn->fenm', contracted_intermediate)

    #	 -0.5000 <j,i||a,b>_bbbb*t2_bbbb(a,b,m,n)*t1_bb(e,i)*t1_bb(f,j)
    doubles_res += -0.500000000000000 * einsum('jiab,abmn,ei,fj->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	 -1.0000 P(m,n)<j,i||a,n>_bbbb*t1_bb(a,m)*t1_bb(e,i)*t1_bb(f,j)
    contracted_intermediate = -1.000000000000000 * einsum('jian,am,ei,fj->efmn', g_bbbb[ob, ob, vb, ob], t1_bb, t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->efnm', contracted_intermediate)

    #	 -1.0000 P(e,f)<i,e||a,b>_bbbb*t1_bb(a,n)*t1_bb(b,m)*t1_bb(f,i)
    contracted_intermediate = -1.000000000000000 * einsum('ieab,an,bm,fi->efmn', g_bbbb[ob, vb, vb, vb], t1_bb, t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])
    doubles_res +=  1.00000 * contracted_intermediate + -1.00000 * einsum('efmn->femn', contracted_intermediate)

    #	  1.0000 <j,i||a,b>_bbbb*t1_bb(a,n)*t1_bb(b,m)*t1_bb(e,i)*t1_bb(f,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,an,bm,ei,fj->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t1_bb, t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 3), (0, 2), (0, 1)])

    return doubles_res


def ccsd_t2_abab_residual(t1_aa, t1_bb, t2_aaaa, t2_bbbb, t2_abab, f_aa, f_bb, g_aaaa, g_bbbb, g_abab, oa, ob, va, vb):

    #    < 0 | m* n* f e e(-T) H e(T) | 0> :

    #	 -1.0000 f_bb(i,n)*t2_abab(e,f,m,i)
    doubles_res  = -1.000000000000000 * einsum('in,efmi->efmn', f_bb[ob, ob], t2_abab)

    #	 -1.0000 f_aa(i,m)*t2_abab(e,f,i,n)
    doubles_res += -1.000000000000000 * einsum('im,efin->efmn', f_aa[oa, oa], t2_abab)

    #	  1.0000 f_aa(e,a)*t2_abab(a,f,m,n)
    doubles_res +=  1.000000000000000 * einsum('ea,afmn->efmn', f_aa[va, va], t2_abab)

    #	  1.0000 f_bb(f,a)*t2_abab(e,a,m,n)
    doubles_res +=  1.000000000000000 * einsum('fa,eamn->efmn', f_bb[vb, vb], t2_abab)

    #	 -1.0000 f_bb(i,a)*t1_bb(a,n)*t2_abab(e,f,m,i)
    doubles_res += -1.000000000000000 * einsum('ia,an,efmi->efmn', f_bb[ob, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 f_aa(i,a)*t1_aa(a,m)*t2_abab(e,f,i,n)
    doubles_res += -1.000000000000000 * einsum('ia,am,efin->efmn', f_aa[oa, va], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 f_aa(i,a)*t2_abab(a,f,m,n)*t1_aa(e,i)
    doubles_res += -1.000000000000000 * einsum('ia,afmn,ei->efmn', f_aa[oa, va], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 f_bb(i,a)*t2_abab(e,a,m,n)*t1_bb(f,i)
    doubles_res += -1.000000000000000 * einsum('ia,eamn,fi->efmn', f_bb[ob, vb], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <e,f||m,n>_abab
    doubles_res +=  1.000000000000000 * einsum('efmn->efmn', g_abab[va, vb, oa, ob])

    #	 -1.0000 <e,i||m,n>_abab*t1_bb(f,i)
    doubles_res += -1.000000000000000 * einsum('eimn,fi->efmn', g_abab[va, ob, oa, ob], t1_bb)

    #	 -1.0000 <i,f||m,n>_abab*t1_aa(e,i)
    doubles_res += -1.000000000000000 * einsum('ifmn,ei->efmn', g_abab[oa, vb, oa, ob], t1_aa)

    #	  1.0000 <e,f||a,n>_abab*t1_aa(a,m)
    doubles_res +=  1.000000000000000 * einsum('efan,am->efmn', g_abab[va, vb, va, ob], t1_aa)

    #	  1.0000 <e,f||m,a>_abab*t1_bb(a,n)
    doubles_res +=  1.000000000000000 * einsum('efma,an->efmn', g_abab[va, vb, oa, vb], t1_bb)

    #	  0.5000 <j,i||m,n>_abab*t2_abab(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jimn,efji->efmn', g_abab[oa, ob, oa, ob], t2_abab)

    #	  0.5000 <i,j||m,n>_abab*t2_abab(e,f,i,j)
    doubles_res +=  0.500000000000000 * einsum('ijmn,efij->efmn', g_abab[oa, ob, oa, ob], t2_abab)

    #	 -1.0000 <e,i||a,n>_abab*t2_abab(a,f,m,i)
    doubles_res += -1.000000000000000 * einsum('eian,afmi->efmn', g_abab[va, ob, va, ob], t2_abab)

    #	 -1.0000 <i,f||a,n>_abab*t2_aaaa(a,e,m,i)
    doubles_res += -1.000000000000000 * einsum('ifan,aemi->efmn', g_abab[oa, vb, va, ob], t2_aaaa)

    #	  1.0000 <i,f||a,n>_bbbb*t2_abab(e,a,m,i)
    doubles_res +=  1.000000000000000 * einsum('ifan,eami->efmn', g_bbbb[ob, vb, vb, ob], t2_abab)

    #	  1.0000 <i,e||a,m>_aaaa*t2_abab(a,f,i,n)
    doubles_res +=  1.000000000000000 * einsum('ieam,afin->efmn', g_aaaa[oa, va, va, oa], t2_abab)

    #	 -1.0000 <e,i||m,a>_abab*t2_bbbb(a,f,n,i)
    doubles_res += -1.000000000000000 * einsum('eima,afni->efmn', g_abab[va, ob, oa, vb], t2_bbbb)

    #	 -1.0000 <i,f||m,a>_abab*t2_abab(e,a,i,n)
    doubles_res += -1.000000000000000 * einsum('ifma,eain->efmn', g_abab[oa, vb, oa, vb], t2_abab)

    #	  0.5000 <e,f||a,b>_abab*t2_abab(a,b,m,n)
    doubles_res +=  0.500000000000000 * einsum('efab,abmn->efmn', g_abab[va, vb, va, vb], t2_abab)

    #	  0.5000 <e,f||b,a>_abab*t2_abab(b,a,m,n)
    doubles_res +=  0.500000000000000 * einsum('efba,bamn->efmn', g_abab[va, vb, va, vb], t2_abab)

    #	 -1.0000 <i,j||a,n>_abab*t1_aa(a,i)*t2_abab(e,f,m,j)
    doubles_res += -1.000000000000000 * einsum('ijan,ai,efmj->efmn', g_abab[oa, ob, va, ob], t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,n>_bbbb*t1_bb(a,i)*t2_abab(e,f,m,j)
    doubles_res +=  1.000000000000000 * einsum('jian,ai,efmj->efmn', g_bbbb[ob, ob, vb, ob], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,m>_aaaa*t1_aa(a,i)*t2_abab(e,f,j,n)
    doubles_res +=  1.000000000000000 * einsum('jiam,ai,efjn->efmn', g_aaaa[oa, oa, va, oa], t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <j,i||m,a>_abab*t1_bb(a,i)*t2_abab(e,f,j,n)
    doubles_res += -1.000000000000000 * einsum('jima,ai,efjn->efmn', g_abab[oa, ob, oa, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <j,i||a,n>_abab*t1_aa(a,m)*t2_abab(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jian,am,efji->efmn', g_abab[oa, ob, va, ob], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <i,j||a,n>_abab*t1_aa(a,m)*t2_abab(e,f,i,j)
    doubles_res +=  0.500000000000000 * einsum('ijan,am,efij->efmn', g_abab[oa, ob, va, ob], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <j,i||m,a>_abab*t1_bb(a,n)*t2_abab(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jima,an,efji->efmn', g_abab[oa, ob, oa, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.5000 <i,j||m,a>_abab*t1_bb(a,n)*t2_abab(e,f,i,j)
    doubles_res +=  0.500000000000000 * einsum('ijma,an,efij->efmn', g_abab[oa, ob, oa, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,j||a,n>_abab*t2_abab(a,f,m,j)*t1_aa(e,i)
    doubles_res +=  1.000000000000000 * einsum('ijan,afmj,ei->efmn', g_abab[oa, ob, va, ob], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,n>_abab*t2_aaaa(a,e,m,j)*t1_bb(f,i)
    doubles_res +=  1.000000000000000 * einsum('jian,aemj,fi->efmn', g_abab[oa, ob, va, ob], t2_aaaa, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <j,i||a,n>_bbbb*t2_abab(e,a,m,j)*t1_bb(f,i)
    doubles_res += -1.000000000000000 * einsum('jian,eamj,fi->efmn', g_bbbb[ob, ob, vb, ob], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <j,i||a,m>_aaaa*t2_abab(a,f,j,n)*t1_aa(e,i)
    doubles_res += -1.000000000000000 * einsum('jiam,afjn,ei->efmn', g_aaaa[oa, oa, va, oa], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 <i,j||m,a>_abab*t2_bbbb(a,f,n,j)*t1_aa(e,i)
    doubles_res +=  1.000000000000000 * einsum('ijma,afnj,ei->efmn', g_abab[oa, ob, oa, vb], t2_bbbb, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 <j,i||m,a>_abab*t2_abab(e,a,j,n)*t1_bb(f,i)
    doubles_res +=  1.000000000000000 * einsum('jima,eajn,fi->efmn', g_abab[oa, ob, oa, vb], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,e||a,b>_aaaa*t1_aa(a,i)*t2_abab(b,f,m,n)
    doubles_res +=  1.000000000000000 * einsum('ieab,ai,bfmn->efmn', g_aaaa[oa, va, va, va], t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <e,i||b,a>_abab*t1_bb(a,i)*t2_abab(b,f,m,n)
    doubles_res +=  1.000000000000000 * einsum('eiba,ai,bfmn->efmn', g_abab[va, ob, va, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,f||a,b>_abab*t1_aa(a,i)*t2_abab(e,b,m,n)
    doubles_res +=  1.000000000000000 * einsum('ifab,ai,ebmn->efmn', g_abab[oa, vb, va, vb], t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,f||a,b>_bbbb*t1_bb(a,i)*t2_abab(e,b,m,n)
    doubles_res +=  1.000000000000000 * einsum('ifab,ai,ebmn->efmn', g_bbbb[ob, vb, vb, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <e,i||b,a>_abab*t1_bb(a,n)*t2_abab(b,f,m,i)
    doubles_res += -1.000000000000000 * einsum('eiba,an,bfmi->efmn', g_abab[va, ob, va, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,f||b,a>_abab*t1_bb(a,n)*t2_aaaa(b,e,m,i)
    doubles_res += -1.000000000000000 * einsum('ifba,an,bemi->efmn', g_abab[oa, vb, va, vb], t1_bb, t2_aaaa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,f||a,b>_bbbb*t1_bb(a,n)*t2_abab(e,b,m,i)
    doubles_res += -1.000000000000000 * einsum('ifab,an,ebmi->efmn', g_bbbb[ob, vb, vb, vb], t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,e||a,b>_aaaa*t1_aa(a,m)*t2_abab(b,f,i,n)
    doubles_res += -1.000000000000000 * einsum('ieab,am,bfin->efmn', g_aaaa[oa, va, va, va], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 <e,i||a,b>_abab*t1_aa(a,m)*t2_bbbb(b,f,n,i)
    doubles_res += -1.000000000000000 * einsum('eiab,am,bfni->efmn', g_abab[va, ob, va, vb], t1_aa, t2_bbbb, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 <i,f||a,b>_abab*t1_aa(a,m)*t2_abab(e,b,i,n)
    doubles_res += -1.000000000000000 * einsum('ifab,am,ebin->efmn', g_abab[oa, vb, va, vb], t1_aa, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <e,i||a,b>_abab*t2_abab(a,b,m,n)*t1_bb(f,i)
    doubles_res += -0.500000000000000 * einsum('eiab,abmn,fi->efmn', g_abab[va, ob, va, vb], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <e,i||b,a>_abab*t2_abab(b,a,m,n)*t1_bb(f,i)
    doubles_res += -0.500000000000000 * einsum('eiba,bamn,fi->efmn', g_abab[va, ob, va, vb], t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,f||a,b>_abab*t2_abab(a,b,m,n)*t1_aa(e,i)
    doubles_res += -0.500000000000000 * einsum('ifab,abmn,ei->efmn', g_abab[oa, vb, va, vb], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <i,f||b,a>_abab*t2_abab(b,a,m,n)*t1_aa(e,i)
    doubles_res += -0.500000000000000 * einsum('ifba,bamn,ei->efmn', g_abab[oa, vb, va, vb], t2_abab, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  1.0000 <i,j||m,n>_abab*t1_aa(e,i)*t1_bb(f,j)
    doubles_res +=  1.000000000000000 * einsum('ijmn,ei,fj->efmn', g_abab[oa, ob, oa, ob], t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <e,i||a,n>_abab*t1_aa(a,m)*t1_bb(f,i)
    doubles_res += -1.000000000000000 * einsum('eian,am,fi->efmn', g_abab[va, ob, va, ob], t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,f||a,n>_abab*t1_aa(a,m)*t1_aa(e,i)
    doubles_res += -1.000000000000000 * einsum('ifan,am,ei->efmn', g_abab[oa, vb, va, ob], t1_aa, t1_aa, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 <e,i||m,a>_abab*t1_bb(a,n)*t1_bb(f,i)
    doubles_res += -1.000000000000000 * einsum('eima,an,fi->efmn', g_abab[va, ob, oa, vb], t1_bb, t1_bb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -1.0000 <i,f||m,a>_abab*t1_bb(a,n)*t1_aa(e,i)
    doubles_res += -1.000000000000000 * einsum('ifma,an,ei->efmn', g_abab[oa, vb, oa, vb], t1_bb, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <e,f||b,a>_abab*t1_bb(a,n)*t1_aa(b,m)
    doubles_res +=  1.000000000000000 * einsum('efba,an,bm->efmn', g_abab[va, vb, va, vb], t1_bb, t1_aa, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,j||a,b>_abab*t2_abab(a,b,i,n)*t2_abab(e,f,m,j)
    doubles_res += -0.500000000000000 * einsum('ijab,abin,efmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,j||b,a>_abab*t2_abab(b,a,i,n)*t2_abab(e,f,m,j)
    doubles_res += -0.500000000000000 * einsum('ijba,bain,efmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_bbbb*t2_bbbb(a,b,n,i)*t2_abab(e,f,m,j)
    doubles_res += -0.500000000000000 * einsum('jiab,abni,efmj->efmn', g_bbbb[ob, ob, vb, vb], t2_bbbb, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_aaaa*t2_aaaa(a,b,m,i)*t2_abab(e,f,j,n)
    doubles_res += -0.500000000000000 * einsum('jiab,abmi,efjn->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_abab*t2_abab(a,b,m,i)*t2_abab(e,f,j,n)
    doubles_res += -0.500000000000000 * einsum('jiab,abmi,efjn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||b,a>_abab*t2_abab(b,a,m,i)*t2_abab(e,f,j,n)
    doubles_res += -0.500000000000000 * einsum('jiba,bami,efjn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.2500 <j,i||a,b>_abab*t2_abab(a,b,m,n)*t2_abab(e,f,j,i)
    doubles_res +=  0.250000000000000 * einsum('jiab,abmn,efji->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.2500 <i,j||a,b>_abab*t2_abab(a,b,m,n)*t2_abab(e,f,i,j)
    doubles_res +=  0.250000000000000 * einsum('ijab,abmn,efij->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.2500 <j,i||b,a>_abab*t2_abab(b,a,m,n)*t2_abab(e,f,j,i)
    doubles_res +=  0.250000000000000 * einsum('jiba,bamn,efji->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  0.2500 <i,j||b,a>_abab*t2_abab(b,a,m,n)*t2_abab(e,f,i,j)
    doubles_res +=  0.250000000000000 * einsum('ijba,bamn,efij->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||a,b>_aaaa*t2_aaaa(a,e,j,i)*t2_abab(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiab,aeji,bfmn->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||b,a>_abab*t2_abab(e,a,j,i)*t2_abab(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('jiba,eaji,bfmn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <i,j||b,a>_abab*t2_abab(e,a,i,j)*t2_abab(b,f,m,n)
    doubles_res += -0.500000000000000 * einsum('ijba,eaij,bfmn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,j||b,a>_abab*t2_abab(e,a,i,n)*t2_abab(b,f,m,j)
    doubles_res +=  1.000000000000000 * einsum('ijba,eain,bfmj->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,b>_aaaa*t2_aaaa(a,e,m,i)*t2_abab(b,f,j,n)
    doubles_res +=  1.000000000000000 * einsum('jiab,aemi,bfjn->efmn', g_aaaa[oa, oa, va, va], t2_aaaa, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <i,j||a,b>_abab*t2_aaaa(a,e,m,i)*t2_bbbb(b,f,n,j)
    doubles_res +=  1.000000000000000 * einsum('ijab,aemi,bfnj->efmn', g_abab[oa, ob, va, vb], t2_aaaa, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||b,a>_abab*t2_abab(e,a,m,i)*t2_abab(b,f,j,n)
    doubles_res +=  1.000000000000000 * einsum('jiba,eami,bfjn->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 1), (0, 1)])

    #	  1.0000 <j,i||a,b>_bbbb*t2_abab(e,a,m,i)*t2_bbbb(b,f,n,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,eami,bfnj->efmn', g_bbbb[ob, ob, vb, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 1), (0, 1)])

    #	 -0.5000 <j,i||b,a>_abab*t2_abab(e,a,m,n)*t2_abab(b,f,j,i)
    doubles_res += -0.500000000000000 * einsum('jiba,eamn,bfji->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -0.5000 <i,j||b,a>_abab*t2_abab(e,a,m,n)*t2_abab(b,f,i,j)
    doubles_res += -0.500000000000000 * einsum('ijba,eamn,bfij->efmn', g_abab[oa, ob, va, vb], t2_abab, t2_abab, optimize=['einsum_path', (0, 2), (0, 1)])

    #	  0.5000 <j,i||a,b>_bbbb*t2_abab(e,a,m,n)*t2_bbbb(b,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jiab,eamn,bfji->efmn', g_bbbb[ob, ob, vb, vb], t2_abab, t2_bbbb, optimize=['einsum_path', (0, 2), (0, 1)])

    #	 -1.0000 <i,j||a,b>_abab*t1_aa(a,i)*t1_bb(b,n)*t2_abab(e,f,m,j)
    doubles_res += -1.000000000000000 * einsum('ijab,ai,bn,efmj->efmn', g_abab[oa, ob, va, vb], t1_aa, t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_bbbb*t1_bb(a,i)*t1_bb(b,n)*t2_abab(e,f,m,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,ai,bn,efmj->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t1_bb, t2_abab, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_aaaa*t1_aa(a,i)*t1_aa(b,m)*t2_abab(e,f,j,n)
    doubles_res +=  1.000000000000000 * einsum('jiab,ai,bm,efjn->efmn', g_aaaa[oa, oa, va, va], t1_aa, t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	 -1.0000 <j,i||b,a>_abab*t1_bb(a,i)*t1_aa(b,m)*t2_abab(e,f,j,n)
    doubles_res += -1.000000000000000 * einsum('jiba,ai,bm,efjn->efmn', g_abab[oa, ob, va, vb], t1_bb, t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_aaaa*t1_aa(a,i)*t2_abab(b,f,m,n)*t1_aa(e,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,ai,bfmn,ej->efmn', g_aaaa[oa, oa, va, va], t1_aa, t2_abab, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	 -1.0000 <j,i||b,a>_abab*t1_bb(a,i)*t2_abab(b,f,m,n)*t1_aa(e,j)
    doubles_res += -1.000000000000000 * einsum('jiba,ai,bfmn,ej->efmn', g_abab[oa, ob, va, vb], t1_bb, t2_abab, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	 -1.0000 <i,j||a,b>_abab*t1_aa(a,i)*t2_abab(e,b,m,n)*t1_bb(f,j)
    doubles_res += -1.000000000000000 * einsum('ijab,ai,ebmn,fj->efmn', g_abab[oa, ob, va, vb], t1_aa, t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_bbbb*t1_bb(a,i)*t2_abab(e,b,m,n)*t1_bb(f,j)
    doubles_res +=  1.000000000000000 * einsum('jiab,ai,ebmn,fj->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  0.5000 <j,i||b,a>_abab*t1_bb(a,n)*t1_aa(b,m)*t2_abab(e,f,j,i)
    doubles_res +=  0.500000000000000 * einsum('jiba,an,bm,efji->efmn', g_abab[oa, ob, va, vb], t1_bb, t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	  0.5000 <i,j||b,a>_abab*t1_bb(a,n)*t1_aa(b,m)*t2_abab(e,f,i,j)
    doubles_res +=  0.500000000000000 * einsum('ijba,an,bm,efij->efmn', g_abab[oa, ob, va, vb], t1_bb, t1_aa, t2_abab, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	  1.0000 <i,j||b,a>_abab*t1_bb(a,n)*t2_abab(b,f,m,j)*t1_aa(e,i)
    doubles_res +=  1.000000000000000 * einsum('ijba,an,bfmj,ei->efmn', g_abab[oa, ob, va, vb], t1_bb, t2_abab, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	  1.0000 <j,i||b,a>_abab*t1_bb(a,n)*t2_aaaa(b,e,m,j)*t1_bb(f,i)
    doubles_res +=  1.000000000000000 * einsum('jiba,an,bemj,fi->efmn', g_abab[oa, ob, va, vb], t1_bb, t2_aaaa, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_bbbb*t1_bb(a,n)*t2_abab(e,b,m,j)*t1_bb(f,i)
    doubles_res +=  1.000000000000000 * einsum('jiab,an,ebmj,fi->efmn', g_bbbb[ob, ob, vb, vb], t1_bb, t2_abab, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_aaaa*t1_aa(a,m)*t2_abab(b,f,j,n)*t1_aa(e,i)
    doubles_res +=  1.000000000000000 * einsum('jiab,am,bfjn,ei->efmn', g_aaaa[oa, oa, va, va], t1_aa, t2_abab, t1_aa, optimize=['einsum_path', (0, 3), (1, 2), (0, 1)])

    #	  1.0000 <i,j||a,b>_abab*t1_aa(a,m)*t2_bbbb(b,f,n,j)*t1_aa(e,i)
    doubles_res +=  1.000000000000000 * einsum('ijab,am,bfnj,ei->efmn', g_abab[oa, ob, va, vb], t1_aa, t2_bbbb, t1_aa, optimize=['einsum_path', (0, 3), (1, 2), (0, 1)])

    #	  1.0000 <j,i||a,b>_abab*t1_aa(a,m)*t2_abab(e,b,j,n)*t1_bb(f,i)
    doubles_res +=  1.000000000000000 * einsum('jiab,am,ebjn,fi->efmn', g_abab[oa, ob, va, vb], t1_aa, t2_abab, t1_bb, optimize=['einsum_path', (0, 2), (0, 2), (0, 1)])

    #	  0.5000 <i,j||a,b>_abab*t2_abab(a,b,m,n)*t1_aa(e,i)*t1_bb(f,j)
    doubles_res +=  0.500000000000000 * einsum('ijab,abmn,ei,fj->efmn', g_abab[oa, ob, va, vb], t2_abab, t1_aa, t1_bb, optimize=['einsum_path', (0, 2), (0, 2), (0, 1)])

    #	  0.5000 <i,j||b,a>_abab*t2_abab(b,a,m,n)*t1_aa(e,i)*t1_bb(f,j)
    doubles_res +=  0.500000000000000 * einsum('ijba,bamn,ei,fj->efmn', g_abab[oa, ob, va, vb], t2_abab, t1_aa, t1_bb, optimize=['einsum_path', (0, 2), (0, 2), (0, 1)])

    #	  1.0000 <i,j||a,n>_abab*t1_aa(a,m)*t1_aa(e,i)*t1_bb(f,j)
    doubles_res +=  1.000000000000000 * einsum('ijan,am,ei,fj->efmn', g_abab[oa, ob, va, ob], t1_aa, t1_aa, t1_bb, optimize=['einsum_path', (0, 2), (0, 2), (0, 1)])

    #	  1.0000 <i,j||m,a>_abab*t1_bb(a,n)*t1_aa(e,i)*t1_bb(f,j)
    doubles_res +=  1.000000000000000 * einsum('ijma,an,ei,fj->efmn', g_abab[oa, ob, oa, vb], t1_bb, t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	 -1.0000 <e,i||b,a>_abab*t1_bb(a,n)*t1_aa(b,m)*t1_bb(f,i)
    doubles_res += -1.000000000000000 * einsum('eiba,an,bm,fi->efmn', g_abab[va, ob, va, vb], t1_bb, t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (0, 2), (0, 1)])

    #	 -1.0000 <i,f||b,a>_abab*t1_bb(a,n)*t1_aa(b,m)*t1_aa(e,i)
    doubles_res += -1.000000000000000 * einsum('ifba,an,bm,ei->efmn', g_abab[oa, vb, va, vb], t1_bb, t1_aa, t1_aa, optimize=['einsum_path', (0, 1), (1, 2), (0, 1)])

    #	  1.0000 <i,j||b,a>_abab*t1_bb(a,n)*t1_aa(b,m)*t1_aa(e,i)*t1_bb(f,j)
    doubles_res +=  1.000000000000000 * einsum('ijba,an,bm,ei,fj->efmn', g_abab[oa, ob, va, vb], t1_bb, t1_aa, t1_aa, t1_bb, optimize=['einsum_path', (0, 1), (1, 3), (0, 2), (0, 1)])

    return doubles_res

