# -*- coding: UTF-8 -*-
# cSpell:ignore mmag

from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle
import astropy.units as u

from kcexo.transit import Transit


def create_transit_schematic(transit: Transit,
                             meridian_flip_duration: u.Quantity["time"],
                             name: str = "",
                             use_times: bool = True,
                             show_labels: bool = True,
                             show_meridian_flip: bool = True,
                             show_twilight: bool = True,
                             ax: Any|None = None) -> None:
    """Create a `matplotlib` plot of the transit profile, label t1, t2, t3, t4, t5 and t6 times
          and show meridian flip time and duration and twilights if so requested.

    Args:
        transit (Transit): The transit that will be plotted.
        meridian_flip_duration (u.Quantity['time']): How long will the meridian flip take?
        name (str, optional): Name of the planet which will be used as the title. Defaults to "" which 
            means that no title will be added.
        use_times (bool, optional): Should actual times be used to annotate the x axis or should 
            relative 1/2 hours from start be used? Defaults to True meaning that times will be used.
        show_labels (bool, optional): Should x and y axis labels be shows? Defaults to True.
        show_meridian_flip (bool, optional): Should meridian flips be shown? Defaults to True.
        show_twilight (bool, optional): Should twilight be shown? Defaults to True.
        ax (Any | None, optional): `matplotlib` axis to use. Defaults to None meaning that a new 
            one will be created.
    """
    if ax is None:
        _, ax = plt.subplots(1,1)
    
    # time offsets
    times = transit.t12345_as_list()
    
    # create the plot
    max_x = 100
    ax.set_xlim(0, max_x)
    full_duration = (transit.post_egress - transit.pre_ingress).to(u.hour).value
    one_hr = max_x / full_duration
    x = [(t-transit.pre_ingress).to(u.hour).value * one_hr for t in times]
    y = [0, 0, transit.depth.value, transit.depth.value, 0, 0]
    if show_labels:
        ax.set_ylabel("Transit Depth (mmag)")
        ax.set_xlabel("Time (hr)")
    ax.invert_yaxis()
    if use_times:
        x2_tick_labels = [t.iso[11:16] for t in times]
        x2_locations = x
        ax.xaxis.set_major_locator(mticker.FixedLocator(x2_locations))
        ax.set_xticklabels(x2_tick_labels, rotation=45, ha='right')
    else:
        xtick_labels = np.arange(0, full_duration, 0.5)
        tic_locations = [e*one_hr/2 for e in range(len(xtick_labels))]
        ax.xaxis.set_major_locator(mticker.FixedLocator(tic_locations))
        ax.set_xticklabels(xtick_labels)
    ax.grid(True)
    ax.plot(x, y, c='blue')
    yminmax = ax.get_ylim()
    # meridian flip
    if show_meridian_flip:
        meridian_flip = (transit.meridian_crossing - transit.pre_ingress).to(u.hour).value
        if meridian_flip > 0 and meridian_flip < full_duration:
            ax.add_patch(Rectangle(xy=(meridian_flip*one_hr, yminmax[1]), height=yminmax[0]-yminmax[1], width=meridian_flip_duration.to(u.hour).value*one_hr, color='red', fill=True, zorder=-10))
    # twilight
    if show_twilight:
        c = ['gray', 'silver', 'lightgray', 'whitesmoke']
        
        for i, tt in enumerate(transit.twilight_e):
            t = (tt - transit.pre_ingress).to(u.hour).value
            if t > 0:
                ax.add_patch(Rectangle(xy=(0, yminmax[1]), height=yminmax[0]-yminmax[1], width=t*one_hr, color=c[i], fill=True, zorder=-i))
        for i, tt in enumerate(transit.twilight_m):
            t = (tt - transit.pre_ingress).to(u.hour).value
            if t < full_duration:
                w = full_duration - t
                ax.add_patch(Rectangle(xy=(t*one_hr, yminmax[1]), height=yminmax[0]-yminmax[1], width=w*one_hr, color=c[-i-1], fill=True, zorder=-(4-i)))
    if name:
        ax.set_title(name)
