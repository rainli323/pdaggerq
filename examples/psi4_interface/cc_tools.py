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
Driver for spin-orbital CCSD and EOM-CCSD. (EOM-)CCSD code generated with pdaggerq. Integrals come from psi4.
"""

import numpy as np
from numpy import einsum

# psi4
import psi4

# ccsd iterations
from ccsd import ccsd_iterations
from ccsd import ccsd_energy

# ccsdt iterations
from ccsdt import ccsdt_iterations
from ccsdt import ccsdt_energy

def spatial_to_spin_orbital_oei(h, n, no):
    """
    get spin-orbital-basis one-electron integrals

    :param h: one-electron orbitals
    :param n: number of spatial orbitals
    :param no: number of (doubly) occupied orbitals
    :return:  spin-orbital one-electron integrals, sh
    """

    # build spin-orbital oeis
    sh = np.zeros((2*n,2*n))

    # index 1
    for i in range(0,n):
        ia = i
        ib = i
    
        # alpha occ do nothing
        if ( ia < no ):
            ia = i
        # alpha vir shift up by no
        else :
            ia += no
        # beta occ
        if ( ib < no ):
            ib += no
        else :
            ib += n
    
        # index 2
        for j in range(0,n):
            ja = j
            jb = j
    
            # alpha occ
            if ( ja < no ):
                ja = j
            # alpha vir
            else :
                ja += no
            # beta occ
            if ( jb < no ):
                jb += no
            # beta vir
            else :
                jb += n

            # Haa
            sh[ia,ja] = h[i,j]
            # Hbb
            sh[ib,jb] = h[i,j]
    
    return sh

def spatial_to_spin_orbital_tei(g, n, no):
    """
    get spin-orbital-basis two-electron integrals

    :param g: two-electron integrals in chemists' notation
    :param n: number of spatial orbitals
    :param no: number of (doubly) occupied orbitals
    :return:  spin-orbital two-electron integrals, sg
    """

    # build spin-orbital teis
    sg = np.zeros((2*n,2*n,2*n,2*n))

    # index 1
    for i in range(0,n):
        ia = i
        ib = i
    
        # alpha occ do nothing
        if ( ia < no ):
            ia = i
        # alpha vir shift up by no
        else :
            ia += no
        # beta occ
        if ( ib < no ):
            ib += no
        else :
            ib += n
    
        # index 2
        for j in range(0,n):
            ja = j
            jb = j
    
            # alpha occ
            if ( ja < no ):
                ja = j
            # alpha vir
            else :
                ja += no
            # beta occ
            if ( jb < no ):
                jb += no
            # beta vir
            else :
                jb += n

            # index 3
            for k in range(0,n):
                ka = k
                kb = k
    
                # alpha occ
                if ( ka < no ):
                    ka = k
                # alpha vir
                else :
                    ka += no
                # beta occ
                if ( kb < no ):
                    kb += no
                # beta vir
                else :
                    kb += n
    
                # index 4
                for l in range(0,n):
                    la = l
                    lb = l
    
                    # alpha occ
                    if ( la < no ):
                        la = l
                    # alpha vir
                    else :
                        la += no
                    # beta occ
                    if ( lb < no ):
                        lb += no
                    # beta vir
                    else :
                        lb += n
                     
                    # (aa|aa)
                    sg[ia,ja,ka,la] = g[i,j,k,l]
                    # (aa|bb)
                    sg[ia,ja,kb,lb] = g[i,j,k,l]
                    # (bb|aa)
                    sg[ib,jb,ka,la] = g[i,j,k,l]
                    # (bb|bb)
                    sg[ib,jb,kb,lb] = g[i,j,k,l]
    
    return sg

def get_integrals():
    """

    get one- and two-electron integrals from psi4

    :return nsocc: number of occupied orbitals
    :return nsvirt: number of virtual orbitals
    :return fock: the fock matrix (spin-orbital basis)
    :return gtei: antisymmetrized two-electron integrals (spin-orbital basis)

    """

    # compute the Hartree-Fock energy and wave function
    scf_e, wfn = psi4.energy('SCF', return_wfn=True)

    # number of doubly occupied orbitals
    no   = wfn.nalpha()
    
    # total number of orbitals
    nmo     = wfn.nmo()
    
    # number of virtual orbitals
    nv   = nmo - no
    
    # orbital energies
    epsilon     = np.asarray(wfn.epsilon_a())
    
    # molecular orbitals (spatial):
    C = wfn.Ca()

    # use Psi4's MintsHelper to generate integrals
    mints = psi4.core.MintsHelper(wfn.basisset())

    # build the one-electron integrals
    H = np.asarray(mints.ao_kinetic()) + np.asarray(mints.ao_potential())
    H = np.einsum('uj,vi,uv', C, C, H)

    # unpack one-electron integrals in spin-orbital basis
    sH   = spatial_to_spin_orbital_oei(H,nmo,no)
    
    # build the two-electron integrals:
    tei = np.asarray(mints.mo_eri(C, C, C, C))

    # unpack two-electron integrals in spin-orbital basis
    stei = spatial_to_spin_orbital_tei(tei,nmo,no)

    # antisymmetrize g(ijkl) = <ij|kl> - <ij|lk> = (ik|jl) - (il|jk)
    gtei = np.einsum('ikjl->ijkl', stei) - np.einsum('iljk->ijkl', stei)

    # occupied, virtual slices
    n = np.newaxis
    o = slice(None, 2 * no)
    v = slice(2 * no, None)

    # build spin-orbital fock matrix
    fock = sH + np.einsum('piqi->pq', gtei[:, o, :, o])

    nsvirt = 2 * nv
    nsocc = 2 * no

    return nsocc, nsvirt, fock, gtei

def ccsd(mol, do_eom_ccsd = False):
    """

    run ccsd

    :param mol: a psi4 molecule
    :param do_eom_ccsd: do run eom-ccsd? default false
    :return cc_energy: the total ccsd energy

    """

    nsocc, nsvirt, fock, tei = get_integrals()
    
    # occupied, virtual slices
    n = np.newaxis
    o = slice(None, nsocc)
    v = slice(nsocc, None)

    # orbital energies
    row, col = fock.shape
    eps = np.zeros(row)
    for i in range(0,row):
        eps[i] = fock[i,i]

    # energy denominators
    e_abij = 1 / (-eps[v, n, n, n] - eps[n, v, n, n] + eps[n, n, o, n] + eps[
        n, n, n, o])
    e_ai = 1 / (-eps[v, n] + eps[n, o])

    # hartree-fock energy
    hf_energy = 1.0 * einsum('ii', fock[o, o]) -0.5 * einsum('ijij', tei[o, o, o, o])

    t1 = np.zeros((nsvirt, nsocc))
    t2 = np.zeros((nsvirt, nsvirt, nsocc, nsocc))
    t1, t2 = ccsd_iterations(t1, t2, fock, tei, o, v, e_ai, e_abij,
                      hf_energy, e_convergence=1e-10, r_convergence=1e-10, diis_size=8, diis_start_cycle=4)

    cc_energy = ccsd_energy(t1, t2, fock, tei, o, v)

    nuclear_repulsion_energy = mol.nuclear_repulsion_energy()

    print("")
    print("    CCSD Correlation Energy: {: 20.12f}".format(cc_energy - hf_energy))
    print("    CCSD Total Energy:       {: 20.12f}".format(cc_energy + nuclear_repulsion_energy))
    print("")

    if not do_eom_ccsd: 
        return cc_energy + nuclear_repulsion_energy

    # now eom-ccsd?
    print("    ==> EOM-CCSD <==")
    print("")
    from eom_ccsd import build_eom_ccsd_H

    # populate core list for super inefficicent implementation of CVS approximation
    core_list = []
    for i in range (0, nsocc):
        core_list.append(i)
    H = build_eom_ccsd_H(fock, tei, o, v, t1, t2, nsocc, nsvirt, core_list)

    print('    eigenvalues of e(-T) H e(T):')
    print('')

    print('    %5s %20s %20s' % ('state', 'total energy','excitation energy'))
    en, vec = np.linalg.eig(H)
    en.sort()
    for i in range (1,min(21,len(en))):
        print('    %5i %20.12f %20.12f' % ( i, en[i] + nuclear_repulsion_energy,en[i]-cc_energy ))

    print('')

    return cc_energy + nuclear_repulsion_energy

def ccsdt(mol):
    """

    run ccsdt

    :param mol: a psi4 molecule
    :return cc_energy: the total ccsdt energy

    """

    nsocc, nsvirt, fock, tei = get_integrals()
    
    # occupied, virtual slices
    n = np.newaxis
    o = slice(None, nsocc)
    v = slice(nsocc, None)

    # orbital energies
    row, col = fock.shape
    eps = np.zeros(row)
    for i in range(0,row):
        eps[i] = fock[i,i]

    # energy denominators
    e_abcijk = 1 / (-eps[v, n, n, n, n, n] - eps[n, v, n, n, n, n] - eps[n, n, v, n, n, n] + eps[n, n, n, o, n, n] + eps[n, n, n, n, o, n] + eps[n, n, n, n, n, o])
    e_abij = 1 / (-eps[v, n, n, n] - eps[n, v, n, n] + eps[n, n, o, n] + eps[n, n, n, o])
    e_ai = 1 / (-eps[v, n] + eps[n, o])

    # hartree-fock energy
    hf_energy = 1.0 * einsum('ii', fock[o, o]) -0.5 * einsum('ijij', tei[o, o, o, o])

    t1 = np.zeros((nsvirt, nsocc))
    t2 = np.zeros((nsvirt, nsvirt, nsocc, nsocc))
    t3 = np.zeros((nsvirt, nsvirt, nsvirt, nsocc, nsocc, nsocc))
    t1, t2, t3 = ccsdt_iterations(t1, t2, t3, fock, tei, o, v, e_ai, e_abij, e_abcijk,
                      hf_energy, e_convergence=1e-10, r_convergence=1e-10, diis_size=8, diis_start_cycle=4)

    #t1, t2 = ccsd_iterations(t1, t2, fock, tei, o, v, e_ai, e_abij,
    #                  hf_energy, e_convergence=1e-10, r_convergence=1e-10, diis_size=8, diis_start_cycle=4)

    cc_energy = ccsdt_energy(t1, t2, t3, fock, tei, o, v)

    nuclear_repulsion_energy = mol.nuclear_repulsion_energy()

    print("")
    print("    CCSDT Correlation Energy: {: 20.12f}".format(cc_energy - hf_energy))
    print("    CCSDT Total Energy:       {: 20.12f}".format(cc_energy + nuclear_repulsion_energy))
    print("")

    return cc_energy + nuclear_repulsion_energy

if __name__ == "__main__":
    main()
