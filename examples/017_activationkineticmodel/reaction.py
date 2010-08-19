#!/usr/bin/env python
# TAMkin is a post-processing toolkit for thermochemistry and kinetics analysis.
# Copyright (C) 2008-2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>,
# Matthias Vandichel <Matthias.Vandichel@UGent.be> and
# An Ghysels <An.Ghysels@UGent.be>, Center for Molecular Modeling (CMM), Ghent
# University, Ghent, Belgium; all rights reserved unless otherwise stated.
#
# This file is part of TAMkin.
#
# TAMkin is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following five articles:
#
# "Vibrational Modes in partially optimized molecular systems.", An Ghysels,
# Dimitri Van Neck, Veronique Van Speybroeck, Toon Verstraelen and Michel
# Waroquier, Journal of Chemical Physics, Vol. 126 (22): Art. No. 224102, 2007
# DOI:10.1063/1.2737444
#
# "Cartesian formulation of the Mobile Block Hesian Approach to vibrational
# analysis in partially optimized systems", An Ghysels, Dimitri Van Neck and
# Michel Waroquier, Journal of Chemical Physics, Vol. 127 (16), Art. No. 164108,
# 2007
# DOI:10.1063/1.2789429
#
# "Calculating reaction rates with partial Hessians: validation of the MBH
# approach", An Ghysels, Veronique Van Speybroeck, Toon Verstraelen, Dimitri Van
# Neck and Michel Waroquier, Journal of Chemical Theory and Computation, Vol. 4
# (4), 614-625, 2008
# DOI:10.1021/ct7002836
#
# "Mobile Block Hessian approach with linked blocks: an efficient approach for
# the calculation of frequencies in macromolecules", An Ghysels, Veronique Van
# Speybroeck, Ewald Pauwels, Dimitri Van Neck, Bernard R. Brooks and Michel
# Waroquier, Journal of Chemical Theory and Computation, Vol. 5 (5), 1203-1215,
# 2009
# DOI:10.1021/ct800489r
#
# "Normal modes for large molecules with arbitrary link constraints in the
# mobile block Hessian approach", An Ghysels, Dimitri Van Neck, Bernard R.
# Brooks, Veronique Van Speybroeck and Michel Waroquier, Journal of Chemical
# Physics, Vol. 130 (18), Art. No. 084107, 2009
# DOI:10.1063/1.3071261
#
# TAMkin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


# Import the tamkin libarary.
from tamkin import *
# Import unit conversin factors
from molmod import *
# Import numpy stuff
from numpy import *

###
### reaction can be split up into two parts (HAA = acetic acid):
### activation part: VO(AA)(OH)--H2O + TBHP <=> VO(AA)(OOtBu) + 2H2O
### reaction part (oxygen transfer reaction): VO(AA)(OOtBu) + cyclohexene -> VO(ACAC)(OtBu) + cyclohexene-epoxide
###
# yclohexene  reaction.py  TBHP  TS  VO_AA_OOtBu  water

nma_H2O = NMA(load_molecule_g03fchk("water/gaussian.fchk"))
nma_VO_AA_OH_H2O = NMA(load_molecule_g03fchk("VO_AA_OH_H2O/gaussian.fchk"))
nma_VO_AA_OOtBu = NMA(load_molecule_g03fchk("VO_AA_OOtBu/gaussian.fchk"))
nma_TBHP = NMA(load_molecule_g03fchk("TBHP/gaussian.fchk"))
nma_TS = NMA(load_molecule_g03fchk("TS/TS.fchk"))
nma_cyclohexene = NMA(load_molecule_g03fchk("cyclohexene/gaussian.fchk"))

pf_H2O = PartFun(nma_H2O, [ExtTrans(), ExtRot(2),Vibrations(freq_scaling=1.0, zp_scaling=1.0)])
pf_VO_AA_OH_H2O = PartFun(nma_VO_AA_OH_H2O, [ExtTrans(), ExtRot(1),Vibrations(freq_scaling=1.0, zp_scaling=1.0)])
pf_VO_AA_OOtBu = PartFun(nma_VO_AA_OOtBu, [ExtTrans(), ExtRot(1),Vibrations(freq_scaling=1.0, zp_scaling=1.0)])
pf_TBHP = PartFun(nma_TBHP, [ExtTrans(), ExtRot(1),Vibrations(freq_scaling=1.0, zp_scaling=1.0)])
pf_TS =  PartFun(nma_TS, [ExtTrans(), ExtRot(1),Vibrations(freq_scaling=1.0, zp_scaling=1.0)])
pf_cyclohexene = PartFun(nma_cyclohexene, [ExtTrans(), ExtRot(1),Vibrations(freq_scaling=1.0, zp_scaling=1.0)])

# One can compute the equilibrium coefficient for the activation reaction and the forward coefficient for the reaction separately:

# Thermodynamic model
tm = ThermodynamicModel([pf_VO_AA_OH_H2O,pf_TBHP],[pf_VO_AA_OOtBu,pf_H2O,pf_H2O],cp=True)
print tm.compute_equilibrium_constant(323.0,do_log=False),tm.compute_delta_free_energy(323.0)/kjmol

# Kinetic model
km = KineticModel([pf_VO_AA_OOtBu,pf_cyclohexene],pf_TS,cp=True,tunneling=None)
print km.compute_rate_coeff(323.0,do_log=False), km.compute_delta_free_energy(323.0)/kjmol
print tm.compute_equilibrium_constant(323.0,do_log=False)*km.compute_rate_coeff(323.0,do_log=False)

ra = ReactionAnalysis(km, 273, 373.1, temp_step=10)
ra.plot_arrhenius("arrhenius.png") # make the Arrhenius plot

# Estimate the error on the kinetic parameters due to level of theory artifacts
# with Monte Carlo sampling. The monte_carlo method takes three optional
# arguments:
#  1) freq_error: the absolute stochastic error on the frequencies (default=1*invcm)
#  2) energy_error: the absolute error on the energy (default=0.0)
#  3) num_iter: the number of monte carlo samples (default=100)
ra.monte_carlo()
# plot the parameters, this includes the monte carlo results
ra.plot_parameters("parameters.png")
# write all results to a file.
ra.write_to_file("reaction.txt") # summary of the analysis


# Or one can determine a global k value and fit this within a temperature region by making use of the class ActivationKineticModel
akm = ActivationKineticModel(tm,km)
print akm.compute_rate_coeff(323.0), akm.compute_delta_free_energy(323.0)/kjmol
akm.write_to_file("activation_model.txt")