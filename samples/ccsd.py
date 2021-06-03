
import sys
sys.path.insert(0, './..')

import pdaggerq

ahat = pdaggerq.ahat_helper("fermi")
ahat.set_print_level(0)

# energy equation

ahat.set_bra("")

print('')
print('    < 0 | e(-T) H e(T) | 0> :')
print('')

ahat.add_st_operator(1.0,['f'],['t1','t2'])
ahat.add_st_operator(1.0,['v'],['t1','t2'])

ahat.simplify()

# grab list of fully-contracted strings, then print
energy_terms = ahat.fully_contracted_strings()
for my_term in energy_terms:
    print(my_term)

ahat.clear()

# singles equations

#ahat.set_bra("singles")
ahat.set_left_operators(['e1(m,e)'])

print('')
print('    < 0 | m* e e(-T) H e(T) | 0> :')
print('')

ahat.add_st_operator(1.0,['f'],['t1','t2'])
ahat.add_st_operator(1.0,['v'],['t1','t2'])

ahat.simplify()

# grab list of fully-contracted strings, then print
singles_residual_terms = ahat.fully_contracted_strings()
for my_term in singles_residual_terms:
    print(my_term)

ahat.clear()

# doubles equations

#ahat.set_bra("doubles")
ahat.set_left_operators(['e2(m,n,f,e)'])

print('')
print('    < 0 | m* n* f e e(-T) H e(T) | 0> :')
print('')

ahat.add_st_operator(1.0,['f'],['t1','t2'])
ahat.add_st_operator(1.0,['v'],['t1','t2'])

ahat.simplify()

# grab list of fully-contracted strings, then print
doubles_residual_terms = ahat.fully_contracted_strings()
for my_term in doubles_residual_terms:
    print(my_term)


ahat.clear()

