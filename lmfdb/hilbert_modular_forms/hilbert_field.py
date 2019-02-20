# -*- coding: utf-8 -*-
r""" Class for interface with the 'field' component of the Hilbert Modular Form database.

Initial version (University of Warwick 2015) Aurel Page and John Cremona

"""

from sage.all import ZZ
from lmfdb import db
from lmfdb.WebNumberField import WebNumberField

def findvar(L):
    """
    Return the variable name from a collection of objects
    """
    for x in L:
        for c in x:
            if c.isalpha():
                return c.encode()
    return None

def str2fieldelt(F,strg):
    """Given a string strg representing an element of the number field F
    as a polynomial in its generator, return the number field element.

    F is the number field (in the correct variable)

    strg is a string representing an element of F
    """
    return F(strg.encode())

def str2ideal(F,strg):
    """Given a string strg representing an ideal of the number field F,
    return (N,n,I,gen) where I is the ideal, N its norm, n the least
    positive integer in I and gen a second generator.

    F is the number field (in the correct variable)

    strg is a string representing an ideal of F in the form '[N,n,gen]'
    """
    idlstr = strg[1:-1].replace(' ','').split(',')
    N = ZZ(idlstr[0]) #norm
    n = ZZ(idlstr[1]) #smallest integer
    gen = str2fieldelt(F,idlstr[2]) #other generator
    idl = F.ideal(n,gen)
    return N,n,idl,gen

def niceideals(F, ideals): #HNF + sage ideal + label
    """Convert a list of ideas from strongs to actual NumberField ideals

    F is a Sage NumberField

    ideals is a list of strings representing ideals I in the field, of
    the form [N,a,alpha] where N is the norm of I, a the least
    positive integer in I, and alpha a field element such that I is
    generated by a and alpha.

    The output is a list

    """
    nideals = []
    ilabel = 1
    norm = ZZ(0)
    for i in range(len(ideals)):
        N,n,idl,_ = str2ideal(F,ideals[i])
        assert idl.norm() == N and idl.smallest_integer() == n
        if N != norm:
            ilabel = ZZ(1)
            norm = N
        label = N.str() + '.' + ilabel.str()
        hnf = idl.pari_hnf().python()
        nideals.append([hnf, idl, label])
        ilabel += 1
    return nideals

def conjideals(ideals, auts): #(label,g) -> label
    cideals = {}
    from copy import copy
    ideals = copy(ideals)
    ideals.sort()
    for ig,g in enumerate(auts):
        gideals = copy(ideals)
        for I in gideals:
            I[0] = g(I[1]).pari_hnf().python()
        gideals.sort()
        for I,J in zip(ideals,gideals):
            cideals[(J[2],ig)] = I[2]
    return cideals



class HilbertNumberField(WebNumberField):
    """
    Subclass of WebNumberField which also facilitates extraction of
    the number field data stored in the Hilbert Modular Forms
    database.
    """
    def __init__(self, label):
        self.Fdata = db.hmf_fields.lookup(label)
        self.ideals = self.Fdata['ideals']
        self.primes = self.Fdata['primes']
        self.var = findvar(self.ideals)
        WebNumberField.__init__(self,label,gen_name=self.var)
        self.ideal_dict = {}
        self.label_dict = {}
        for I in self.ideals_iter():
            self.ideal_dict[I['label']]=I['ideal']
            self.label_dict[I['ideal']]=I['label']

    def _iter_ideals(self, primes=False, number=None):
        """
        Iterator through all ideals of self.  Delivers dicts with keys
        'label' and 'ideal'.
        """
        count = 0
        ilabel = 1
        norm = ZZ(0)
        ideals = self.ideals
        if primes:
            ideals = self.primes
        for idlstr in ideals:
            N,n,idl,_ = str2ideal(self.K(),idlstr)
            assert idl.norm() == N and idl.smallest_integer() == n
            if N != norm:
                ilabel = ZZ(1)
                norm = N
            label = N.str() + '.' + ilabel.str()
            yield {'label':label, 'ideal':idl}
            ilabel += 1
            count += 1
            if count==number:
                raise StopIteration

    def primes_iter(self, number=None):
        return self._iter_ideals(True,number)

    def ideals_iter(self, number=None):
        return self._iter_ideals(False,number)

    def ideal_label(self, idl):
        try:
            return self.label_dict[idl]
        except KeyError:
            return None

    def ideal(self, lab):
        try:
            return self.ideal_dict[lab]
        except KeyError:
            return None

    def prime_label(self, idl):
        return self.ideal_label(idl)
        # for I in self.primes_iter():
        #     if I['ideal']==idl:
        #         return I['label']
        # return None

    def prime(self, lab):
        return self.ideal(lab)
        # for I in self.primes_iter():
        #     if I['label']==lab:
        #         return I['ideal']
        # return None


