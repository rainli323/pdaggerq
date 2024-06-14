import pdaggerq

def main():

    ops = [['w0'], ['f'], ['v'], ['d+'], ['d-']]
    coeffs = [1.0, 1.0, 1.0, -1.0, -1.0]

    c_ops = [['B+'], ['B-']]
    c_coeffs = [1.0, 1.0]

    T = ['t2', 'u0', 'u1', 'u2']

    lproj = [
        # [['1']],
        [['e1(a,i)']],
        [['e2(i,j,b,a)']],
        [['B-']],
        [['B-', 'e1(i,a)']],
        [['B-', 'e2(i,j,b,a)']],
    ]
    rproj = [
        # [['1']],
        [['e1(a,i)']],
        [['e2(a,b,j,i)']],
        [['B+']],
        [['e1(a,i)', 'B+']],
        [['e2(a,b,j,i)', 'B+']],
    ]

    rproj_eqnames = ["sigmal1", "sigmal2", "sigmam0", "sigmam1", "sigmam2"]
    lproj_eqnames = ["sigmar1", "sigmar2", "sigmas0", "sigmas1", "sigmas2"]
    eqs = {}

    for i, R in enumerate(rproj):

        # set up pq
        pq = pdaggerq.pq_helper("fermi")
        L = [['l1'], ['l2'], ['m0'], ['m1'], ['m2']]

        rproj_eqname = rproj_eqnames[i]

        print("Deriving equation: ", f"{rproj_eqname} = <{L}| Hbar |{R}>", flush=True)

        # set projection operators
        pq.set_left_operators_type("EE")
        pq.set_left_operators(L)
        pq.set_right_operators(R)


        # add similarity transformed operators
        for j, op in enumerate(ops):
            pq.add_st_operator(coeffs[j], op, T)

        # simplify and block by spin
        pq.simplify()
        block_by_spin(pq, rproj_eqname, R, eqs)



        ### now do coherent state operators ###
        pq = pdaggerq.pq_helper("fermi")

        # get name of eq
        rproj_eqname = "c" + rproj_eqname
        print("Deriving equation: ", f"{rproj_eqname} = <{L}| B* + B |{R}>", flush=True)

        # set projection operators
        pq.set_left_operators_type("EE")
        pq.set_left_operators(L)
        pq.set_right_operators(R)

        # add similarity transformed operators
        for j, op in enumerate(c_ops):
            pq.add_st_operator(c_coeffs[j], op, T)

        # simplify and block by spin
        pq.simplify()
        block_by_spin(pq, rproj_eqname, R, eqs)

        # remove pq
        del pq

    for i, L in enumerate(lproj):
        # set up pq
        pq = pdaggerq.pq_helper("fermi")
        R = [['r1'], ['r2'], ['s0'], ['s1'], ['s2']]

        # get name of eq
        lproj_eqname = lproj_eqnames[i]
        print("Deriving equation: ", f"{lproj_eqname} = <{L}| Hbar |{R}>", flush=True)

        # set projection operators
        pq.set_left_operators(L)
        pq.set_right_operators_type("EE")
        pq.set_right_operators(R)


        # add similarity transformed operators
        for j, op in enumerate(ops):
            pq.add_st_operator(coeffs[j], op, T)

        # simplify and block by spin
        pq.simplify()
        block_by_spin(pq, lproj_eqname, L, eqs)

        ### now do coherent state operators ###
        pq = pdaggerq.pq_helper("fermi")

        # get name of eq
        lproj_eqname = "c" + lproj_eqname
        print("Deriving equation: ", f"{lproj_eqname} = <{L}| B* + B |{R}>", flush=True)

        # set projection operators
        pq.set_left_operators(L)
        pq.set_right_operators_type("EE")
        pq.set_right_operators(R)

        # add similarity transformed operators
        for j, op in enumerate(c_ops):
            pq.add_st_operator(c_coeffs[j], op, T)

        # simplify and block by spin
        pq.simplify()
        block_by_spin(pq, lproj_eqname, L, eqs)

        # remove pq
        del pq
    exit(0)

    # enable pq_graph
    graph = pdaggerq.pq_graph({
        'verbose':  True,
        'batched': True,
        'allow_merge': True,
        'use_trial_index': True,
        'conditions': {
            "u0": ["u0", "m0", "s0"],
            "u1": ["u1", "m1", "s1"],
            "u2": ["u2", "m2", "s2"]
        },
        'no_scalars': False,
        'nthreads': -1,
    })

    # add equations to graph
    for proj_eqname, eq in eqs.items():
        graph.add(eq, proj_eqname, ['a','b','i','j'])

    # optimize graph
    graph.optimize()
    graph.print("cpp")
    graph.analysis()
    graph.write_dot("qed_eom_ccsd.dot")

    return graph

def get_spin_labels(ops):
    spin_map = {}

    # make spin list using index
    labels = set()
    for op in ops:       
        for subop in op:
            if "(" not in subop:
                continue # no labels

            # get all labels in parentheses
            subop_labels = subop[subop.find("(")+1:subop.find(")")].split(",")
            for label in subop_labels:
                labels.add(label)

    # sort labels
    labels = sorted(labels)
    labels = list(labels)
    
    # block by spin (aaaa, abab, and bbbb)
    spin_types = None
    if len(labels) == 4:
        spin_types = ["aaaa", "abab", "bbbb"]
    elif len(labels) == 3:
        spin_types = ["aaa", "abb", "aba", "bbb"]
    elif len(labels) == 2:
        spin_types = ["aa", "bb"]
    elif len(labels) == 1:
        spin_types = ["a", "b"]
    elif len(labels) == 0:
        spin_types = []

    for spin in spin_types: 
        if len(labels) != len(spin):
            continue # incompatible spin


        # create dictionary mapping labels to spins
        label_to_spin = {}
        for i, label in enumerate(labels):
            label_to_spin[label] = spin[i]

        spin_map[spin] = label_to_spin

    return spin_map

def block_by_spin(pq, eqname, ops, eqs):
    spin_map = get_spin_labels(ops)
    print(f"    blocking by spin:", flush=True)
    for spins, label_to_spin in spin_map.items():
        print(f"        {spins} -> ", end="")
        for label, spin in label_to_spin.items():
            print(f"{label} -> {spin}", end=", ")
        print()
    print()
    for spins, label_to_spin in spin_map.items():

        # create name for equation
        spin_eqname = eqname + "_" + spins
        
        
        pq.block_by_spin(label_to_spin)
        eqs[spin_eqname] = pq
    
        terms = pq.fully_contracted_strings()
        for term in terms:
            print(term)
        print()

if __name__ == "__main__":
    main()
