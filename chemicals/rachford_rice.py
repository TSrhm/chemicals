r"""Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, 2017, 2018, 2019, 2020 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This module contains functions for solving the Rachford-Rice Equation. This is
used to solve ideal flashes, and is the inner loop of the sequential-substitution
flash algorithm. It is not used by full newton-algorithms. The
sequential-substitution is normally recommended because it does not suffer
from the ~N^3 behavior of solving a matrix.

For reporting bugs, adding feature requests, or submitting pull requests,
please use the `GitHub issue tracker <https://github.com/CalebBell/chemicals/>`_.

.. contents:: :local:

Two Phase - Interface
---------------------
.. autofunction:: chemicals.rachford_rice.flash_inner_loop
.. autofunction:: chemicals.rachford_rice.flash_inner_loop_methods
.. autodata:: chemicals.rachford_rice.flash_inner_loop_all_methods

Two Phase - Implementations
---------------------------
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution_LN2
.. autofunction:: chemicals.rachford_rice.Li_Johns_Ahmadi_solution
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution_Leibovici_Neoschil
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution_polynomial

Two Phase - High-Precision Implementations
------------------------------------------
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution_mpmath
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution_binary_dd
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution_Leibovici_Neoschil_dd

Three Phase
-----------
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solution2

N Phase
-------
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_solutionN

Two Phase Utility Functions
---------------------------
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_polynomial
.. autofunction:: chemicals.rachford_rice.Rachford_Rice_flash_error


Numerical Notes
---------------
For the two-phase problem, there are the following ways of computing the vapor
and liquid mole fractions once the vapor fraction and liquid fraction has
been computed:


The most commonly shown expression is:


.. math::
    x_i = \frac{z_i}{1 + \frac{V}{F}(K_i-1)}

This can cause numerical issues when :math:`K_i` is near 1. It also shows
issues near :math:`\frac{V}{F}(K_i-1) = -1`.

Another expression which avoids the second issue is

.. math::
    x_i = \frac{z_i}{\frac{L}{F} + (1 - \frac{L}{F})K_i}

Much like the other expression above this numerical issues but at different
conditions: :math:`\frac{L}{F} = 1` and :math:`\frac{L}{F} = -(1 - \frac{L}{F})K_i`.

One more expression using both liquid and vapor fraction is:

.. math::
    x_i = \frac{z_i}{K_i\frac{V}{F} + \frac{L}{F} }

This expression only has one problematic area: :math:`K_i\frac{V}{F} = \frac{L}{F}`.
Preferably, this is computed with a fused-multiply-add operation.

Another expression which flips the K value into the liquid form and swaps the
vapor fraction for the liquid fraction in-line is as follows

.. math::
    x_i = \frac{\frac{z_i}{K_i}}
    {\frac{\frac{L}{F}}{K_i} + \frac{V}{F}}

This also has numerical problems when :math:`-\frac{\frac{L}{F}}{K_i} = \frac{V}{F}`.

Even when computing a solution with high precision such as with `mpmath`,
the resulting compositions and phase fractions may fail basic tests. In the
following case, a nasty problem has a low-composition but relatively volatile
last component. Mathematically, :math:`1 = \frac{\frac{L}{F} x_i + \frac{V}{F} y_i}{z_i}`.
This is true for all components except the last one in this case, where
significant error exists.

>>> zs = [0.004632150100959984, 0.019748784459594933, 0.0037494212674659875, 0.0050492815033649835, 7.049818284201636e-05, 0.019252941309184937, 0.022923068733233923, 0.02751809363371991, 0.044055273670258854, 0.026348159124199914, 0.029384949788372902, 0.022368938441593926, 0.03876345111451487, 0.03440715821883388, 0.04220510198067186, 0.04109191458414686, 0.031180945124537895, 0.024703227642798916, 0.010618543295340965, 0.043262442161003854, 0.006774922650311977, 0.02418090788262392, 0.033168278052077886, 0.03325881573680989, 0.027794535589044905, 0.00302091746847699, 0.013693571363003955, 0.043274465132840854, 0.02431371852108292, 0.004119055065872986, 0.03314056562191489, 0.03926511182895087, 0.0305068048046159, 0.014495317922126952, 0.03603737707409988, 0.04346278949361786, 0.019715052322446934, 0.028565255195219907, 0.023343683279902924, 0.026532427286078915, 2.0833722372767433e-06]
>>> Ks = [0.000312001984979, 0.478348350355814, 0.057460349529956, 0.142866526725442, 0.186076915390803, 1.67832923245552, 0.010784509466239, 0.037204384948088, 0.005359146955631, 2.41896552551221, 0.020514598049597, 0.104545054017411, 2.37825397780443, 0.176463709057649, 0.000474240879865, 0.004738042026669, 0.02556030236928, 0.00300089652604, 0.010614774675069, 1.75142303167203, 1.47213647779132, 0.035773024794854, 4.15016401471676, 0.024475125100923, 0.00206952065986, 2.09173484409107, 0.06290795470216, 0.001537212006245, 1.16935817509767, 0.001830422812888, 0.058398776367331, 0.516860928072656, 1.03039372722559, 0.460775800103578, 0.10980302936483, 0.009883724220094, 0.021938589630783, 0.983011657214417, 0.01978995396409, 0.204144939961852, 14.0521979447538]
>>> LF, VF, xs, ys = Rachford_Rice_solution_mpmath(zs=zs, Ks=Ks)
>>> (LF*xs[-1] + VF*ys[-1])/zs[-1]
1.0000000000028162

"""


__all__ = ['Rachford_Rice_flash_error',
           'Rachford_Rice_solution', 'Rachford_Rice_polynomial',
           'Rachford_Rice_solution_polynomial', 'Rachford_Rice_solution_LN2',
           'Rachford_Rice_solution2', 'Rachford_Rice_solutionN',
           'Rachford_Rice_flashN_f_jac', 'Rachford_Rice_flash2_f_jac',
           'Li_Johns_Ahmadi_solution', 'flash_inner_loop',
           'flash_inner_loop_all_methods', 'flash_inner_loop_methods',
           'Rachford_Rice_solution_mpmath', 'Rachford_Rice_solution_binary_dd',
           'Rachford_Rice_solution_Leibovici_Neoschil',
           'Rachford_Rice_solution_Leibovici_Neoschil_dd']

from fluids.numerics import (
    IS_PYPY,
    add_dd,
    brenth,
    div_dd,
    gt_dd,
    halley,
    horner,
    horner_and_der,
    lt_dd,
    mul_dd,
    mul_noerrors_dd,
    newton,
    newton_system,
    one_10_epsilon_larger,
    one_10_epsilon_smaller,
    one_epsilon_larger,
    one_epsilon_smaller,
    py_solve,
    roots_cubic,
    roots_quartic,
    secant,
    solve_2_direct,
    solve_3_direct,
    solve_4_direct,
    exp, log
)
from fluids.numerics import numpy as np

from chemicals.exceptions import PhaseCountReducedError
from chemicals.utils import  mark_numba_incompatible, mark_numba_uncacheable

try:
    from itertools import combinations
except:
    pass


def Rachford_Rice_polynomial_3(zs, Cs):
    z0, z1, z2 = zs
    C0, C1, C2 = Cs
    x0 = C0*z0
    x1 = C1*z1
    x2 = C2*z2
    a_inv = 1.0/(C0*C1*C2*(z0 + z1 + z2))
    return [1.0,
            (C0*(x1+x2) + C1*(x0 + x2) + C2*(x0 + x1))*a_inv,
            (x0 + x1 + x2)*a_inv]

def Rachford_Rice_polynomial_4(zs, Cs):
    z0, z1, z2, z3 = zs
    C0, C1, C2, C3 = Cs
    x0 = C0*z0
    x1 = C1*x0
    x2 = C1*z1
    x3 = C0*x2
    x4 = C2*z2
    x5 = C0*x4
    x6 = C3*z3
    x7 = C0*x6
    x8 = C2*x0
    x9 = C2*x2
    x10 = C1*x4
    x11 = C1*x6
    a_inv = 1.0/(C0*C1*C2*C3) # z0 + z1 + z2 + z3 = 1
    x0_x2_x4 = x0 + x2 + x4
    t1 = x1 + x10 + x3 + x5 + x8 + x9
    return [1.0,
            (C1*(x5 + x7) + C2*(x1 + x11 + x3 + x7) + C3*t1)*a_inv,
            (C2*x6 + C3*x0_x2_x4 + t1 + x11 + x7)*a_inv,
            (x0_x2_x4 + x6)*a_inv]


def Rachford_Rice_polynomial_5(zs, Cs):
    z0, z1, z2, z3, z4 = zs
    C0, C1, C2, C3, C4 = Cs
    x0 = C0*z0
    x1 = C1*x0
    x2 = C2*x1
    x3 = C1*z1
    x4 = C0*x3
    x5 = C2*x4
    x6 = C2*z2
    x7 = C0*x6
    x8 = C1*x7
    x9 = C3*z3
    x10 = C0*x9
    x11 = C1*x10
    x12 = C4*z4
    x13 = C0*x12
    x14 = C1*x13
    x15 = C3*x1
    x16 = C3*x4
    x17 = C2*x0
    x18 = C3*x17
    x19 = C3*x7
    x20 = C2*x10
    x21 = C2*x13
    x22 = C2*x3
    x23 = C3*x22
    x24 = C1*x6
    x25 = C3*x24
    x26 = C1*x9
    x27 = C2*x26
    x28 = C1*x12
    x29 = C2*x28
    x30 = C3*x0
    x31 = C3*x3
    x32 = C3*x6
    x33 = C2*x9
    x34 = C2*x12
    a_inv = 1.0/(C0*C1*C2*C3*C4*(z0 + z1 + z2 + z3 + z4))
    b = (C2*x11 + C2*x14 + C3*x14 + C3*x2 + C3*x21 + C3*x29 + C3*x5 + C3*x8
         + C4*x11 + C4*x15 + C4*x16 + C4*x18 + C4*x19 + C4*x2 + C4*x20 + C4*x23
         + C4*x25 + C4*x27 + C4*x5 + C4*x8)*a_inv
    c = (C3*x13 + C3*x28 + C3*x34 + C4*x1 + C4*x10 + C4*x17 + C4*x22 + C4*x24
         + C4*x26 + C4*x30 + C4*x31 + C4*x32 + C4*x33 + C4*x4 + C4*x7 + x11
         + x14 + x15 + x16 + x18 + x19 + x2 + x20 + x21 + x23 + x25 + x27
         + x29 + x5 + x8)*a_inv
    d = (C3*x12 + C4*x0 + C4*x3 + C4*x6 + C4*x9 + x1 + x10 + x13 + x17 + x22
         + x24 + x26 + x28 + x30 + x31 + x32 + x33 + x34 + x4 + x7)*a_inv
    e = (x0 + x12 + x3 + x6 + x9)*a_inv
    return [1.0, b, c, d, e]


# _RR_poly_idx_cache = {}
def _Rachford_Rice_polynomial_coeff(value, zs, Cs, N):
#     global_list = []
#     # This part can be cached, so its performance implication is small
#     # I believe for high-N, this is causing out of memory errors
#     # However, even when using yield, still out-of-memories
#     def better_recurse(prev_value, max_value, working=None):
#         if working is None:
#             working = []
#         for i in range(prev_value, max_value):
#             if N == max_value:
# #                yield working + [i]
# #                return
#                 global_list.append(working + [i])
#             else:
#                 better_recurse(i + 1, max_value + 1, working + [i])
# #        return global_list
#
#     if (value, N) in _RR_poly_idx_cache:
#         global_list = _RR_poly_idx_cache[(value, N)]
#     else:
#         better_recurse(0, value)
#         _RR_poly_idx_cache[(value, N)] = global_list
#
#     zs_sum_mat = []
#     Cs_inv_mat = []
#     for i in range(N):
#         Cs_inv_list = []
#         zs_sum_list = []
#         for j in range(N):
#             if j > i:
#                 Cs_inv_list.append(None)
#                 zs_sum_list.append(None)
#             else:
#                 Cs_inv_list.append(Cs[i]*Cs[j])
#                 zs_sum_list.append(zs[i] + zs[j])
#         Cs_inv_mat.append(Cs_inv_list)
#         zs_sum_mat.append(zs_sum_list)
#     print(Cs_inv_mat)
#     Cs_inv_mat = [[Ci*Cj for Cj in Cs] for Ci in Cs]
#     zs_sum_mat = [[zi + zj for zj in zs] for zi in zs]

    # If there were some way to use cse this might work much faster
    # c = 0.0
    # for x in range(N):
    #     for y in range(x):
    #         c += (1.0 - zs[x] - zs[y])*(Cs[x]*Cs[y])
    # return c


    c = 0.0

    for idxs in combinations(list(range(N)), 1+N-value):
    #for idxs in global_list:
        C_msum = 1.0
        z_tot = 1.0
        for i in idxs:
            z_tot -= zs[i]
            C_msum *= Cs[i]
#         print(z_tot, C_msum, idxs)
#         C_msum = 1.0
#         z_tot = 1.0
#         l_idxs = len(idxs)
# #         # j is always larger than i only need half the matrixes
#         for i in range(0, l_idxs-1, 2):
#             i, j = idxs[i], idxs[i+1]
# #             print(j, i)
# #             print(j > i)
#             z_tot -= zs_sum_mat[j][i]
#             C_msum *= Cs_inv_mat[j][i]
#         if l_idxs & 1:
#             j = idxs[-1]
#             z_tot -= zs[j]
#             C_msum *= Cs[j]
        c += z_tot*C_msum
    return c


def Rachford_Rice_polynomial(zs, Ks):
    r'''Transforms the Rachford-Rice equation into a polynomial and returns
    its coefficients.
    A spelled-out solution is used for N from 2 to 5, derived with SymPy and
    optimized with the common sub expression approach.

    .. warning:: For large numbers of components (>20) this model performs
       terribly, though with future optimization it may be possible to have
       better performance.

    .. math::
        \sum_{i=1}^N z_i C_i\left[ \Pi_{j\ne i}^N \left(1 + \frac{V}{F}
        C_j\right)\right] = 0

    .. math::
        C_i = K_i - 1.0

    Once the above calculation is performed, it must be rearranged into
    polynomial form.

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]

    Returns
    -------
    coeffs : float
        Coefficients, with earlier coefficients corresponding to higher powers,
        [-]

    Notes
    -----
    Explicit calculations for any degree can be obtained with SymPy, changing
    N as desired:


    >>> from sympy import * # doctest: +SKIP
    >>> N = 4
    >>> Cs = symbols('C0:' + str(N)) # doctest: +SKIP
    >>> zs = symbols('z0:' + str(N)) # doctest: +SKIP
    >>> alpha = symbols('alpha') # doctest: +SKIP
    >>> tot = 0
    >>> for i in range(N): # doctest: +SKIP
    ...     mult_sum = 1
    >>> for j in range(N): # doctest: +SKIP
    ...     if j != i:
    ...         mult_sum *= (1 + alpha*Cs[j])
    ...     tot += zs[i]*Cs[i]*mult_sum

    poly_expr = poly(expand(tot), alpha)
    coeff_list = poly_expr.all_coeffs()
    cse(coeff_list, optimizations='basic')

    [1]_ suggests a matrix-math based approach for solving the model, but that
    has not been performed here. [1]_ also has explicit equations for
    up to N = 7 to derive the coefficients.

    The general form was derived to be slightly different than that in [1]_,
    but is confirmed to also be correct as it matches other methods for solving
    the Rachford-Rice equation. [2]_ has similar information to [1]_.

    The first coefficient is always 1.

    The approach is also discussed in [3]_, with one example.

    Examples
    --------
    >>> Rachford_Rice_polynomial(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    [1.0, -3.6926529966760824, 2.073518878815093]

    References
    ----------
    .. [1] Weigle, Brett D. "A Generalized Polynomial Form of the Objective
       Function in Flash Calculations." Pennsylvania State University, 1992.
    .. [2] Warren, John H. "Explicit Determination of the Vapor Fraction in
       Flash Calculations." Pennsylvania State University, 1991.
    .. [3] Monroy-Loperena, Rosendo, and Felipe D. Vargas-Villamil. "On the
       Determination of the Polynomial Defining of Vapor-Liquid Split of
       Multicomponent Mixtures." Chemical Engineering Science 56, no. 20
       (October 1, 2001): 5865-68.
       https://doi.org/10.1016/S0009-2509(01)00267-6.
    '''
    N = len(zs)
    Cs = [0.0]*N
    for i in range(N):
        Cs[i] = Ks[i] - 1.0
    if N == 2:
        C0, C1 = Cs
        z0, z1 = zs
        Cs[0] = 1.0
        Cs[1] = (C0*z0 + C1*z1)/(C0*C1*(z0 + z1))
        return Cs
    elif N == 3:
        return Rachford_Rice_polynomial_3(zs, Cs)
    elif N == 4:
        return Rachford_Rice_polynomial_4(zs, Cs)
    elif N == 5:
        return Rachford_Rice_polynomial_5(zs, Cs)

    Cs_inv = [0.0]*N
    for i in range(N):
        Cs_inv[i] = 1.0/Cs[i]
    #coeffs = [1.0]
    coeffs = [0.0]*N
    coeffs[0] = 1.0

#    if N > 2:
    c = 0.0
    for i in range(0, N):
        c += (1.0 - zs[i])*Cs_inv[i]
    coeffs[1] = c
    #coeffs.append(c)
    for v, i in zip(range(N - 1, 2, -1), range(2, N-1)):
        coeffs[i] = _Rachford_Rice_polynomial_coeff(v, zs, Cs_inv, N)


    # coeffs.extend([_Rachford_Rice_polynomial_coeff(v, zs, Cs_inv, N)
    #                 for v in range(N-1, 2, -1)])

    c = 0.0
    for i in range(0, N):
        C_sumprod = 1.0
        for j, C in enumerate(Cs_inv):
            if j != i:
                C_sumprod *= C
        c += zs[i]*C_sumprod
    coeffs[-1] = c
    return coeffs

def err_RR_poly(VF, poly):
    return horner(poly, VF)
def err_and_der_RR_poly(VF, poly):
    return horner_and_der(poly, VF)

@mark_numba_uncacheable
def Rachford_Rice_solution_polynomial(zs, Ks):
    r'''Solves the Rachford-Rice equation by transforming it into a polynomial,
    and then either analytically calculating the roots, or, using the known
    range the correct root is in, numerically solving for the correct
    polynomial root. The analytical solutions are used for N from 2 to 4.

    Uses the method proposed in [2]_ to obtain an initial guess when solving
    the polynomial for the root numerically.

    .. math::
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    .. warning:: : Using this function with more than 20 components is likely
       to crash Python! This model does not work well with many components!

    This method, developed first in [3]_ and expanded in [1]_, is clever but
    of little use for large numbers of components.

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]

    Returns
    -------
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    This approach has mostly been ignored by academia, despite some of its
    advantages.

    The initial guess is the average of the following, as described in [2]_.

    .. math::
        \left(\frac{V}{F}\right)_{min} = \frac{(K_{max}-K_{min})z_{of\;K_{max}}
        - (1-K_{min})}{(1-K_{min})(K_{max}-1)}

    .. math::
        \left(\frac{V}{F}\right)_{max} = \frac{1}{1-K_{min}}

    If the `newton` method does not converge, a bisection method (brenth) is
    used instead. However, it is somewhat slower, especially as newton will
    attempt 50 iterations before giving up.

    This method could be speed up somewhat for N <= 4; the checks for the
    vapor fraction range are not really needed.


    Examples
    --------
    >>> Rachford_Rice_solution_polynomial(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.6907302627738543, [0.33940869696634357, 0.3650560590371706, 0.2955352439964858], [0.5719036543882889, 0.27087159580558057, 0.15722474980613044])

    References
    ----------
    .. [1] Weigle, Brett D. "A Generalized Polynomial Form of the Objective
       Function in Flash Calculations." Pennsylvania State University, 1992.
    .. [2] Li, Yinghui, Russell T. Johns, and Kaveh Ahmadi. "A Rapid and Robust
       Alternative to Rachford-Rice in Flash Calculations." Fluid Phase
       Equilibria 316 (February 25, 2012): 85-97.
       doi:10.1016/j.fluid.2011.12.005.
    .. [3] Warren, John H. "Explicit Determination of the Vapor Fraction in
       Flash Calculations." Pennsylvania State University, 1991.
    '''
    N = len(zs)
    if N > 30: # numba: delete
        raise ValueError("Unlikely to solve") # numba: delete
    poly = Rachford_Rice_polynomial(zs, Ks)

    Kmin = min(Ks) # numba: delete
    Kmax = max(Ks)# numba: delete
    z_of_Kmax = zs[Ks.index(Kmax)]# numba: delete
#    Kmin, Kmax, z_of_Kmax = Ks[0], Ks[0], zs[0] # numba: uncomment
#    for i in range(N): # numba: uncomment
#        if Ks[i] > Kmax: # numba: uncomment
#            z_of_Kmax = zs[i] # numba: uncomment
#            Kmax = Ks[i] # numba: uncomment
#        if Ks[i] < Kmin: # numba: uncomment
#            Kmin = Ks[i] # numba: uncomment
    if Kmin > 1.0 or Kmax < 1.0:
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment

    V_over_F_min = ((Kmax-Kmin)*z_of_Kmax - (1.- Kmin))/((1.- Kmin)*(Kmax - 1.))
    V_over_F_max = 1./(1.-Kmin)

    if V_over_F_min < 0.0:
        V_over_F_min *= one_epsilon_larger
    else:
        V_over_F_min *= one_epsilon_smaller

    if V_over_F_max < 0.0:
        V_over_F_max *= one_epsilon_larger
    else:
        V_over_F_max *= one_epsilon_smaller


    if N > 5:
        # For safety, obtain limits of K
        x0 = 0.5*(V_over_F_min + V_over_F_max)

        found = False
        try:
            V_over_F = secant(err_RR_poly, x0, args=(poly,))
            found = True
            # V_over_F = secant(err, x0, low=V_over_F_min, high=V_over_F_max, bisection=True)
            # V_over_F = newton(err_and_der, x0, fprime=True, low=V_over_F_min, high=V_over_F_max, bisection=True)
            if V_over_F < V_over_F_min or V_over_F > V_over_F_max:
                found = False
        except:
            pass
        if not found:
            V_over_F = brenth(err_RR_poly, V_over_F_min, V_over_F_max, args=(poly,))
    else:
        if N == 4:
            coeffs = (poly[0], poly[1], poly[2], poly[3])
        elif N == 3:
            coeffs = (0.0, poly[0], poly[1], poly[2])
#            (0.0,) + tuple(poly)
        elif N == 2:
            coeffs = (0.0, 0.0, poly[0], poly[1])

#        roots = np.roots(poly) # numba: uncomment
        if N == 5: # numba: delete
            roots = roots_quartic(poly[0], poly[1], poly[2], poly[3], poly[4]) # numba: delete
        else: # numba: delete
            roots = roots_cubic(coeffs[0], coeffs[1], coeffs[2], coeffs[3]) # numba: delete
        if N == 2:
            V_over_F = roots[0]
        else:
            found = False
            for root in roots:
                if abs(root.imag) < 1e-9 and V_over_F_min <= root.real <= V_over_F_max:
#                if root.imag == 0.0 and V_over_F_min <= root <= V_over_F_max:
                    V_over_F = root.real
                    found = True
                    break
            if not found:
                raise ValueError("Bad roots")#, roots, "Root should be between V_over_F_min and V_over_F_max")

    xs = [0.0]*N
    ys = [0.0]*N
    for i in range(N):
        xs[i] = zs[i]/(1. + V_over_F*(Ks[i]-1.0))
        ys[i] = xs[i]*Ks[i]
    return V_over_F, xs, ys


def Rachford_Rice_flash_error(V_over_F, zs, Ks):
    r'''Calculates the objective function of the Rachford-Rice flash equation.
    This function should be called by a solver seeking a solution to a flash
    calculation. The unknown variable is `V_over_F`, for which a solution
    must be between 0 and 1.

    .. math::
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    Parameters
    ----------
    V_over_F : float
        Vapor fraction guess [-]
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]

    Returns
    -------
    error : float
        Deviation between the objective function at the correct V_over_F
        and the attempted V_over_F, [-]

    Notes
    -----
    The derivation is as follows:

    .. math::
        F z_i = L x_i + V y_i

    .. math::
        x_i = \frac{z_i}{1 + \frac{V}{F}(K_i-1)}

    .. math::
        \sum_i y_i = \sum_i K_i x_i = 1

    .. math::
        \sum_i(y_i - x_i)=0

    .. math::
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    This objective function was proposed in [1]_.

    Examples
    --------
    >>> Rachford_Rice_flash_error(0.5, zs=[0.5, 0.3, 0.2],
    ... Ks=[1.685, 0.742, 0.532])
    0.04406445591174976

    References
    ----------
    .. [1] Rachford, H. H. Jr, and J. D. Rice. "Procedure for Use of Electronic
       Digital Computers in Calculating Flash Vaporization Hydrocarbon
       Equilibrium." Journal of Petroleum Technology 4, no. 10 (October 1,
       1952): 19-3. doi:10.2118/952327-G.
    '''
    err = 0.0
    for i in range(len(zs)):
        err += zs[i]*(Ks[i] - 1.0)/(1.0 + V_over_F*(Ks[i] - 1.0))
    return err

def Rachford_Rice_err_fprime(V_over_F, zs_k_minus_1, zs_k_minus_1_2, K_minus_1):
    err0, err1 = 0.0, 0.0
    for num0, num1, Kim1 in zip(zs_k_minus_1, zs_k_minus_1_2, K_minus_1):
        VF_kim1_1_inv = 1.0/(1. + V_over_F*Kim1)
        err0 += num0*VF_kim1_1_inv
        err1 += num1*VF_kim1_1_inv*VF_kim1_1_inv
#            print(err0, V_over_F)
    return err0, err1

def Rachford_Rice_err_fprime2(V_over_F, zs_k_minus_1, zs_k_minus_1_2, zs_k_minus_1_3, K_minus_1):
    err0, err1, err2 = 0.0, 0.0, 0.0
    for num0, num1, num2, Kim1 in zip(zs_k_minus_1, zs_k_minus_1_2, zs_k_minus_1_3, K_minus_1):
        VF_kim1_1_inv = 1.0/(1. + V_over_F*Kim1)
        t2 = VF_kim1_1_inv*VF_kim1_1_inv
        err0 += num0*VF_kim1_1_inv
        err1 += num1*t2
        err2 += num2*t2*VF_kim1_1_inv
#            print(err0, err1, err2)
    # print(err0, V_over_F)
    return err0, err1, err2

def Rachford_Rice_err(V_over_F, zs_k_minus_1, K_minus_1):
    err = 0.0
    for i in range(len(zs_k_minus_1)):
        err += zs_k_minus_1[i]/(1. + V_over_F*K_minus_1[i])
    return err



@mark_numba_uncacheable
def Rachford_Rice_solution(zs, Ks, fprime=False, fprime2=False, guess=None):
    r'''Solves the objective function of the Rachford-Rice flash equation [1]_.
    Uses the method proposed in [2]_ to obtain an initial guess.

    .. math::
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]
    fprime : bool, optional
        Whether or not to use the first derivative of the objective function
        in the solver (Newton-Raphson is used) or not (secant is used), [-]
    fprime2 : bool, optional
        Whether or not to use the second derivative of the objective function
        in the solver (parabolic Halley`s method is used if True) or not, [-]
    guess : float, optional
        Optional initial guess for vapor fraction, [-]

    Returns
    -------
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    The initial guess is the average of the following, as described in [2]_.

    .. math::
        \left(\frac{V}{F}\right)_{min} = \frac{(K_{max}-K_{min})z_{of\;K_{max}}
        - (1-K_{min})}{(1-K_{min})(K_{max}-1)}

    .. math::
        \left(\frac{V}{F}\right)_{max} = \frac{1}{1-K_{min}}

    Another algorithm for determining the range of the correct solution is
    given in [3]_; [2]_ provides a narrower range however. For both cases,
    each guess should be limited to be between 0 and 1 as they are often
    negative or larger than 1.

    .. math::
        \left(\frac{V}{F}\right)_{min} = \frac{1}{1-K_{max}}

    .. math::
        \left(\frac{V}{F}\right)_{max} = \frac{1}{1-K_{min}}

    If the `newton` method does not converge, a bisection method (brenth) is
    used instead. However, it is somewhat slower, especially as newton will
    attempt 50 iterations before giving up.

    In all benchmarks attempted, secant method provides better performance than
    Newton-Raphson or parabolic Halley`s method. This may not be generally
    true; but it is for Python and SciPy's implementation. They are implemented
    for benchmarking purposes.

    The first and second derivatives are:

    .. math::
        \frac{d \text{ obj}}{d \frac{V}{F}} = \sum_i \frac{-z_i(K_i-1)^2}
        {(1 + \frac{V}{F}(K_i-1))^2}

    .. math::
        \frac{d^2 \text{ obj}}{d (\frac{V}{F})^2} = \sum_i \frac{2z_i(K_i-1)^3}
        {(1 + \frac{V}{F}(K_i-1))^3}

    Examples
    --------
    >>> Rachford_Rice_solution(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.6907302627738544, [0.33940869696634357, 0.3650560590371706, 0.2955352439964858], [0.5719036543882889, 0.27087159580558057, 0.15722474980613044])

    References
    ----------
    .. [1] Rachford, H. H. Jr, and J. D. Rice. "Procedure for Use of Electronic
       Digital Computers in Calculating Flash Vaporization Hydrocarbon
       Equilibrium." Journal of Petroleum Technology 4, no. 10 (October 1,
       1952): 19-3. doi:10.2118/952327-G.
    .. [2] Li, Yinghui, Russell T. Johns, and Kaveh Ahmadi. "A Rapid and Robust
       Alternative to Rachford-Rice in Flash Calculations." Fluid Phase
       Equilibria 316 (February 25, 2012): 85-97.
       doi:10.1016/j.fluid.2011.12.005.
    .. [3] Whitson, Curtis H., and Michael L. Michelsen. "The Negative Flash."
       Fluid Phase Equilibria, Proceedings of the Fifth International
       Conference, 53 (December 1, 1989): 51-71.
       doi:10.1016/0378-3812(89)80072-X.
    '''
    N = len(Ks)

    Kmin, Kmax, z_of_Kmax = 1e300, -1e300, 1e300
    for i in range(N):
        if zs[i] > 0.0:
            if Ks[i] > Kmax:
                z_of_Kmax = zs[i]
                Kmax = Ks[i]
            if Ks[i] < Kmin:
                Kmin = Ks[i]
    if Kmin > 1.0*(1-1e-15) or Kmax < 1.0*(1+1e-15):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment
    V_over_F_min = ((Kmax-Kmin)*z_of_Kmax - (1.- Kmin))/((1.- Kmin)*(Kmax- 1.))
    V_over_F_max = 1./(1.-Kmin)

    V_over_F_min2 = V_over_F_min
    V_over_F_max2 = V_over_F_max
    if guess is not None and guess > V_over_F_min and guess < V_over_F_max:
        x0 = guess
    else:
        x0 = (V_over_F_min2 + V_over_F_max2)*0.5

    K_minus_1 = [0.0]*N
    zs_k_minus_1 = [0.0]*N
    for i in range(N):
        Kim1 = Ks[i] - 1.0
        K_minus_1[i] = Kim1
        zs_k_minus_1[i] = zs[i]*Kim1

    if fprime or fprime2:
        zs_k_minus_1_2 = [0.0]*N
        for i in range(N):
            zs_k_minus_1_2[i] = -zs_k_minus_1[i]*K_minus_1[i]

    if fprime2:
        zs_k_minus_1_3 = [0.0]*N
        for i in range(N):
            zs_k_minus_1_3[i] = -2.0*zs_k_minus_1_2[i]*K_minus_1[i]

    try:
        low, high = V_over_F_min*one_epsilon_larger, V_over_F_max*one_epsilon_smaller
        if fprime2:
            V_over_F = halley(Rachford_Rice_err_fprime2, x0, ytol=1e-5, #fprime=True, fprime2=True,
                              high=high, low=low, bisection=True, args=(zs_k_minus_1, zs_k_minus_1_2, zs_k_minus_1_3, K_minus_1))
        elif fprime:
            V_over_F = newton(Rachford_Rice_err_fprime, x0, ytol=1e-12, fprime=True, high=high,
                              low=low, bisection=True, args=(zs_k_minus_1, zs_k_minus_1_2, K_minus_1))
        else:
#            print(V_over_F_max, V_over_F_min)
            V_over_F = secant(Rachford_Rice_err, x0, ytol=1e-5, xtol=1.48e-8, high=high,
                              low=low, bisection=True, require_xtol=True,
                              args=(zs_k_minus_1, K_minus_1))

#        assert V_over_F >= V_over_F_min2
#        assert V_over_F <= V_over_F_max2
    except:
        V_over_F = brenth(Rachford_Rice_err, low, high, args=(zs_k_minus_1, K_minus_1))

    xs = zs_k_minus_1
    ys = K_minus_1
    for i in range(N):
        xs[i] = zs[i]/(1. + V_over_F*K_minus_1[i])
        ys[i] = xs[i]*Ks[i]
    return V_over_F, xs, ys


def Rachford_Rice_numpy_err(V_over_F, zs_k_minus_1, K_minus_1):
    err = (zs_k_minus_1/(1.0 + V_over_F*K_minus_1)).sum()
#    return err # numba: uncomment
    return float(err) # numba: delete

def Rachford_Rice_numpy_err_fprime2(V_over_F, zs_k_minus_1, K_minus_1):
    x0 = 1.0/(K_minus_1*V_over_F + 1.0)

    err = zs_k_minus_1*x0
    fprime = -err*K_minus_1*x0
    fprime2 = -2.0*fprime*K_minus_1*x0
#    print(float(err.sum()), float(fprime.sum()), float(fprime2.sum()), V_over_F)
    return float(err.sum()), float(fprime.sum()), float(fprime2.sum())
#    return err.sum(), fprime.sum(), fprime2.sum()




@mark_numba_uncacheable
def Rachford_Rice_solution_numpy(zs, Ks, guess=None):
    """Undocumented version of Rachford_Rice_solution which works with numpy
    instead.

    Can be up to 15x faster for cases of 30000+ compounds; typically 7-10 x
    faster.
    """
    zs, Ks = np.array(zs), np.array(Ks) # numba: delete
    N = len(Ks)
    Kmin, Kmax, z_of_Kmax = 1e300, -1e300, 1e300
    for i in range(N):
        if zs[i] > 0.0:
            if Ks[i] > Kmax:
                z_of_Kmax = zs[i]
                Kmax = Ks[i]
            if Ks[i] < Kmin:
                Kmin = Ks[i]
    if Kmin > 1.0*(1-1e-15) or Kmax < 1.0*(1+1e-15):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment

    V_over_F_min = ((Kmax-Kmin)*z_of_Kmax - (1.-Kmin))/((1.-Kmin)*(Kmax-1.))
    V_over_F_max = 1./(1.-Kmin)

    if V_over_F_min < 0.0:
        V_over_F_min *= one_epsilon_larger
    else:
        V_over_F_min *= one_epsilon_smaller

    if V_over_F_max < 0.0:
        V_over_F_max *= one_epsilon_larger
    else:
        V_over_F_max *= one_epsilon_smaller

#    , one_epsilon_larger

    V_over_F_min2 = V_over_F_min
    V_over_F_max2 = V_over_F_max
    if guess is not None and guess > V_over_F_min and guess < V_over_F_max:
        x0 = guess
    else:
        x0 = (V_over_F_min2 + V_over_F_max2)*0.5


    K_minus_1 = Ks - 1.0
    zs_k_minus_1 = zs*K_minus_1

    try:
        V_over_F = halley(Rachford_Rice_numpy_err_fprime2, x0, high=V_over_F_max*one_epsilon_smaller,
                          low=V_over_F_min*one_epsilon_larger, xtol=1e-13, args=(zs_k_minus_1, K_minus_1),
                          bisection=True)
    except:
        V_over_F = brenth(Rachford_Rice_numpy_err, V_over_F_max*one_epsilon_smaller, V_over_F_min*one_epsilon_larger,
                          args=(zs_k_minus_1, K_minus_1))

    xs = zs/(1.0 + V_over_F*K_minus_1)
    ys = Ks*xs
#    return V_over_F, xs, ys # numba: uncomment
    return float(V_over_F), xs.tolist(), ys.tolist() # numba: delete

def Rachford_Rice_err_fprime_Leibovici_Neoschil_dd(VF_r, VF_e, zs_k_minus_1_r, zs_k_minus_1_e,
                                                   zs_k_minus_1_r_2_r, zs_k_minus_1_r_2_e,
                                                   Km1r, Km1e, VF_min_r, VF_min_e, VF_max_r, VF_max_e):
    plain_errr, plain_erre, plan_diffr, plan_diffe = 0.0, 0.0, 0.0, 0.0

    for i in range(len(zs_k_minus_1_r)):
        denr, dene = mul_dd(VF_r, VF_e, Km1r[i], Km1e[i])
        denr, dene = add_dd(1.0, 0.0, denr, dene)
        VF_kim1_1_invr, VF_kim1_1_inve = div_dd(1.0, 0.0, denr, dene)
        tmpr, tmpe = mul_dd(zs_k_minus_1_r[i], zs_k_minus_1_e[i], VF_kim1_1_invr, VF_kim1_1_inve)

        # Add the error to the summation variables
        plain_errr, plain_erre = add_dd(plain_errr, plain_erre, tmpr, tmpe)

        tmpr, tmpe = mul_dd(VF_kim1_1_invr, VF_kim1_1_inve, VF_kim1_1_invr, VF_kim1_1_inve)
        tmpr, tmpe = mul_dd(zs_k_minus_1_r_2_r[i], zs_k_minus_1_r_2_e[i], tmpr, tmpe)

        # Add the error to the derivative variables
        plan_diffr, plan_diffe = add_dd(plan_diffr, plan_diffe, tmpr, tmpe)

    # err = (V_over_F - V_over_F_min)*(V_over_F_max - V_over_F)*plain_err
    errr, erre = add_dd(VF_r, VF_e, -VF_min_r, -VF_min_e)
    tmpr, tmpe = add_dd(VF_max_r, VF_max_e, -VF_r, -VF_e)
    errr, erre = mul_dd(errr, erre, tmpr, tmpe)
    errr, erre = mul_dd(errr, erre, plain_errr, plain_erre)

    fprimer, fprimee = add_dd(-VF_r, -VF_e, VF_max_r, VF_max_e)
    fprimer, fprimee = mul_dd(plan_diffr, plan_diffe, fprimer, fprimee)

    tmpr, tmpe = add_dd(VF_r, VF_e, -VF_min_r, -VF_min_e)
    # This line finishes plan_diff*(-VF_r + VF_max_r)*(VF_r - VF_min_r)
    fprimer, fprimee = mul_dd(tmpr, tmpe, fprimer, fprimee)


    tmpr, tmpe = add_dd(-VF_r, -VF_e, VF_max_r, VF_max_e)
    tmpr, tmpe = mul_dd(tmpr, tmpe, plain_errr, plain_erre)
    # This line finishes adding + plain_err*(-VF_r + VF_max_r)
    fprimer, fprimee = add_dd(tmpr, tmpe, fprimer, fprimee)

    tmpr, tmpe = add_dd(-VF_r, -VF_e, VF_min_r, VF_min_e)
    tmpr, tmpe = mul_dd(tmpr, tmpe, plain_errr, plain_erre)

    # This line finishes adding + plain_err*(-VF_r + VF_min_r)
    fprimer, fprimee = add_dd(tmpr, tmpe, fprimer, fprimee)

    return errr, erre, fprimer, fprimee



def Rachford_Rice_err_fprime_Leibovici_Neoschil(V_over_F, zs_k_minus_1, zs_k_minus_1_2, K_minus_1, V_over_F_min, V_over_F_max):
    plain_err, plan_diff = 0.0, 0.0
    for num0, num1, Kim1 in zip(zs_k_minus_1, zs_k_minus_1_2, K_minus_1):
        VF_kim1_1_inv = 1.0/(1. + V_over_F*Kim1)
        plain_err += num0*VF_kim1_1_inv
        plan_diff += num1*VF_kim1_1_inv*VF_kim1_1_inv
    err = (V_over_F - V_over_F_min)*(V_over_F_max - V_over_F)*plain_err
    fprime = (plan_diff*(-V_over_F + V_over_F_max)*(V_over_F - V_over_F_min)
              + plain_err*(-V_over_F + V_over_F_max)
              + plain_err*(-V_over_F + V_over_F_min))
    # print(err, V_over_F)
    return err, fprime


@mark_numba_uncacheable
def Rachford_Rice_solution_Leibovici_Neoschil(zs, Ks, guess=None):
    r'''Solves the objective function of the Rachford-Rice flash equation as
    modified by Leibovici and Neoschil. This modification helps
    convergence near the vapor fraction boundaries only; it slows
    convergence in other regions.

    .. math::
        \left(\frac{V}{F} - \alpha_L\right)\left(\alpha_R - \frac{V}{F}\right)
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    .. math::
        \alpha_L = - \frac{1}{K_{max} - 1}

    .. math::
        \alpha_R = \frac{1}{1 - K_{min}}

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]
    guess : float, optional
        Optional initial guess for vapor fraction, [-]

    Returns
    -------
    L_over_F : float
        Liquid fraction solution [-]
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    The initial guess is the average of the following.

    .. math::
        \left(\frac{V}{F}\right)_{min} = \frac{(K_{max}-K_{min})z_{of\;K_{max}}
        - (1-K_{min})}{(1-K_{min})(K_{max}-1)}

    .. math::
        \left(\frac{V}{F}\right)_{max} = \frac{1}{1-K_{min}}

    Examples
    --------
    >>> Rachford_Rice_solution_Leibovici_Neoschil(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.3092697372261, 0.69073026277385, [0.339408696966343, 0.36505605903717, 0.29553524399648], [0.57190365438828, 0.270871595805580, 0.157224749806130])

    References
    ----------
    .. [1] Leibovici, ClaudeF., and Jean Neoschil. "A New Look at the
       Rachford-Rice Equation." Fluid Phase Equilibria 74 (July 15, 1992):
       303-8. https://doi.org/10.1016/0378-3812(92)85069-K.
    '''
    N = len(Ks)
    Kmin, Kmax, z_of_Kmax = 1e300, -1e300, 1e300
    for i in range(N):
        if zs[i] > 0.0:
            if Ks[i] > Kmax:
                z_of_Kmax = zs[i]
                Kmax = Ks[i]
            if Ks[i] < Kmin:
                Kmin = Ks[i]
    if Kmin > 1.0*(1-1e-15) or Kmax < 1.0*(1+1e-15):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment
    V_over_F_min = ((Kmax-Kmin)*z_of_Kmax - (1.- Kmin))/((1.- Kmin)*(Kmax- 1.))
    V_over_F_min_LN = -1.0/(Kmax-1) # There is a special lower limit to use for this method
    V_over_F_max = 1./(1.-Kmin)

    if guess is not None and guess > V_over_F_min and guess < V_over_F_max:
        x0 = guess
    else:
        x0 = (V_over_F_min + V_over_F_max)*0.5

    # Pre-compute as much as we can to speedup the slower solve of the
    # error equation
    K_minus_1 = [0.0]*N
    zs_k_minus_1 = [0.0]*N
    zs_k_minus_1_2 = [0.0]*N
    for i in range(N):
        Kim1 = Ks[i] - 1.0
        K_minus_1[i] = Kim1
        zs_k_minus_1[i] = zs[i]*Kim1
        zs_k_minus_1_2[i] = -zs_k_minus_1[i]*K_minus_1[i]

    # Right the boundaries, the derivative goes very large and microscopic steps are made and the newton solver switches
    # The boundaries need to be handled with bisection-style solvers
    # The 1e-15 tolerance is able to be found with the 10*epsilon limits.
    low, high = V_over_F_min*one_10_epsilon_larger, V_over_F_max*one_10_epsilon_smaller
    V_over_F = newton(Rachford_Rice_err_fprime_Leibovici_Neoschil, x0, xtol=1e-15, ytol=1e-5, fprime=True, high=high,
                        low=low, bisection=True, args=(zs_k_minus_1, zs_k_minus_1_2, K_minus_1, V_over_F_min_LN, V_over_F_max))

    # For maximum accuracy, the equation should be re-solved to obtain 16 digits
    # of precision for the liquid fraction
    # Fortunately, we have an extremely good guess.
    # We can re-use the same arrays.
    for i in range(N):
        Kim1 = 1.0/Ks[i] - 1.0
        K_minus_1[i] = Kim1
        zs_k_minus_1[i] = zs[i]*Kim1
        zs_k_minus_1_2[i] = -zs_k_minus_1[i]*K_minus_1[i]

    # Translate the limits, noting that Kmin and Kmax are their inverses
    # and they trade places.
    x0 = 1.0 - V_over_F
    L_over_F_min_LN = -1.0/(1/Kmin-1)
    L_over_F_max = 1./(1.-1/Kmax)
    # Try to polish it but do not require a ytol, but do allow it to exit on hitting a boundary or there being a large ytol error.
    LF = newton(Rachford_Rice_err_fprime_Leibovici_Neoschil, x0, xtol=1e-15, ytol=1e100, fprime=True, high=x0+1e-4,
                    low=x0-1e-4, bisection=True, args=(zs_k_minus_1, zs_k_minus_1_2, K_minus_1, L_over_F_min_LN, L_over_F_max))

    xs = zs_k_minus_1
    ys = K_minus_1
    for i in range(N):
        K_minus_1 = Ks[i] - 1.0
            # Attempt to avoid truncation error by using the liquid fraction
            # some of the time.
        switch = -1.001 < V_over_F*K_minus_1 < -0.999
        if switch:
            xs[i] = zs[i]/(LF + (1.0 - LF)*Ks[i])
        else:
            xs[i] = zs[i]/(1. + V_over_F*K_minus_1)

        # xs[i] = zs[i]/(Ks[i]*V_over_F + LF)
        # xs[i] = zs[i]/fma(Ks[i],V_over_F, LF)

    # The following trick can ensure the compositions sum to 1; small precision
    # gain but sometimes a large error can still exist.
    i_max_x = xs.index(max(xs))# numba: delete

#    max_x = 0  # numba: uncomment
#    i_max_x = 0 # numba: uncomment
#    for i in range(N): # numba: uncomment
#        if xs[i] > max_x: # numba: uncomment
#            max_x = xs[i] # numba: uncomment
#            i_max_x = i # numba: uncomment


    x_sum = sum(xs)
    xs[i_max_x] = xs[i_max_x]  + (1.0-x_sum)

    for i in range(N):
        ys[i] = xs[i]*Ks[i]
    return LF, V_over_F, xs, ys


@mark_numba_uncacheable
def Rachford_Rice_solution_Leibovici_Neoschil_dd(zs, Ks, guess=None):
    r'''Solves the objective function of the Rachford-Rice flash equation as
    modified by Leibovici and Neoschil, using double-double precision math
    for maximum accuracy. For most cases, this function will return
    bit-for-bit accurate results; but there are pathological inputs where
    error still occurs.

    .. math::
        \left(\frac{V}{F} - \alpha_L\right)\left(\alpha_R - \frac{V}{F}\right)
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    .. math::
        \alpha_L = - \frac{1}{K_{max} - 1}

    .. math::
        \alpha_R = \frac{1}{1 - K_{min}}

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]
    guess : float, optional
        Optional initial guess for vapor fraction, [-]

    Returns
    -------
    L_over_F : float
        Liquid fraction solution [-]
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    The initial guess is the average of the following.

    .. math::
        \left(\frac{V}{F}\right)_{min} = \frac{(K_{max}-K_{min})z_{of\;K_{max}}
        - (1-K_{min})}{(1-K_{min})(K_{max}-1)}

    .. math::
        \left(\frac{V}{F}\right)_{max} = \frac{1}{1-K_{min}}

    Examples
    --------
    >>> Rachford_Rice_solution_Leibovici_Neoschil_dd(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.3092697372261, 0.69073026277385, [0.339408696966343, 0.36505605903717, 0.29553524399648], [0.57190365438828, 0.270871595805580, 0.157224749806130])

    References
    ----------
    .. [1] Leibovici, ClaudeF., and Jean Neoschil. "A New Look at the
       Rachford-Rice Equation." Fluid Phase Equilibria 74 (July 15, 1992):
       303-8. https://doi.org/10.1016/0378-3812(92)85069-K.
    '''
    N = len(Ks)
    if N == 2:
        return Rachford_Rice_solution_binary_dd(zs, Ks)
    Kmin, Kmax, z_of_Kmax = 1e300, -1e300, 1e300
    for i in range(N):
        if zs[i] > 0.0:
            if Ks[i] > Kmax:
                z_of_Kmax = zs[i]
                Kmax = Ks[i]
            if Ks[i] < Kmin:
                Kmin = Ks[i]
    if Kmin > 1.0*(1-1e-15) or Kmax < 1.0*(1+1e-15):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment

    numr, nume = add_dd(Kmax, 0, -Kmin, 0)
    numr, nume = mul_dd(numr, nume, z_of_Kmax, 0)
    tmpr, tmpe = add_dd(1.0, 0.0, -Kmin, 0.0)
    numr, nume = add_dd(numr, nume, -tmpr, -tmpe)

    denr, dene = add_dd(1.0, 0, -Kmin, 0)
    tmpr, tmpe = add_dd(Kmax, 0.0, -1.0, 0.0)
    denr, dene = mul_dd(denr, dene, tmpr, tmpe)
    VFminr, VFmine = div_dd(numr, nume, denr, dene)

    denr, dene = add_dd(Kmax, 0, -1.0, 0.0)
    VFminLNr, VFminLNe = div_dd(-1.0, 0.0, denr, dene)

    denr, dene = add_dd(1.0, 0, -Kmin, 0.0)
    VFmaxr, VFmaxe = div_dd(1.0, 0.0, denr, dene)

    if guess is not None and guess > VFminr and guess < VFmaxr:
        x0 = guess
    else:
        try:
            # Try to obtain an initial guess for speed and convergence from the
            # other solvers
            x0, _, _ = Rachford_Rice_solution_LN2(zs, Ks)
        except:
            x0 = 0.5*(VFminr + VFmaxr)



    # Pre-compute as much as we can to speedup the slower solve of the
    # error equation
    K_minus_1r = [0.0]*N
    K_minus_1e = [0.0]*N

    zs_k_minus_1r = [0.0]*N
    zs_k_minus_1e = [0.0]*N

    zs_k_minus_1_2r = [0.0]*N
    zs_k_minus_1_2e = [0.0]*N
    for i in range(N):
        Kim1r, Kim1e = add_dd(Ks[i], 0.0, -1.0, 0.0)
        K_minus_1r[i] = Kim1r
        K_minus_1e[i] = Kim1e

        z_k_minus_1r, z_k_minus_1e = mul_dd(zs[i], 0.0, Kim1r, Kim1e)

        zs_k_minus_1r[i] = z_k_minus_1r
        zs_k_minus_1e[i] = z_k_minus_1e

        z_k_minus_1_2r, z_k_minus_1_2e = mul_dd(z_k_minus_1r, z_k_minus_1e, -Kim1r, -Kim1e)
        zs_k_minus_1_2r[i] = z_k_minus_1_2r
        zs_k_minus_1_2e[i] = z_k_minus_1_2e
    VFr = x0
    VFe = 0.0

    VF_minr, VF_mine = VFminr, VFmine
    VF_maxr, VF_maxe = VFmaxr, VFmaxe

    for it in range(100):
        errr, erre, fprimer, fprimee = Rachford_Rice_err_fprime_Leibovici_Neoschil_dd(VFr, VFe,
                                                                zs_k_minus_1r, zs_k_minus_1e, zs_k_minus_1_2r, zs_k_minus_1_2e,
                                                       K_minus_1r, K_minus_1e, VFminLNr, VFminLNe, VFmaxr, VFmaxe)
        if errr > 0.0:
            VF_minr, VF_mine = VFr, VFe
        else:
            VF_maxr, VF_maxe = VFr, VFe

        stepe, stepr = div_dd(errr, erre, fprimer, fprimee)
        VFr, VFe = add_dd(VFr, VFe, -stepe, -stepr)

        # Do a bisection step if we are outside of the bounds
        if lt_dd(VFr, VFe, VF_minr, VF_mine) or gt_dd(VFr, VFe, VF_maxr, VF_maxe):
            VFr, VFe = add_dd(VF_minr, VF_mine, VF_maxr, VF_maxe)
            VFr, VFe = mul_dd(0.5, 0.0, VFr, VFe)

        if abs(errr) < 1e-25:
            break
    # if it > 30:
    #     print(f'zs={zs}')
    #     print(f'Ks={Ks}')
    #     1/0

    LFr, LFe = add_dd(1.0, 0.0, -VFr, -VFe)

    xs = zs_k_minus_1_2r
    ys = zs_k_minus_1_2e
    for i in range(N):
        # Should not be necessary and does not help numba
        # switch = -1.001 < VFr*(Ks[i]-1) < -0.999
        # if switch:
        #     # xs[i] = zs[i]/(LF + (1.0 - LF)*Ks[i])
        #     denr, dene = add_dd(1.0, 0, -LFr, -LFe)
        #     denr, dene = mul_dd(denr, dene, Ks[i], 0.0)
        #     denr, dene = add_dd(denr, dene, LFr, LFe)
        #     xir, xie = div_dd(zs[i], 0.0, denr, dene)
        # else:
        # xi = zs[i]/(1.0 + V_over_F*(Ks[i] - 1.0))
        K_minus_1r, K_minus_1e = add_dd(Ks[i], 0, -1.0, 0)
        denr, dene = mul_dd(K_minus_1r, K_minus_1e, VFr, VFe)
        denr, dene = add_dd(1.0, 0, denr, dene)
        xir, xie = div_dd(zs[i], 0.0, denr, dene)

        xs[i] = xir
        yir, yie = mul_dd(xir, xie, Ks[i], 0.0)
        ys[i] = yir

    return LFr, VFr, xs, ys

def Rachford_Rice_solution_binary_dd(zs, Ks):
    r'''Solves the the Rachford-Rice flash equation for a binary system using
    double-double math. This increases the range in which the
    calculation can be performed accurately but does not totally eliminate
    error.

    .. math::
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    The analytical solution for a binary system is:

    .. math::
        \frac{V}{F} = \frac{- K_{0} z_{0} - K_{1} z_{1} + z_{0} + z_{1}}
        {K_{0} K_{1} z_{0} + K_{0} K_{1} z_{1} - K_{0} z_{0} - K_{0} z_{1}
         - K_{1} z_{0} - K_{1} z_{1} + z_{0} + z_{1}}

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]

    Returns
    -------
    L_over_F : float
        Liquid fraction solution [-]
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----

    Examples
    --------
    This system with large volatility difference and a trace of a component
    shows a correct calculation. Try it out with other solvers for bad results!

    >>> Rachford_Rice_solution_binary_dd(zs=[1E-27, 1.0], Ks=[1000000000000,0.1])
    (1.000000000001, -1.0000000000009988e-12, [9.0000000000009e-13, 0.9999999999991], [0.90000000000009, 0.09999999999991001])

    Note the limitations of this solver can be explored by comparing against
    :obj:`Rachford_Rice_solution_mpmath`. For example, with `z0` of 1e-28
    in the above example error creeps back in.

    '''
    if len(zs) != 2:
        raise ValueError("This solution method works on two components only")
    z0, z1 = zs
    K0, K1 = Ks
    if (K0 < 1.0 and K1 < 1.0) or (K0 > 1.0 and K1 > 1.0):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#                raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment
    l = 2
    xs = [0.0]*l
    ys = [0.0]*l

    z0z1r, z0z1e = add_dd(z0, 0.0, z1, 0.0)
    K0z0r, K0z0e = mul_noerrors_dd(K0, z0)
    K1z1r, K1z1e = mul_noerrors_dd(K1, z1)

    tempr, tempe = add_dd(z0z1r, z0z1e, -K0z0r, -K0z0e)
    t0r, t0e = add_dd(tempr, tempe, -K1z1r, -K1z1e)

    tempr, tempe = mul_dd(K1, 0.0, K0z0r, K0z0e)
    denr, dene = add_dd(t0r, t0e, tempr, tempe)
    tempr, tempe = mul_dd(K0, 0.0, K1z1r, K1z1e)
    denr, dene = add_dd(denr, dene, tempr, tempe)
    tempr, tempe = mul_noerrors_dd(K0, z1)
    denr, dene = add_dd(denr, dene, -tempr, -tempe)
    tempr, tempe = mul_noerrors_dd(K1, z0)
    denr, dene = add_dd(denr, dene, -tempr, -tempe)
    V_over_Fr, V_over_Fe = div_dd(t0r, t0e, denr, dene)
    L_over_Fr, L_over_Fe = add_dd(1.0, 0.0, -V_over_Fr, -V_over_Fe)

    # Compute x0
    denr, dene = add_dd(K0, 0.0, -1.0, 0.0)
    denr, dene = mul_dd(V_over_Fr, V_over_Fe, denr, dene)
    denr, dene = add_dd(1.0, 0.0, denr, dene)
    x0r, x0e = div_dd(z0, 0.0, denr, dene)
    # Compute x1 from the balance since we are higher precision
#     x1r, x1e = add_dd(1.0, 0.0, -x0r, -x0e)
    # it usually works but sometimes causes issues; beter to compute it with the slow way
    denr, dene = add_dd(K1, 0.0, -1.0, 0.0)
    denr, dene = mul_dd(V_over_Fr, V_over_Fe, denr, dene)
    denr, dene = add_dd(1.0, 0.0, denr, dene)
    x1r, x1e = div_dd(z1, 0.0, denr, dene)

    # Compute y0 and y1
    y0r, y0e = mul_dd(x0r, x0e, K0, 0.0)
    y1r, y1e = mul_dd(x1r, x1e, K1, 0.0)

    xs[0] = x0r
    xs[1] = x1r
    ys[0] = y0r
    ys[1] = y1r
    return L_over_Fr, V_over_Fr, xs, ys


@mark_numba_incompatible
def Rachford_Rice_solution_mpmath(zs, Ks, dps=200, tol=1e-100):
    r'''Solves the the Rachford-Rice flash equation using numerical
    root-finding to a high precision using the `mpmath` library.

    .. math::
        \sum_i \frac{z_i(K_i-1)}{1 + \frac{V}{F}(K_i-1)} = 0

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]
    dps : int, optional
        Number of decimal places to use in the intermediate values of the
        calculation, [-]
    tol : float, optional
        The tolerance of the solver used in `mpmath`, [-]

    Returns
    -------
    L_over_F : float
        Liquid fraction solution [-]
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    This function is written solely for development purposes with the aim
    of returning bit-accurate solutions.

    Note that the liquid fraction is also returned; it is insufficient to
    compute it as :math:`\frac{L}{F} = 1 - \frac{V}{F}`.

    Examples
    --------
    >>> Rachford_Rice_solution_mpmath(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.3092697372261456, 0.6907302627738544, [0.33940869696634357, 0.3650560590371706, 0.29553524399648584], [0.5719036543882889, 0.27087159580558057, 0.15722474980613046])
    >>> Rachford_Rice_solution_mpmath(zs=[0.999999999999, 1e-12], Ks=[2.0, 1e-12])
    (1e-12, 0.999999999999, [0.49999999999975003, 0.50000000000025], [0.9999999999995001, 5.0000000000025e-13])
    '''
    # extremely important to validate high decimal precision with mpmath
    # numerical issues make this an open research problem with respect to maintaining speed
    from mpmath import mp, mpf

    mp.dps = dps
    N = len(zs)

    def make_objf(zs_k_minus_1, K_minus_1):
        def Rachford_Rice_err(V_over_F):
            # Compute the objective function
            err = 0
            for i in range(len(zs_k_minus_1)):
                err += zs_k_minus_1[i]/(1 + V_over_F*K_minus_1[i])
            return err
        return Rachford_Rice_err

    def make_objf_der(zs_k_minus_1, zs_k_minus_1_2, K_minus_1):
        def Rachford_Rice_err_fprime(V_over_F):
            # Compute the objective function and its derivative w.r.t. V_over_F
            err0, err1 = 0, 0
            for num0, num1, Kim1 in zip(zs_k_minus_1, zs_k_minus_1_2, K_minus_1):
                VF_kim1_1_inv = 1/(1 + V_over_F*Kim1)
                err0 += num0*VF_kim1_1_inv
                err1 += num1*VF_kim1_1_inv*VF_kim1_1_inv
            # print(V_over_F, err0, err1)
            return err0, err1
        return Rachford_Rice_err_fprime

    zs_orig, Ks_orig = zs, Ks

    solve_order = 1 # 1 for newton, 0 for secant - development only, should always return the correct answer

    Kmin, Kmax, z_of_Kmax = 1e300, -1e300, 1e300
    for i in range(N):
        if zs[i] > 0.0:
            if Ks[i] > Kmax:
                z_of_Kmax = zs[i]
                Kmax = Ks[i]
            if Ks[i] < Kmin:
                Kmin = Ks[i]
    if Kmin > 1.0 or Kmax < 1.0:
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))

    z_of_Kmax, Kmin, Kmax = mpf(z_of_Kmax), mpf(Kmin), mpf(Kmax)

    V_over_F_min = ((Kmax-Kmin)*z_of_Kmax - (1- Kmin))/((1- Kmin)*(Kmax- 1))
    V_over_F_max = 1/(1 - Kmin)

    # Attempt to avoid zero division errors at either boundary
    V_over_F_min += V_over_F_min*tol
    V_over_F_max -= V_over_F_max*tol

    zs_mp = [mpf(i) for i in zs]
    Ks_mp = [mpf(i) for i in Ks]
    Ks_minus_1 = [Ki - 1 for Ki in Ks_mp]

    zs_k_minus_1 = [zs_mp[i]*Ks_minus_1[i] for i in range(N)]

    zs_k_minus_1_2 = [0.0]*N
    for i in range(N):
        zs_k_minus_1_2[i] = -zs_k_minus_1[i]*Ks_minus_1[i]

    if solve_order == 0:
        objf = make_objf(zs_k_minus_1, Ks_minus_1)
    elif solve_order == 1:
        objf = make_objf_der(zs_k_minus_1, zs_k_minus_1_2, Ks_minus_1)

    guess = None
    try:
        # Try to obtain an initial guess for speed and convergence from the
        # other solvers
        guess, _, _ = flash_inner_loop(zs_orig, Ks_orig)
    except:
        pass
    if guess is None or (guess < V_over_F_min or guess > V_over_F_max):
        # Check the guess to ensure it is within bounds
        guess = 0.5*(V_over_F_min + V_over_F_max)
    guess = mpf(guess)

    # mpmath does not have an option to respect boundaries, so its solvers
    # often go outside the correct range
    # try:
    #     V_over_F = findroot(objf, guess, tol=tol, solver='newton')
    # except:
    if N == 2:
        # A peculiar amount of numerical issues come up in binaries with the solvers
        # Fortunately, the analytical solution is easy to compute and we have lots of
        # decimals!
        z1, z2 = zs_mp
        K1, K2 = Ks_mp
        z1z2 = z1 + z2
        K1z1 = K1*z1
        K2z2 = K2*z2
        t1 = z1z2 - K1z1 - K2z2
        den = t1 + K2*K1z1 + K1*K2z2 - K1*z2 - K2*z1
        V_over_F = t1/den
    else:
        # Requiring a low ytol seems to guarantee a correct solution
        if solve_order == 0:
            p1 = 0.4*V_over_F_min + 0.6*V_over_F_max
            V_over_F = secant(objf, guess, low=V_over_F_min, high=V_over_F_max, xtol=tol, maxiter=1000, ytol=1e-50, x1=p1)
        elif solve_order == 1:
            try:
                V_over_F = newton(objf, guess, low=V_over_F_min, high=V_over_F_max, xtol=tol, maxiter=1000, ytol=1e-50, fprime=True)
            except:
                # Should happen only just barely because of numerical issues calculating the bounds
                V_over_F = newton(objf, guess, xtol=tol, maxiter=1000, ytol=1e-50, fprime=True)

    xs = [0]*N
    ys = [0]*N

    LF = 1 - V_over_F
    for i in range(N):
        x_calc = zs_mp[i]/(1 + V_over_F*Ks_minus_1[i])
        y_calc = x_calc*Ks_mp[i]

        # This printed value should be 1. Once the values are converted to
        # floating-point, this may no longer be true!
        # print((LF*x_calc + V_over_F*y_calc)/zs[i])
        xs[i] = float(x_calc)
        ys[i] = float(y_calc)
    return float(LF), float(V_over_F), xs, ys



def Rachford_Rice_err_LN2(y, zs, cis_ys, x0, V_over_F_min, N):
    x1 = exp(-y)
    x3 = 1.0/(x1 + 1.0)
    x0x3 = x0*x3

    x6 = x0x3*x3
    x1x6 = x1*x6
    t50 = V_over_F_min + x0x3
    t51 = 1.0 - 2.0*x1*x3

    F0, dF0, ddF0 = 0.0, 0.0, 0.0
    for i in range(N):
        x5 = 1.0/(t50 - cis_ys[i])
        zix5 = zs[i]*x5
        F0 += zix5
        # Func requires 1 division, 1 multiplication, 2 add
        # 1st Deriv adds 2 mult, 1 add
        # 3rd deriv adds 1 mult, 3 add
        x5x1x6 = x5*x1x6
        x7 = zix5*x5x1x6
        dF0 += x7
        ddF0 += x7*(t51 + x5x1x6 + x5x1x6)
    # print(F0, y)
    return F0, -dF0, ddF0

@mark_numba_uncacheable
def Rachford_Rice_solution_LN2(zs, Ks, guess=None):
    r'''Solves the a objective function for the Rachford-Rice flash equation
    according to the Leibovici and Nichita (2010) transformation (method 2).
    This transformation makes the only zero of the function be the desired one.
    Consequently, higher-order methods may be used to solve this equation.
    Halley's (second derivative) method is found to be the best; typically
    needing ~50% fewer iterations than the RR formulation with Secant method.

    .. math::
        H(y) = \sum_i^n \frac{z_i}{\lambda - c_i} = 0

    .. math::
        \lambda = c_k + \frac{c_{k+1} - c_k}{1 + e^{-y}}

    .. math::
        c_i = \frac{1}{1-K_i}

    .. math::
        c_{k} = \left(\frac{V}{F}\right)_{min}

    .. math::
        c_{k+1} = \left(\frac{V}{F}\right)_{max}

    Note the two different uses of `c` in the above equation, confusingly
    given in [1]_. `lambda` is the vapor fraction.

    Once the equation has been solved for `y`, the vapor fraction can be
    calculated outside the solver.


    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]
    guess : float, optional
        Optional initial guess for vapor fraction, [-]

    Returns
    -------
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    The initial guess is the average of the following, as described in [2]_.

    .. math::
        \left(\frac{V}{F}\right)_{min} = \frac{(K_{max}-K_{min})z_{of\;K_{max}}
        - (1-K_{min})}{(1-K_{min})(K_{max}-1)}

    .. math::
        \left(\frac{V}{F}\right)_{max} = \frac{1}{1-K_{min}}

    The first and second derivatives are derived with sympy as follows:

    >>> from sympy import * # doctest: +SKIP
    >>> VF_min, VF_max, ai, ci, y = symbols('VF_min, VF_max, ai, ci, y') # doctest: +SKIP
    >>> V_over_F = (VF_min + (VF_max - VF_min)/(1 + exp(-y))) # doctest: +SKIP
    >>> F = ai/(V_over_F - ci) # doctest: +SKIP
    >>> terms = [F, diff(F, y), diff(F, y, 2)] # doctest: +SKIP
    >>> cse(terms, optimizations='basic') # doctest: +SKIP

    Some helpful information about this transformation can also be found in
    [3]_.

    Examples
    --------
    >>> Rachford_Rice_solution_LN2(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.6907302627738, [0.3394086969663, 0.3650560590371, 0.29553524399648], [0.571903654388, 0.27087159580558, 0.1572247498061])

    References
    ----------
    .. [1] Leibovici, Claude F., and Dan Vladimir Nichita. "Iterative Solutions
       for ∑iaiλ-ci=1 Equations." Chemical Engineering Research and Design 88,
       no. 5 (May 1, 2010): 602-5. https://doi.org/10.1016/j.cherd.2009.10.012.
    .. [2] Li, Yinghui, Russell T. Johns, and Kaveh Ahmadi. "A Rapid and Robust
       Alternative to Rachford-Rice in Flash Calculations." Fluid Phase
       Equilibria 316 (February 25, 2012): 85-97.
       doi:10.1016/j.fluid.2011.12.005.
    .. [3] Billingsley, D. S. "Iterative Solution for ∑iaiλ-ci Equations."
       Computers & Chemical Engineering 26, no. 3 (March 15, 2002): 457-60.
       https://doi.org/10.1016/S0098-1354(01)00767-0.
    '''
    N = len(Ks)
    Kmin, Kmax, z_of_Kmax = 1e300, -1e300, 1e300
    for i in range(N):
        if zs[i] > 0.0:
            if Ks[i] > Kmax:
                z_of_Kmax = zs[i]
                Kmax = Ks[i]
            if Ks[i] < Kmin:
                Kmin = Ks[i]
    if Kmin > 1.0*(1-1e-15) or Kmax < 1.0*(1+1e-15):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment

    one_m_Kmin = 1.0 - Kmin
    Kmax_m_one = (Kmax - 1.)
    N = len(zs)
    V_over_F_min = ((Kmax-Kmin)*z_of_Kmax - one_m_Kmin)/((one_m_Kmin)*Kmax_m_one)
    V_over_F_max = 1./one_m_Kmin

    guess = 0.5*(V_over_F_min + V_over_F_max) if guess is None else guess
    cis_ys = [0.0]*N  # To save memory, reuse this list later
    for i in range(N):
        cis_ys[i] = 1.0/(1.0 - Ks[i])

    x0 = V_over_F_max - V_over_F_min

    # Suggests guess V_over_F_min, not using
    log_transform = (V_over_F_max-guess)/(guess-V_over_F_min)
    if abs(log_transform-1) < 1e-10:
        # The derivative is huge around a log transform of 1, better to start at a hard-coded location
        log_transform = 0.8
    if log_transform > 0.0:
        guess = -log(log_transform)
    else:
        # Case where guess was less than V_over_F_min - nasty
        guess = 0.5*(V_over_F_min + V_over_F_max)
        guess = -log((V_over_F_max-guess)/(guess-V_over_F_min))
    # Should always converge - no poles

    # The function cannot be evaluated in some regions due to a zero division however
    # ci should be the minimum
    if V_over_F_max > 0.0:
        near_high = V_over_F_max*one_epsilon_smaller
    else:
        near_high = V_over_F_max*one_epsilon_larger
    if (near_high-V_over_F_min) == 0.0:
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s"%(Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment
    solver_high = -log((V_over_F_max-near_high)/(near_high-V_over_F_min))

    if V_over_F_min < 0.0:
        near_low = V_over_F_min*one_epsilon_smaller
    elif V_over_F_min > 0.0:
        near_low = V_over_F_min*one_epsilon_larger
    else:
        # V_over_F_min equals zero case, cannot evaluate there
        near_low = min(1e-20, V_over_F_max*1e-15)
    if (near_low-V_over_F_min) == 0.0:
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s"%(Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment
    solver_low = -log((V_over_F_max-near_low)/(near_low-V_over_F_min))

    V_over_F = newton(Rachford_Rice_err_LN2, guess, fprime=True, fprime2=True, xtol=1.48e-12, low=solver_low, high=solver_high, bisection=True, args=(zs, cis_ys, x0, V_over_F_min, N)) # numba: delete
#    V_over_F = halley(Rachford_Rice_err_LN2, guess, xtol=1e-10, args=(zs, cis_ys, x0, V_over_F_min, N)) # numba: uncomment
    V_over_F = (V_over_F_min + (V_over_F_max - V_over_F_min)/(1.0 + exp(-V_over_F)))

    if 1-1e-4 < V_over_F < 1+1e-4:
        # Re-calculate while inverting phase compositions and inverting the K values
        # This is necessary for the correct calculation for x compositions when the
        # liquid fraction is very near zero.
        Ks_inv = cis_ys
        for i in range(N):
            Ks_inv[i] = 1.0/Ks[i]
        LF, xs, ys = Rachford_Rice_solution_LN2(zs, Ks_inv, guess=1.0-V_over_F)
        return V_over_F, ys, xs

    else:
        xs = [0.0]*N
        for i in range(N):
            xi = zs[i]/(1.0 + V_over_F*(Ks[i] - 1.0))
            xs[i] = xi
            cis_ys[i] = Ks[i]*xi
    return V_over_F, xs, cis_ys

def LJA_err(x1, t1, terms_2, terms_3, N2):
    err = 1. + t1*x1
    for i in range(N2):
        # evaluations: 2 mult, 1 div, 1 add
        err += x1/(terms_2[i] + terms_3[i]*x1)
    return err

def LJA_fprime2(v, t1, terms_2, terms_3, N2):
    err = 1. + t1*v
    fprime = t1
    fprime2 = 0.0
    for i in range(N2):
        x0 = terms_3[i]*v
        x1 = terms_2[i] + x0
        x2 = 1.0/x1
        x3 = x0*x2
        err += v*x2
        fprime += x2*(1.0 - x3)
        fprime2 += 2.0*terms_3[i]*(x3 - 1.0)*x2*x2
    return err, fprime, fprime2

@mark_numba_uncacheable
def Li_Johns_Ahmadi_solution(zs, Ks, guess=None):
    r'''Solves the objective function of the Li-Johns-Ahmadi flash equation.
    Uses the method proposed in [1]_ to obtain an initial guess.

    .. math::
        0 = 1 + \left(\frac{K_{max}-K_{min}}{K_{min}-1}\right)x_{max} + \sum_{i=2}^{n-1}
        \frac{K_i-K_{min}}{K_{min}-1}
        \left[\frac{z_i(K_{max}-1)x_{max}}{(K_i-1)z_{max} + (K_{max}-K_i)x_{max}}\right]

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]

    Returns
    -------
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Notes
    -----
    The initial guess is the average of the following, as described in [1]_.
    Each guess should be limited to be between 0 and 1 as they are often
    negative or larger than 1. `max` refers to the corresponding mole fractions
    for the species with the largest K value.

    .. math::
        \left(\frac{1-K_{min}}{K_{max}-K_{min}}\right)z_{max}\le x_{max} \le
        \left(\frac{1-K_{min}}{K_{max}-K_{min}}\right)

    If the `newton` method does not converge, a bisection method (brenth) is
    used instead. However, it is somewhat slower, especially as newton will
    attempt 50 iterations before giving up.

    This method does not work for problems of only two components.
    K values are sorted internally. Has not been found to be quicker than the
    Rachford-Rice equation.

    Examples
    --------
    >>> Li_Johns_Ahmadi_solution(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.6907302627738544, [0.33940869696634357, 0.3650560590371706, 0.2955352439964858], [0.5719036543882889, 0.27087159580558057, 0.15722474980613044])

    References
    ----------
    .. [1] Li, Yinghui, Russell T. Johns, and Kaveh Ahmadi. "A Rapid and Robust
       Alternative to Rachford-Rice in Flash Calculations." Fluid Phase
       Equilibria 316 (February 25, 2012): 85-97.
       doi:10.1016/j.fluid.2011.12.005.
    '''
    # Re-order both Ks and Zs by K value, higher coming first
    p = sorted(zip(Ks,zs), reverse=True) # numba: delete
    Ks_sorted, zs_sorted = [K for (K,z) in p], [z for (K,z) in p] # numba: delete
#    sorted_idxs = np.argsort(Ks)[::-1] # numba: uncomment
#    Ks_sorted, zs_sorted = Ks[sorted_idxs], zs[sorted_idxs] # numba: uncomment

    # Largest K value and corresponding overall mole fraction
    k1 = Ks_sorted[0]
    z1 = zs_sorted[0]
    # Smallest K value
    kn = Ks_sorted[-1]

    if kn > 1.0*(1-1e-15) or k1 < 1.0*(1+1e-15):
        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#        raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment

    x_max = (1. - kn)/(k1 - kn)
    x_min = x_max*z1

    if x_min < 0.0:
        x_min2 = 0.0
    else:
        x_min2 = x_min

    if x_max > 1.0:
        x_max2 = 1.0
    else:
        x_max2 = x_max

    N = len(zs)
    N2 = N - 2
    length = N - 1
    kn_m_1 = kn - 1.0
    k1_m_1 = (k1 - 1.0)
    kn_m_1_inv = 1.0/kn_m_1
    t1 = (k1 - kn)*kn_m_1_inv

    x_guess = (x_min2 + x_max2)*0.5 if guess is None else z1/(guess*k1_m_1 + 1.0)

    Ks_iter = Ks_sorted[1:length]
    zs_iter = zs_sorted[1:length]

    for i in range(N2):
        ki = Ks_iter[i]
        term_1 = 1.0/((ki - kn)*kn_m_1_inv*zs_iter[i]*k1_m_1)
        Ks_iter[i] = (ki - 1.0)*z1*term_1
        zs_iter[i] = (k1 - ki)*term_1

    terms_2, terms_3 = Ks_iter, zs_iter


    try:
        x1 = halley(LJA_fprime2, x_guess, low=x_min, high=x_max, xtol=1e-12, bisection=True, args=(t1, terms_2, terms_3, N2))
#        x1 = secant(LJA_err, x_guess, low=x_min, high=x_max, ytol=1e-13, args=(t1, terms_2, terms_3, N2))
        # newton skips out of its specified range in some cases, finding another solution
        # Check for that with asserts, and use brenth if it did
        # Must also check that V_over_F is right.
        V_over_F = (z1 - x1)/(x1*k1_m_1)
#        print('V_over_F', V_over_F)
#        assert x1 >= x_min
#        assert x1 <= x_max
#        assert 0.0 <= V_over_F <= 1.0
    except:
#        print('using bounding')
#        from fluids.numerics import py_bisect as bisect
#        x1 = bisect(objective, x_min, x_max, ytol=1e-12)
        x1 = brenth(LJA_err, x_min, x_max, args=(t1, terms_2, terms_3, N2)) # , xtol=1e-12, rtol=0
        V_over_F = (-x1 + z1)/(x1*(k1 - 1.))

    for i in range(N):
        xi = zs[i]/(1.0 + V_over_F*(Ks[i] - 1.0))
        Ks_sorted[i] = xi
        zs_sorted[i] = Ks[i]*xi
    return V_over_F, Ks_sorted, zs_sorted


def _Rachford_Rice_analytical_3(zs, Ks):
    z1, z2, z3 = zs
    K1, K2, K3 = Ks
    x0 = K1*z1
    x1 = K1*z2
    x2 = K1*z3
    x3 = K2*z1
    x4 = K2*z2
    x5 = K2*z3
    x6 = K3*z1
    x7 = K3*z2
    x8 = K3*z3
    x9 = K2*x0
    x10 = K2*x1
    x11 = K2*x2
    x12 = K3*x0
    x13 = K3*x1
    x14 = K3*x2
    x15 = K3*x4
    x16 = K3*x5
    x17 = x0 + x0
    x18 = x17*x4
    x19 = x5 + x5
    x20 = x0*x19
    x21 = x1*x19
    x22 = x17*x7
    x23 = x17*x8
    x24 = x8 + x8
    x25 = x1*x24
    x26 = x3 + x3
    x27 = x26*x7
    x28 = x24*x3
    x29 = x24*x4
    x30 = K1*K1
    x31 = z2*z2
    x32 = x30*x31
    x33 = z3*z3
    x34 = x30*x33
    x35 = K2*K2
    x36 = z1*z1
    x37 = x35*x36
    x38 = x33*x35
    x39 = K3*K3
    x40 = x36*x39
    x41 = x31*x39
    x42 = K1 + K1
    x43 = K2*x33
    x44 = x42*x43
    x45 = K3*x31
    x46 = x42*x45
    x47 = z2 + z2
    x48 = x30*z3
    x49 = K2 + K2
    x50 = K3*x36
    x51 = x49*x50
    x52 = z1 + z1
    x53 = x35*z3
    x54 = x39*z2
    x55 = 4.0*x12
    x56 = 4.0*K1
    x57 = K2*x56
    x58 = x35*x47
    x59 = x1 + x1
    x60 = x39*z3
    x61 = x30*x47
    x62 = x4 + x4
    x63 = x6 + x6
    x64 = x7 + x7
    x65 = K3 + K3

    V_over_F = (-(-x0  + 0.5*(-x1 + x10 + x12 + x14 + x15
                  + x16 - x2 - x3 - x5 - x6 - x7
                  + x9) - x4  - x8  + z1 + z2 + z3 + (
                 K3*x43*x56 - x0*x58 + 4.0*x13*x5 + x18 - x20 - x21 - x22 + x23
                 - x25 - x27 - x28 + x29 + x30*(-x27 - x28 + x29 + x35*x52*z2
                + x37 + x40 - x51) + x32 + x34*(x39 - x65 + 1.0) + x35*(-x22
                 + x23 - x25 + x32 + x41 - x46) + x37 - x38*x65 + x38 + x39*(
                x18 - x20 - x21 + x38 - x44 + x48*x52) + x4*x55 + x40 + x41
                + x42*(-x37 - x40) - x44 - x46 + x48*(x26 + x47 - x62 - x63
                - x64) + x49*(-x32 - x41) + x5*x55 - x51 + x53*(x59 + x52
                -x17 + x54 + x54 - x63 - x64) + x54*(x52 - x17 - x26)
                + x57*(x45 + x50) + x58*x6 + x60*(x26 -x17 + x59 - x62)
                + x61*(x6 - x3)
                )**0.5*0.5)/(
                K3*(x10 + x11 - x3 + x9) + x0 + x1 - x10 - x11 - x12 - x13
                - x14 - x15 - x16 + x2 + x3 + x4 + x5 + x6 + x7 + x8 - x9
                - z1 - z2 - z3))


    xs = [0.0]*3
    ys = [0.0]*3
    for i in range(3):
        xi = zs[i]/(1.0 + V_over_F*(Ks[i] - 1.0))
        xs[i] = xi
        ys[i] = Ks[i]*xi
    return V_over_F, xs, ys





FLASH_INNER_ANALYTICAL = 'Analytical'
FLASH_INNER_SECANT = 'Rachford-Rice (Secant)'
FLASH_INNER_NR = 'Rachford-Rice (Newton-Raphson)'
FLASH_INNER_HALLEY = 'Rachford-Rice (Halley)'
FLASH_INNER_NUMPY = 'Rachford-Rice (NumPy)'
FLASH_INNER_LJA = 'Li-Johns-Ahmadi'
FLASH_INNER_POLY = 'Rachford-Rice (polynomial)'
FLASH_INNER_LN2 = 'Leibovici and Nichita 2'
FLASH_INNER_LN = 'Leibovici and Neoschil'

flash_inner_loop_all_methods = (FLASH_INNER_ANALYTICAL,
                                FLASH_INNER_SECANT,
                                FLASH_INNER_NR, FLASH_INNER_HALLEY,
                                FLASH_INNER_NUMPY, FLASH_INNER_LJA,
                                FLASH_INNER_POLY, FLASH_INNER_LN2,
                                FLASH_INNER_LN)
"""Tuple of method name keys. See the `flash_inner_loop` for the actual references"""

def flash_inner_loop_methods(N):
    """Return all methods able to solve the Rachford-Rice equation
    for the specified number of components.

    Parameters
    ----------
    N : int
        Number of components, [-]

    Returns
    -------
    methods : list[str]
        Methods which can be used to solve the Rachford-rice equation

    See Also
    --------
    flash_inner_loop
    """
    methods = []
    if N in (2, 3, 4, 5):
        methods.append(FLASH_INNER_ANALYTICAL)
    if N >= 10 and not IS_PYPY:
        methods.append(FLASH_INNER_NUMPY)
    if N >= 2:
        methods.extend([FLASH_INNER_LN2, FLASH_INNER_SECANT, FLASH_INNER_NR, FLASH_INNER_HALLEY, FLASH_INNER_LN])
        if N < 10 and not IS_PYPY:
            methods.append(FLASH_INNER_NUMPY)
    if N >= 3:
        methods.append(FLASH_INNER_LJA)
    if N < 20:
        methods.append(FLASH_INNER_POLY)
    return methods


@mark_numba_uncacheable
def flash_inner_loop(zs, Ks, method=None, guess=None, check=False):
    r'''This function handles the solution of the inner loop of a flash
    calculation, solving for liquid and gas mole fractions and vapor fraction
    based on specified overall mole fractions and K values. As K values are
    weak functions of composition, this should be called repeatedly by an outer
    loop. Will automatically select an algorithm to use if no method is
    provided. Should always provide a solution.

    The automatic algorithm selection will try an analytical solution, and use
    the Rachford-Rice method if there are 6 or more components in the mixture.

    Parameters
    ----------
    zs : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[float]
        Equilibrium K-values, [-]
    guess : float, optional
        Optional initial guess for vapor fraction, [-]
    check : bool, optional
        Whether or not to check the K values to ensure a positive-composition
        solution exists, [-]

    Returns
    -------
    V_over_F : float
        Vapor fraction solution [-]
    xs : list[float]
        Mole fractions of each species in the liquid phase, [-]
    ys : list[float]
        Mole fractions of each species in the vapor phase, [-]

    Other Parameters
    ----------------
    method : string, optional
        The method name to use. Accepted methods are 'Analytical',
        'Rachford-Rice (Secant)', 'Rachford-Rice (Newton-Raphson)',
        'Rachford-Rice (Halley)', 'Rachford-Rice (NumPy)',
        'Leibovici and Nichita 2', 'Rachford-Rice (polynomial)', and
        'Li-Johns-Ahmadi'. All valid values are also held
        in the list `flash_inner_loop_methods`.

    Notes
    -----
    A total of eight methods are available for this function. They are:

        * 'Analytical', an exact solution derived with SymPy, applicable only
          only to mixtures of two, three, or four components
        * 'Rachford-Rice (Secant)', 'Rachford-Rice (Newton-Raphson)',
          'Rachford-Rice (Halley)', or 'Rachford-Rice (NumPy)',
          which numerically solves an objective function
          described in :obj:`Rachford_Rice_solution`.
        * 'Leibovici and Nichita 2', a transformation of the RR equation
          described in :obj:`Rachford_Rice_solution_LN2`.
        * 'Li-Johns-Ahmadi', which numerically solves an objective function
          described in :obj:`Li_Johns_Ahmadi_solution`.
        * 'Leibovici and Neoschil', which numerically solves an objective
          function described in :obj:`Rachford_Rice_solution_Leibovici_Neoschil`.

    Examples
    --------
    >>> flash_inner_loop(zs=[0.5, 0.3, 0.2], Ks=[1.685, 0.742, 0.532])
    (0.6907302627738, [0.3394086969663, 0.3650560590371, 0.29553524399648], [0.571903654388, 0.27087159580558, 0.1572247498061])
    '''
    l = len(zs)
    if method is None:
        method2 = FLASH_INNER_ANALYTICAL if l < 3 else (FLASH_INNER_NUMPY if (not IS_PYPY and l >= 10) else FLASH_INNER_LN2)
    else:
        method2 = method
    # if check:
    #     check = False
    if check:
        K_low, K_high = False, False
        for zi, Ki in zip(zs, Ks):
            if zi != 0.0:
                if Ki > 1.0:
                    K_high = True
                else:
                    K_low = True
                if K_high and K_low:
                    break
        if not K_low or not K_high:
            raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" %(Ks)) # numba: delete
#            raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment

        for zi in zs:
            if zi == 0.0:
                # Count the number of zeros
                zeros = 0
                for zi in zs:
                    if zi == 0.0:
                        zeros += 1

                # Allocate appropriate lists
                zero_indexes = [0]*zeros
                zs2 = [0.0]*(l-zeros)
                Ks2 = [0.0]*(l-zeros)
                running_zeros = 0
                for i in range(l):
                    if zs[i] == 0.0:
                        zero_indexes[running_zeros] = i
                        running_zeros += 1
                    else:
                        zs2[i-running_zeros] = zs[i]
                        Ks2[i-running_zeros] = Ks[i]
                V_over_F, xs, ys = Rachford_Rice_solution(zs2, Ks2, fprime=False, fprime2=False, guess=guess)

                # Reset the values into a main array
                xs2 = [0.0]*l
                ys2 = [0.0]*l
                running_zeros = 0
                for i in range(l):
                    if zs[i] != 0.0:
                        xs2[i] = xs[i - running_zeros]
                        ys2[i] = ys[i - running_zeros]
                    else:
                        running_zeros += 1
                return V_over_F, xs2, ys2

    if method2 == FLASH_INNER_LN2:
        return Rachford_Rice_solution_LN2(zs, Ks, guess)
    elif method2 == FLASH_INNER_LN:
        LF, VF, xs, ys = Rachford_Rice_solution_Leibovici_Neoschil(zs, Ks, guess=guess)
        return (VF, xs, ys)
    elif method2 == FLASH_INNER_SECANT:
        return Rachford_Rice_solution(zs, Ks, fprime=False, fprime2=False, guess=guess)
    elif method2 == FLASH_INNER_ANALYTICAL:
        if l == 2:
            # _, VF, xs, ys = Rachford_Rice_solution_binary_dd(zs, Ks)
            # return VF, xs, ys
            z1, z2 = zs
            K1, K2 = Ks
            if (K1 < 1.0 and K2 < 1.0) or (K1 > 1.0 and K2 > 1.0):
                raise PhaseCountReducedError("For provided K values, there is no positive-composition solution; Ks=%s" % (Ks))  # numba: delete
#                raise PhaseCountReducedError("For provided K values, there is no positive-composition solution") # numba: uncomment
            z1z2 = z1 + z2
            K1z1 = K1*z1
            K2z2 = K2*z2
            t1 = z1z2 - K1z1 - K2z2
            den = t1 + K2*K1z1 + K1*K2z2 - K1*z2 - K2*z1
            if den != 0.0:
                V_over_F = t1/den
            else:
                return Rachford_Rice_solution(zs=zs, Ks=Ks, guess=guess, fprime=False, fprime2=False)
        elif l == 3:
            fail = False
            try:
                sln = _Rachford_Rice_analytical_3(zs, Ks)
            except:
                fail = True
            if not fail and sln[0].imag != 0.0:
                fail = True
            if fail:
                return Rachford_Rice_solution(zs=zs, Ks=Ks, guess=guess, fprime=False, fprime2=False)
            return sln
        elif l == 4:
            return Rachford_Rice_solution_polynomial(zs, Ks)
        # Better to use a numerical solution
#            poly = Rachford_Rice_polynomial_4(zs, [Ki - 1.0 for Ki in Ks])
#            V_over_F = roots_cubic_a1(poly[1], poly[2], poly[3])[2].real
        elif l == 5:
            return Rachford_Rice_solution_polynomial(zs, Ks)
        elif l == 1:
            raise ValueError("Input dimensions are for one component! Rachford-Rice does not apply")
        else:
            raise ValueError('Only solutions for components counts 2, 3, and 4 are available analytically')
        # Need to avoid zero divisions here - specifically when the composition of one component in the feed is 0.0
        xs = [0.0]*l
        ys = [0.0]*l
        for i in range(l):
            try:
                xs[i] = zs[i]/(1.0 + V_over_F*Ks[i]-V_over_F)
            except:
                pass
            ys[i] = xs[i]*Ks[i]
        return V_over_F, xs, ys

    elif method2 == FLASH_INNER_NUMPY:
        try:
            return Rachford_Rice_solution_numpy(zs=zs, Ks=Ks, guess=guess)
        except:
            return Rachford_Rice_solution(zs=zs, Ks=Ks, guess=guess, fprime=False, fprime2=False)
    elif method2 == FLASH_INNER_NR:
        return Rachford_Rice_solution(zs=zs, Ks=Ks, guess=guess, fprime=True)
    elif method2 == FLASH_INNER_HALLEY:
        return Rachford_Rice_solution(zs=zs, Ks=Ks, guess=guess, fprime=True,
                                      fprime2=True)

    elif method2 == FLASH_INNER_LJA:
        return Li_Johns_Ahmadi_solution(zs=zs, Ks=Ks, guess=guess)
    elif method2 == FLASH_INNER_POLY:
        return Rachford_Rice_solution_polynomial(zs=zs, Ks=Ks)
    else:
        raise ValueError('Incorrect method input')


### N phase RR

def Rachford_Rice_flashN_f_jac(betas, ns, Ks, Ksm1=None, zsKsm1=None):
    N = len(betas)
    Fs = [0.0]*N
    dFs_dBetas = [[0.0]*N for i in range(N)] # numba: delete
#    dFs_dBetas = np.zeros((N, N)) # numba: uncomment
    if Ksm1 is None:
        Ksm1 = [[i-1.0 for i in Ks_i] for Ks_i in Ks] # numba: delete
#        Ksm1 = Ks - 1.0 # numba: uncomment
    if zsKsm1 is None:
        zsKsm1 = [[zi*Ksim1 for zi, Ksim1 in zip(ns, Ksm1i)] for Ksm1i in Ksm1] # numba: delete
#        zsKsm1 = ns*Ksm1 # numba: uncomment

    for i, zi in enumerate(ns):
        denom = 1.0
        for j, beta_i in enumerate(betas):
            denom += beta_i*Ksm1[j][i]
        denom_inv = 1.0/denom
        denom_inv2 = denom_inv*denom_inv

        for j in range(N):
            Fs[j] += zsKsm1[j][i]*denom_inv

        for j in range(N):
            f = zsKsm1[j][i]*denom_inv2
            for k in range(j):
                term = f*Ksm1[k][i]
                dFs_dBetas[k][j] -= term
                dFs_dBetas[j][k] -= term
            dFs_dBetas[j][j] -= f*Ksm1[j][i]
    # print(Fs, betas)
    return Fs, dFs_dBetas


def Rachford_Rice_flash2_f_jac(betas, zs, Ks):
    # In a more clever system like RR 2, can compute entire numerators before hand.
    beta_y = betas[0]
    beta_z = betas[1]
    Ks_y = Ks[0]
    Ks_z = Ks[1]
    F0 = 0.0
    F1 = 0.0
    dF0_dy = 0.0
    dF0_dz = 0.0
    dF1_dz = 0.0

    for i in range(len(zs)):
        zi = zs[i]
        Ky_m1 = (Ks_y[i] - 1.0)
        Kz_m1 = (Ks_z[i] - 1.0)
        denom_inv = 1.0/(1.0 + beta_y*Ky_m1 + beta_z*Kz_m1) # same in all
        delta_F0 = zi*Ky_m1*denom_inv
        delta_F1 = zi*Kz_m1*denom_inv

        F0 += delta_F0
        F1 += delta_F1
        c0 = Kz_m1*denom_inv
        dF0_dy -= delta_F0*Ky_m1*denom_inv
        dF0_dz -= delta_F0*c0
        dF1_dz -= delta_F1*c0

#    Fs = [0.0]*2 # numba: uncomment
#    Fs[0] = F0  # numba: uncomment
#    Fs[1] = F1  # numba: uncomment
#    dFs = np.zeros((2,2)) # numba: uncomment
#    dFs[0][0] = dF0_dy # numba: uncomment
#    dFs[0][1] = dF0_dz # numba: uncomment
#    dFs[1][0] = dF0_dz # numba: uncomment
#    dFs[1][1] = dF1_dz # numba: uncomment
#    return Fs, dFs # numba: uncomment
    return [F0, F1], [[dF0_dy, dF0_dz], [dF0_dz, dF1_dz]] # numba: delete

def Rachford_Rice_valid_solution_naive(ns, betas, Ks, limit_betas=False):
    if limit_betas:
        for beta in betas:
            if beta < 0.0 or beta > 1.0:
                return False

    for i, ni in enumerate(ns):
        sum_critiria = 1.0
        for j, beta_i in enumerate(betas):
            sum_critiria += beta_i*(Ks[j][i] - 1.0)
        if sum_critiria < 0.0:
            # Will result in negative composition for xi, yi, and zi
            return False
    return True


@mark_numba_uncacheable
def Rachford_Rice_solutionN(ns, Ks, betas):
    r'''Solves the (phases -1) objectives functions of the Rachford-Rice flash
    equation for an N-phase system. Initial guesses are required for all phase
    fractions except the last. The Newton method is used, with an
    analytical Jacobian.

    Parameters
    ----------
    ns : list[float]
        Overall mole fractions of all species, [-]
    Ks : list[list[float]]
        Equilibrium K-values of all phases with respect to the `x` (reference)
        phase, [-]
    betas : list[float]
        Phase fraction initial guesses only for the first N - 1 phases;
        each value corresponds to the phase fraction of each set of the K
        values; if a phase fraction is specified for the last phase as well,
        it is ignored [-]

    Returns
    -------
    betas : list[float]
        Phase fractions of all of the phases; one each for each K value set
        given, plus the reference phase phase fraction [-]
    compositions : list[list[float]]
        Mole fractions of each species in each phase; order each phase
        in the same order as the K values were provided, and then the `x` phase
        last, which was the reference phase [-]

    Notes
    -----
    This algorithm has been used without issue for 4 and 5 phase flashes.

    Some helpful information was found in [1]_, although this method does not
    follow it exactly.

    Examples
    --------
    >>> ns = [0.204322076984, 0.070970999150, 0.267194323384, 0.296291964579, 0.067046080882, 0.062489248292, 0.031685306730]
    >>> Ks_y = [1.23466988745, 0.89727701141, 2.29525708098, 1.58954899888, 0.23349348597, 0.02038108640, 1.40715641002]
    >>> Ks_z = [1.52713341421, 0.02456487977, 1.46348240453, 1.16090546194, 0.24166289908, 0.14815282572, 14.3128010831]
    >>> Rachford_Rice_solutionN(ns, [Ks_y, Ks_z], [.1, .6])
    ([0.6868328915094767, 0.06019424397668605, 0.25297286451383727], [[0.21147483364299702, 0.07313470386530294, 0.3198289138763589, 0.33293382568889657, 0.03658604244379159, 0.004616341311925657, 0.02142533917172731], [0.26156812278601893, 0.00200221914149187, 0.203926606651898, 0.2431536850887592, 0.03786610596908296, 0.033556798515399944, 0.21792646184834918], [0.1712804659711611, 0.08150738616425436, 0.13934339491931877, 0.20945175387703213, 0.15668977784027896, 0.22650123851718015, 0.015225982711774586]])

    References
    ----------
    .. [1] Gao, Ran, Xiaolong Yin, and Zhiping Li. "Hybrid Newton-Successive
       Substitution Method for Multiphase Rachford-Rice Equations." Entropy 20,
       no. 6 (June 2018): 452. https://doi.org/10.3390/e20060452.
    '''
    limit_betas = False
    if not Rachford_Rice_valid_solution_naive(ns, betas, Ks, limit_betas=limit_betas):
        raise ValueError("Initial guesses will not lead to convergence")

    # Handle the case of the supplementary answer
    phase_count_m1 = len(Ks)
    if len(betas) > phase_count_m1:
        betas = betas[:-1]
    phase_count = phase_count_m1 + 1

    if phase_count_m1 == 2:# numba: delete
        solve_func = solve_2_direct# numba: delete
    elif phase_count_m1 == 3:# numba: delete
        solve_func = solve_3_direct# numba: delete
    elif phase_count_m1 == 4:# numba: delete
        solve_func = solve_4_direct# numba: delete
    else:# numba: delete
        solve_func = py_solve# numba: delete
#    solve_func = np.linalg.solve # numba: uncomment
    # numba is not smart enough to allow different matrix inverters

    Ksm1 = [[i-1.0 for i in Ks_i] for Ks_i in Ks] # numba: delete
#    Ksm1 = Ks - 1.0 # numba: uncomment
    zsKsm1 = [[zi*Ksim1 for zi, Ksim1 in zip(ns, Ksm1i)] for Ksm1i in Ksm1] # numba: delete
#    zsKsm1 = ns*Ksm1 # numba: uncomment

    # if 1:
    #     import matplotlib.pyplot as plt
    #     from matplotlib import cm
    #     betas_plot = linspace(-10, 10, 500)
    #     errs = []
    #     for b0 in betas_plot:
    #         r = []
    #         for b1 in betas_plot:
    #             Fs = Rachford_Rice_flashN_f_jac([b0, b1], ns, Ks)[0]
    #             err = abs(Fs[0]) + abs(Fs[1])
    #             r.append(err)
    #         errs.append(r)

    #     trunc_err_low = 1e-9
    #     trunc_err_high = 10
    #     X, Y = np.meshgrid(betas_plot, betas_plot)
    #     z = np.array(errs).T
    #     if trunc_err_low is not None:
    #         z[np.where(abs(z) < trunc_err_low)] = trunc_err_low
    #     if trunc_err_high is not None:
    #         z[np.where(abs(z) > trunc_err_high)] = trunc_err_high
    #     color_map = cm.viridis

    #     fig, ax = plt.subplots()
    #     im = ax.pcolormesh(X, Y, z, cmap=color_map) # , norm=LogNorm(vmin=trunc_err_low, vmax=trunc_err_high)
    #     cbar = fig.colorbar(im, ax=ax)
    #     cbar.set_label('Relative error')
    #     plt.show()


    betas, _ = newton_system(Rachford_Rice_flashN_f_jac, jac=True,
                             x0=betas, args=(ns, Ks, Ksm1, zsKsm1), solve_func=solve_func,
                             xtol=1e-12,
                             # ytol=1e-14,
                             damping_func=RRN_new_betas
                             )
    all_betas = [0.0]*phase_count
    beta_sum = 0.0
    for i in range(phase_count_m1):
        beta_sum += betas[i]
        all_betas[i] = betas[i]
    all_betas[-1] = 1.0 - beta_sum

#    print(betas, iter, 'current progress')
    N = len(ns)
    ref_comp = [0.0]*N
    ref_comp_sum = 0.0
    for i in range(N):
        denom = 1.0
        for j in range(phase_count_m1):
            denom += betas[j]*(Ks[j][i]-1.0)
        zi = ns[i]/denom
        ref_comp[i] = zi
        ref_comp_sum += zi

#    comps = np.empty((phase_count, N), np.float64) # numba: uncomment
    comps = [] # numba: delete
    for j in range(phase_count_m1):
        comp = [0.0]*N
        Ks_j = Ks[j]
        for i in range(N):
            comp[i] = ref_comp[i]*Ks_j[i]
        comps.append(comp) # numba: delete
#        comps[j] = comp # numba: uncomment

    comps.append(ref_comp) # numba: delete
#    comps[phase_count_m1] = ref_comp  # numba: uncomment

    if (1.0 - ref_comp_sum) > 1e-10:
        raise ValueError("Converged to nonphysical solution")

    return all_betas, comps


def RRN_new_betas(betas, d_betas, damping, ns, Ks, *args):
    N = len(betas)
    limit_betas = False
    max_beta_step = 1e100
    if 0:
        for i in range(N):
            if d_betas[i] > max_beta_step:
                d_betas[i] = max_beta_step
            elif d_betas[i] < -max_beta_step:
                d_betas[i] = -max_beta_step

    betas_test = [0.0]*N
    for i in range(N):
        betas_test[i] = betas[i] + d_betas[i]*damping
    for i in range(20):
        is_valid = Rachford_Rice_valid_solution_naive(ns, betas_test, Ks, limit_betas=limit_betas)
        if is_valid:
            break

        damping = 0.5*damping
        for i in range(N):
            betas_test[i] = betas[i] + d_betas[i]*damping
    if not is_valid:
        raise ValueError("Should never happen - multiphase phase RR still out of bounds after 20 iterations")
    return betas_test


@mark_numba_uncacheable
def Rachford_Rice_solution2(ns, Ks_y, Ks_z, beta_y=0.5, beta_z=1e-6):
    r'''Solves the two objective functions of the Rachford-Rice flash equation
    for a three-phase system. Initial guesses are required for both phase
    fractions, `beta_y` and `beta_z`. The Newton method is used, with an
    analytical Jacobian.

    .. math::
        F_0 = \sum_i \frac{z_i (K_y -1)}{1 + \beta_y(K_y-1) + \beta_z(K_z-1)} = 0

    .. math::
        F_1 = \sum_i \frac{z_i (K_z -1)}{1 + \beta_y(K_y-1) + \beta_z(K_z-1)} = 0

    Parameters
    ----------
    ns : list[float]
        Overall mole fractions of all species (would be `zs` except that is
        conventially used for one of the three phases), [-]
    Ks_y : list[float]
        Equilibrium K-values of `y` phase to `x` phase, [-]
    Ks_z : list[float]
        Equilibrium K-values of `z` phase to `x` phase, [-]
    beta_y : float, optional
        Initial guess for `y` phase (between 0 and 1), [-]
    beta_z : float, optional
        Initial guess for `z` phase (between 0 and 1), [-]

    Returns
    -------
    beta_y : float
        Phase fraction of `y` phase, [-]
    beta_z : float
        Phase fraction of `z` phase, [-]
    xs : list[float]
        Mole fractions of each species in the `x` phase, [-]
    ys : list[float]
        Mole fractions of each species in the `y` phase, [-]
    zs : list[float]
        Mole fractions of each species in the `z` phase, [-]

    Notes
    -----
    The elements of the Jacobian are calculated as follows:

    .. math::
        \frac{\partial F_0}{\partial \beta_y} = \sum_i \frac{-z_i (K_y -1)^2}
        {\left(1 + \beta_y(K_y-1) + \beta_z(K_z-1)\right)^2}

    .. math::
        \frac{\partial F_1}{\partial \beta_z} = \sum_i \frac{-z_i (K_z -1)^2}
        {\left(1  + \beta_y(K_y-1) + \beta_z(K_z-1)\right)^2}

    .. math::
        \frac{\partial F_1}{\partial \beta_y} = \sum_i \frac{\partial F_0}
        {\partial \beta_z}  = \frac{-z_i (K_z -1)(K_y - 1)}{\left(1
        + \beta_y(K_y-1) + \beta_z(K_z-1)\right)^2}

    In general, the solution which Newton's method converges to may not be the
    desired one, so further constraints are required.

    Okuno's method in [1]_ provides a polygonal region where the correct answer
    lies. It has not been implemented.

    The Leibovici and Neoschil method [4]_ provides a method to compute/update
    the damping parameter, which is suposed to ensure convergence. It claims to
    be able to calculate the maximum damping factor for Newton's method, if it
    tries to go out of bounds.

    A custom region which is believed to be the same as that of Okuno is
    implemented instead - the region which ensures positive compositions for
    all compounds in all phases, but does not restrict the phase fractions to
    be between 0 and 1 or even positive.

    With the convergence restraint, it is believed if a solution lies within
    (0, 1) for both variables, the correct solution will be converged to so long
    as the initial guesses are within the correct region.

    Some helpful information has also been found in [2]_ and [3]_.

    Examples
    --------
    >>> ns = [0.204322076984, 0.070970999150, 0.267194323384, 0.296291964579, 0.067046080882, 0.062489248292, 0.031685306730]
    >>> Ks_y = [1.23466988745, 0.89727701141, 2.29525708098, 1.58954899888, 0.23349348597, 0.02038108640, 1.40715641002]
    >>> Ks_z = [1.52713341421, 0.02456487977, 1.46348240453, 1.16090546194, 0.24166289908, 0.14815282572, 14.3128010831]
    >>> Rachford_Rice_solution2(ns, Ks_y, Ks_z, beta_y=.1, beta_z=.6)
    (0.6868328915094766, 0.06019424397668606, [0.1712804659711611, 0.08150738616425436, 0.1393433949193188, 0.20945175387703213, 0.15668977784027893, 0.22650123851718007, 0.015225982711774586], [0.21147483364299702, 0.07313470386530294, 0.31982891387635903, 0.33293382568889657, 0.036586042443791586, 0.004616341311925655, 0.02142533917172731], [0.26156812278601893, 0.00200221914149187, 0.20392660665189805, 0.2431536850887592, 0.03786610596908295, 0.03355679851539993, 0.21792646184834918])

    References
    ----------
    .. [1] Okuno, Ryosuke, Russell Johns, and Kamy Sepehrnoori. "A New
       Algorithm for Rachford-Rice for Multiphase Compositional Simulation."
       SPE Journal 15, no. 02 (June 1, 2010): 313-25.
       https://doi.org/10.2118/117752-PA.
    .. [2] Li, Zhidong, and Abbas Firoozabadi. "Initialization of Phase
       Fractions in Rachford-Rice Equations for Robust and Efficient
       Three-Phase Split Calculation." Fluid Phase Equilibria 332 (October 25,
       2012): 21-27. https://doi.org/10.1016/j.fluid.2012.06.021.
    .. [3] Gao, Ran, Xiaolong Yin, and Zhiping Li. "Hybrid Newton-Successive
       Substitution Method for Multiphase Rachford-Rice Equations." Entropy 20,
       no. 6 (June 2018): 452. https://doi.org/10.3390/e20060452.
    .. [4] Leibovici, Claude F., and Jean Neoschil. "A Solution of
       Rachford-Rice Equations for Multiphase Systems." Fluid Phase Equilibria
       112, no. 2 (December 1, 1995): 217-21.
       https://doi.org/10.1016/0378-3812(95)02797-I.
    '''
    limit_betas = False

    Ks = [Ks_y, Ks_z] # numba: delete
#    Ks = np.vstack((Ks_y, Ks_z)) # numba: uncomment
    betas = [0.0]*2
    betas[0] = beta_y
    betas[1] = beta_z

    if not Rachford_Rice_valid_solution_naive(ns, betas, Ks, limit_betas=limit_betas):
        raise ValueError("Initial guesses will not lead to convergence")

#    if 0:
#        import matplotlib.pyplot as plt
#        from matplotlib import cm
#        betas = linspace(-10, 10, 500)
#        errs = []
#        for b0 in betas:
#            r = []
#            for b1 in betas:
#                Fs = Rachford_Rice_flashN_f_jac([b0, b1], ns, Ks)[0]
#                err = abs(Fs[0]) + abs(Fs[1])
#                r.append(err)
#            errs.append(r)
#
#        trunc_err_low = 1e-9
#        trunc_err_high = 1e5
#        X, Y = np.meshgrid(betas, betas)
#        z = np.array(errs).T
#        if trunc_err_low is not None:
#            z[np.where(abs(z) < trunc_err_low)] = trunc_err_low
#        if trunc_err_high is not None:
#            z[np.where(abs(z) > trunc_err_high)] = trunc_err_high
#        color_map = cm.viridis
#
#        fig, ax = plt.subplots()
#        im = ax.pcolormesh(X, Y, z, cmap=color_map) # , norm=LogNorm(vmin=trunc_err_low, vmax=trunc_err_high)
#        cbar = fig.colorbar(im, ax=ax)
#        cbar.set_label('Relative error')
#        plt.show()
#    if 0:
#        from scipy.optimize import differential_evolution
#        def obj(x):
#            try:
#                x = x.tolist()
#            except:
#                pass
#            Fs = Rachford_Rice_flashN_f_jac(x, ns, Ks)[0]
#            err = 0.0
#            # if sum(x) > 1:
#            #     err += abs(1-sum(x))
#            err += abs(Fs[0]) + abs(Fs[1])
#            return err
#        ans = differential_evolution(obj, [(-30.0, 30.0) for j in range(2)], **{'popsize':200, 'init': 'random', 'atol': 1e-12})
#        objf = float(ans['fun'])

#    betas, iters = newton_system(Rachford_Rice_flashN_f_jac, x0=betas, jac=True,
#                                        xtol=1e-11, ytol=1e100, maxiter=100,
#                                            args=(ns, Ks), damping=1.0,
#                                           damping_func=RRN_new_betas)
    # Rachford_Rice_flash2_f_jac is over twice as fast! Do not change to the generic one.
    betas, iters = newton_system(Rachford_Rice_flash2_f_jac, x0=betas, jac=True,
                                            xtol=1e-11, ytol=1e100, maxiter=100,
                                           args=(ns, Ks), damping=1.0,
                                           damping_func=RRN_new_betas, solve_func=solve_2_direct)
    beta_y = betas[0]
    beta_z = betas[1]

    N = len(ns)
    xs = [0.0]*N
    ys = [0.0]*N
    zs = [0.0]*N
    z_tot = 0.0
    for i in range(N):
        xi = ns[i]/(1. + beta_y*(Ks_y[i] - 1.0) + beta_z*(Ks_z[i] - 1.0))
        xs[i] = xi
        ys[i] = xi*Ks_y[i]
        zs[i] = xi*Ks_z[i]
        z_tot += zs[i]

    if (1.0 - z_tot) > 1e-10:
        raise ValueError("Converged to nonphysical solution")
    return beta_y, beta_z, xs, ys, zs

