#!/usr/bin/env python
# -*- coding:utf8 -*-


from lot_basis import lots_list
import html
from kin import *

from molmod.units import kjmol
from molmod.constants import boltzmann

import pylab, numpy

from matplotlib.backend_bases import GraphicsContextBase
GraphicsContextBase.dashd["dashed"] = (0, (6.0, 3.0))
GraphicsContextBase.dashd["dashdot"] = (0, (4.0, 2.0, 1.0, 2.0))
GraphicsContextBase.dashd["dotted"] = (0, (1.5, 1.5))




def overview(template, title, fn_img, rows):
    if len(rows) == 0:
        rows.append([u"<th>Approach→<br />Functional↓</th>"])
        rows.append(["<th></th>"])
    rows[0].append("<th colspan=4>%s</th>" % title.replace(", ", "<br />"))
    for temp in temps:
        rows[1].append("<td style='font-size:small'>%.0fK</td>" % temp)
    lines = []
    labels = []
    pylab.clf()
    line = pylab.plot(invtemps, experimental_k, color="k", linestyle="-", lw=4)
    lines.append(line)
    labels.append("experiment")
    counter = 2
    for lot in lots_list:
        if lot.spin == "ROS":
            lot_label = "ro" + lot.label
        else:
            lot_label = lot.label
        if len(rows) <= counter:
            rows.append(["<th>%s</th>" % lot_label])
        try:
            ks = load_summary(template % lot_label)[0]
            line = pylab.plot(invtemps, ks, color=lot.color, linestyle=lot.linestyle, lw=2)
            lines.append(line)
            labels.append(lot_label)
            for j in xrange(4):
                ln10ratio = numpy.log10(ks[j]/experimental_k[j])
                color = get_error_color(ln10ratio)
                rows[counter].append("<td style='background-color:%s'>%.0f</td>" % (color, ln10ratio*10))
        except IOError, StopIteration:
            rows[counter].append("<td>&nbsp</td><td>&nbsp</td><td>&nbsp</td><td>&nbsp</td>")
        counter += 1
    pylab.semilogy()
    pylab.fill(
        numpy.concatenate((invtemps, invtemps[::-1])),
        numpy.concatenate((experimental_k*10, experimental_k[::-1]/10)),
        "k", alpha=0.2, lw=0,
    )
    pylab.xticks(
        1/numpy.array([300, 350, 400, 450, 500, 550, 600], float),
        ["300", "350", "400", "450", "500", "550", "600"],
    )
    pylab.title(title)
    pylab.xlabel("T [K]")
    pylab.ylabel("k [(m**3/mol)/s]")
    pylab.ylim(1e-8,1e7)
    legend = pylab.figlegend(
        lines, labels, (0.07,0.06), ncol=3, prop={"size":11},
        handlelength=3, labelspacing=0.1, columnspacing=1
    )
    #legend.get_frame().set_linewidth(0)
    legend.get_frame().set_fill(True)
    legend.get_frame().set_alpha(0.5)
    pylab.savefig(fn_img % "rates")

    pylab.clf()
    lines = []
    labels = []
    line = pylab.plot([experimental_Ea], [experimental_A], color="k", marker="o", ms=11, mew=2, lw=0, ls=" ")
    lines.append(line)
    labels.append("experiment")
    for lot in lots_list:
        if lot.spin == "ROS":
            label = "ro" + lot.label
        else:
            label = lot.label
        try:
            A, Ea = load_summary(template % label)[1]
            marker = {"-": "o", "--": "s", ":": "v", "-.": "h"}[lot.linestyle]
            line = pylab.plot([Ea], [A], color=lot.color, marker=marker, ms=11, mew=2, lw=0, ls=" ")
            lines.append(line)
            labels.append(label)
            continue
        except IOError, StopIteration:
            pass

    pylab.title(title)
    pylab.xlabel("Activation energy [kJ/mol]")
    pylab.ylabel("Pre-exponential factor [(m**3/mol)/s]")
    pylab.semilogy()
    # error margin around experimental data point
    x = []
    y = []
    evals, evecs = numpy.linalg.eigh(covariance_parameters)
    angles = numpy.arange(0.0,360.5,1.0)/180*numpy.pi
    data = numpy.outer(evecs[:,0],numpy.cos(angles))*numpy.sqrt(evals[0]) + \
           numpy.outer(evecs[:,1],numpy.sin(angles))*numpy.sqrt(evals[1])
    pylab.fill(
        experimental_parameters[1] + data[1],
        numpy.exp(experimental_parameters[0] + data[0]),
        color="k", alpha=0.2, lw=0
    )
    # end error margin
    legend = pylab.legend(
        lines, labels, loc=4, ncol=4, prop={"size":11},
        handlelength=1, labelspacing=0.2, columnspacing=2,
        numpoints=1,
    )
    pylab.xlim(0,90)
    pylab.ylim(1e3,1e7)
    #legend.get_frame().set_linewidth(0)
    legend.get_frame().set_fill(True)
    legend.get_frame().set_alpha(0.5)
    pylab.savefig(fn_img % "params")




f = file("kintab.html", "w")
print >> f, html.header % "KIN Overview"

for do_rotor in False, True:
    ir_str = {True: "ir", False: "ho"}[do_rotor]
    ir_info = {
        True: "internal rotor",
        False: "harmonic oscillator",
    }[do_rotor]
    for do_counterpoise in False, True:
        cp_str = {True: "cps", False: "bss"}[do_counterpoise]
        cp_info = {
            True: "with counterpoise correction",
            False: "without counterpoise correction",
        }[do_counterpoise]

        rows = []

        for ts_conformer in "Gauche", "Trans":
            overview(
                "%%s__6-31gd/%s_%s_summary_%s.txt" % (ir_str, cp_str, ts_conformer.lower()),
                "%s, %s, %s, Consistent, 6-31G(d)" % (ir_str.upper(), cp_str.upper(), ts_conformer),
                "kin_%s_%s_%s_consistent_6-31gd_%%s.pdf" % (ir_str, cp_str, ts_conformer.lower()),
                rows,
            )
        for ts_conformer in "Gauche", "Trans":
            overview(
                "%%s__6-311+g3df2p/%s_%s_summary_%s.txt" % (ir_str, cp_str, ts_conformer.lower()),
                "%s, %s, %s, Consistent, 6-311+G(3df,2p)" % (ir_str.upper(), cp_str.upper(), ts_conformer),
                "kin_%s_%s_%s_consistent_6-311+g3df2p_%%s.pdf" % (ir_str, cp_str, ts_conformer.lower()),
                rows,
            )
        for ts_conformer in "Gauche", "Trans":
            overview(
                "GEO__b3lyp__6-31gd__ENERGY__%%s__6-311+g3df2p/%s_%s_summary_%s.txt" % (ir_str, cp_str, ts_conformer.lower()),
                "%s, %s, %s, GEO=B3LYP/6-31G(d), 6-311+G(3df,2p)" % (ir_str.upper(), cp_str.upper(), ts_conformer),
                "kin_%s_%s_%s_geo_6-311+g3df2p_%%s.pdf" % (ir_str, cp_str, ts_conformer.lower()),
                rows,
            )

        print >> f, "<p>10Log10 of ratio between theoretical and experimental rate (%s, %s)</p>" % (ir_info, cp_info)
        html.print_table(f, rows)

print >> f, html.footer
