# -*- coding: UTF-8 -*-
# cSpell:ignore mmag gainsboro yaxis
import operator
from typing import Tuple

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle
from matplotlib import dates
import astropy.units as u

from kcexo.observatory import Observatory
from kcexo.planet import Planet
from kcexo.transit import Transit


twilight_transparency = [0.6, 0.4, 0.3, 0.15, 0.0]


def _has_twin(ax):
    """
    Solution for detecting twin axes built on `ax`. Courtesy of
    Jake Vanderplas http://stackoverflow.com/a/36209590/1340208
    """
    for other_ax in ax.figure.axes:
        if other_ax is ax:
            continue
        if other_ax.bbox.bounds == ax.bbox.bounds:
            return True
    return False


def create_transit_schematic(transit: Transit,
                             meridian_flip_duration: u.Quantity["time"],
                             name: str = "",
                             use_times: bool = True,
                             show_labels: bool = True,
                             show_meridian_flip: bool = True,
                             show_twilight: bool = True,
                             show_grid: bool=True, 
                             style_kwargs: dict|None = None,
                             fig: matplotlib.figure.Figure|None = None,
                             ax: matplotlib.axes.Axes|None = None
                             ) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
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
        show_grid (bool, optional): Draw the gird? Defaults to True.
        fig (matplotlib.axes.Axes | None, optional): `matplotlib` figure to use. Defaults to None meaning that a new 
            one will be created.
        ax (matplotlib.axes.Axes | None, optional): `matplotlib` axis to use. Defaults to None meaning that a new 
            one will be created.
            
    Returns:
        Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: the figure and the axis
    """
    if ax is None:
        if fig is None:
            fig, ax = plt.subplots(1,1)
        else:
            ax = fig.subplots(1,1)
    if style_kwargs is None:
        style_kwargs = {}
    style_kwargs = dict(style_kwargs)
    # time offsets
    times = transit.t12345_as_list()
    
    # create the plot
    max_x = 100
    ax.set_xlim(0, max_x)
    full_duration = (transit.post_egress - transit.pre_ingress).to(u.hour).value
    one_hr = max_x / full_duration
    x = [(t-transit.pre_ingress).to(u.hour).value * one_hr for t in times]
    y = [0, 0, transit.depth.value, transit.depth.value, 0, 0]
    
    ax.invert_yaxis()
    
    if show_labels:
        ax.set_ylabel("Transit Depth (mmag)")
        ax.set_xlabel("Time (hr)")
    
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
    
    style_kwargs.setdefault('c', 'blue')
    ax.plot(x, y, **style_kwargs)
    
    yminmax = ax.get_ylim()
    
    # meridian flip
    if show_meridian_flip:
        meridian_flip = (transit.meridian_crossing - transit.pre_ingress).to(u.hour).value
        if meridian_flip > 0 and meridian_flip < full_duration:
            ax.add_patch(Rectangle(xy=(meridian_flip*one_hr, yminmax[1]), height=yminmax[0]-yminmax[1], width=meridian_flip_duration.to(u.hour).value*one_hr, color='red', fill=True, zorder=-10))
    
    # twilight
    if show_twilight:
        twilights = []
        twilights.extend([((e - transit.pre_ingress).to(u.hour).value*one_hr, twilight_transparency[i]) for i, e in enumerate(transit.twilight_e)])
        twilights.append(((transit.twilight_e[-1] - transit.pre_ingress).to(u.hour).value*one_hr, 0.0))
        twilights.extend([((e - transit.pre_ingress).to(u.hour).value*one_hr, twilight_transparency[4-i]) for i, e in enumerate(transit.twilight_m)])
        twilights.sort(key=operator.itemgetter(0))
        for i, twi in enumerate(twilights[1:], 1):
            ax.axvspan(twilights[i - 1][0], twilights[i][0],
                       ymin=0, ymax=1, color='grey', alpha=twi[1])
            
    ax.grid(show_grid)
    if name:
        ax.set_title(name)
    return fig, ax


def create_sky_transit(transit: Transit,
                       planet: Planet,
                       obs: Observatory,
                       num_points: int = 20,
                       north_to_east_ccw: bool=False, 
                       show_grid: bool=True, 
                       show_horizon: bool=True,
                       horizon_fill_colour: str = 'gainsboro',
                       az_label_offset: u.Quantity['angle']=0.0*u.deg,
                       style_kwargs: dict|None=None,
                       fig: matplotlib.figure.Figure|None = None,
                       ax: matplotlib.axes.Axes|None = None) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """Draw the polar sky plot.
    
    This is a modification of the `astroplan.plot_sky` function.

    Args:
        transit (Transit): Transit that will be rendered
        planet (Planet): Planet that is transiting
        obs (Observatory): Observatory from which we are observing
        num_points (int, optional): Number of points to plot when drawing the path. Defaults to 20.
        north_to_east_ccw (bool, optional): Should we go from N to E in counter-clockwise direction? Defaults to True.
        show_grid (bool, optional): Draw the gird? Defaults to True.
        show_horizon (bool, optional): Draw the horizon? Defaults to True.
        az_label_offset (u.Quantity['angle'], optional): Where to draw the az labels? Defaults to 0.0*u.deg.
        style_kwargs (dict | None, optional): Additional formatting parameters. Defaults to None.
        fig (matplotlib.axes.Axes | None, optional): `matplotlib` figure to use. Defaults to None meaning that a new 
            one will be created.
        ax (Any | None, optional): Axis to use. Defaults to None so a new one will be created.
    
    Returns:
        Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: the figure and the axis
    """
    
    if ax is None:
        if fig is None:
            fig = plt.figure()
            ax = fig.add_subplot(projection='polar')
        else:
            if isinstance(fig.gca(), plt.PolarAxes):
                ax = fig.gca()
            else:
                fig.clear()
                fig.close()
                fig = plt.figure()
                ax = fig.add_subplot(projection='polar')

    if style_kwargs is None:
        style_kwargs = {}
    style_kwargs = dict(style_kwargs)
    if 'marker' not in style_kwargs:
        style_kwargs.setdefault('marker', '')
    if 'ls' not in style_kwargs and 'fmt' not in style_kwargs:
        style_kwargs.setdefault('linestyle', '-')
    if 'lw' not in style_kwargs:
        style_kwargs.setdefault('linewidth', 2.5)
    
    # Grab altitude and azimuth from Astroplan objects.
    time = transit.pre_ingress + np.linspace(0, (transit.post_egress-transit.pre_ingress).to(u.hour).value, num_points)*u.hour
    altitude = (91 * u.deg - obs.observer.altaz(time, planet.host_star.target).alt) * (1/u.deg)
    # Azimuth MUST be given to plot() in radians.
    azimuth = obs.observer.altaz(time, planet.host_star.target).az * (1/u.deg) * (np.pi/180.0)

    target_name = planet.name
    style_kwargs.setdefault('label', target_name)

    # We only want to plot positions above the horizon.
    az_plot = None
    for alt in range(0, len(altitude)):  # pylint:disable=consider-using-enumerate
        if altitude[alt] <= 91.0:  # because we had to change alt as this was easier than messing around with axis
            if az_plot is None:
                az_plot = np.array([azimuth[alt]])
            else:
                az_plot = np.append(az_plot, azimuth[alt])
    alt_plot = altitude[altitude <= 91.0]
    if az_plot is None:
        az_plot = []

    # More axes set-up.
    # Position of azimuth = 0 (data, not label).
    ax.set_theta_zero_location('N')

    # Direction of azimuth increase. Clockwise is -1
    if north_to_east_ccw is False:
        ax.set_theta_direction(-1)

    # Plot target coordinates.
    #ax.scatter(az_plot, alt_plot, **style_kwargs)
    ax.plot(az_plot, alt_plot, **style_kwargs)

    # Set radial limits.
    ax.set_rlim(1, 91)

    # Grid, ticks & labels.
    # May need to set ticks and labels AFTER plotting points.
    if show_grid is True:
        ax.grid(True, which='major')
    if show_grid is False:
        ax.grid(False)

    # For positively-increasing range (e.g., range(1, 90, 15)),
    # labels go from middle to outside.
    degree_sign = u'\N{DEGREE SIGN}'
    r_labels = [
        '90' + degree_sign,
        '',
        '60' + degree_sign,
        '',
        '30' + degree_sign,
        '',
        '0' + degree_sign + ' Alt.',
    ]

    theta_labels = []
    for chunk in range(0, 7):
        label_angle = (az_label_offset*(1/u.deg)) + (chunk*45.0)
        while label_angle >= 360.0:
            label_angle -= 360.0
        if chunk == 0:
            theta_labels.append('N ' + '\n' + str(label_angle) + degree_sign
                                + ' Az')
        elif chunk == 2:
            theta_labels.append('E' + '\n' + str(label_angle) + degree_sign)
        elif chunk == 4:
            theta_labels.append('S' + '\n' + str(label_angle) + degree_sign)
        elif chunk == 6:
            theta_labels.append('W' + '\n' + str(label_angle) + degree_sign)
        else:
            theta_labels.append(str(label_angle) + degree_sign)
    theta_labels.append('')
    # Set ticks and labels.
    ax.set_rgrids(range(1, 106, 15), r_labels, angle=-45)
    ax.set_thetagrids(range(0, 360, 45), theta_labels)
    
    if show_horizon:
        # create horizon, every 5 degrees
        h = [(x[0]*np.pi/180.0, 91-x[1]) for x in obs.horizon]  # 91 deg offset, see above
        theta = [x[0] for x in h]
        r = [x[1] for x in h]
        #ax.plot(theta, r, c='black')
        ax.fill_between(theta, r, 91, interpolate=True, color=horizon_fill_colour)
    return fig, ax


def create_transit_horizon_plot(transit: Transit,
                                planet: Planet,
                                obs: Observatory,
                                num_points: int = 20,
                                show_meridian_flip: bool=True,
                                show_twilight: bool=True,
                                show_airmass_yaxis: bool=True,
                                show_grid: bool=True, 
                                show_horizon: bool=True,
                                horizon_fill_colour: str = 'gainsboro',
                                style_kwargs: dict|None = None,
                                fig: matplotlib.figure.Figure|None = None,
                                ax: matplotlib.axes.Axes|None = None
                                ) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """Plot the target movement accross the sky along with the horizon beneath it.

    Args:
        transit (Transit): Transit to plot.
        planet (Planet): The planet that is transiting.
        obs (Observatory): Which observatory is observing?
        num_points (int, optional): Number of points to use when plotting the path accross the sky. Defaults to 20.
        show_meridian_flip (bool, optional): Should meridian flips be shown (as red rectangle overlay)? Defaults to True.
        show_twilight (bool, optional): Should twilights be shown (as different shades of gray)? Defaults to True.
        show_airmass_yaxis (bool, optional): Should airmass axis be added? Defaults to True.
        show_grid (bool, optional): Draw the gird? Defaults to True.
        show_horizon (bool, optional): Should horizon be drawn? Defaults to True.
        horizon_fill_colour (str, optional): What colour should be used to mark the horizon. Defaults to 'gainsboro' and no, no one knows what that is.
        style_kwargs (dict | None, optional): _description_. Defaults to None.
        fig (matplotlib.axes.Axes | None, optional): `matplotlib` figure to use. Defaults to None meaning that a new 
            one will be created.
        ax (Any | None, optional): `matplotlib` axis to use. Defaults to None so a new one will be created.

    Returns:
        Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: the figure and the axis
    """
    # Set up plot axes and style if needed.
    if ax is None:
        if fig is None:
            fig, ax = plt.subplots(1,1)
        else:
            ax = fig.subplots(1,1)
    if style_kwargs is None:
        style_kwargs = {}
    style_kwargs = dict(style_kwargs)
    if 'ls' not in style_kwargs and 'fmt' not in style_kwargs:
        style_kwargs.setdefault('linestyle', '-')
    if 'lw' not in style_kwargs:
        style_kwargs.setdefault('linewidth', 1.5)

    # Populate time window if needed.
    time = transit.pre_ingress + np.linspace(0, (transit.post_egress-transit.pre_ingress).to(u.hour).value, num_points)*u.hour
    
    # Calculate airmass
    altaz = obs.observer.altaz(time, transit.host_star.target)
    altitude = altaz.alt
    az = altaz.az
    # Mask out nonsense airmasses
    masked_altitude = np.ma.array(altitude, mask=altitude < 0)

    # Some checks & info for labels.
    try:
        target_name = planet.name
    except AttributeError:
        target_name = ''

    # Plot data
    ax.plot(time.plot_date, masked_altitude, label=target_name, **style_kwargs)

    # Plot the horizon
    if show_horizon:
        y = obs.horizon_interpolator(az)
        ax.fill_between(time.plot_date, [0]*len(y), y, interpolate=True, color=horizon_fill_colour)

    # MF
    if show_meridian_flip:
        ax.axvspan(transit.meridian_crossing.plot_date, (transit.meridian_crossing+obs.meridian_crossing_duration).plot_date, ymin=0, ymax=1, color='red')

    # Format the time axis
    ax.set_xlim([time[0].plot_date, time[-1].plot_date])
    date_formatter = dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(date_formatter)
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    # Shade background during night time
    if show_twilight:
        # Calculate and order twilights and set plotting alpha for each
        twilights = []
        twilights.extend([(e.datetime, twilight_transparency[i]) for i, e in enumerate(transit.twilight_e)])
        twilights.append((transit.twilight_e[-1].datetime, 0.0))
        twilights.extend([(e.datetime, twilight_transparency[4-i]) for i, e in enumerate(transit.twilight_m)])
        twilights.sort(key=operator.itemgetter(0))
        for i, twi in enumerate(twilights[1:], 1):
            ax.axvspan(twilights[i - 1][0], twilights[i][0],
                       ymin=0, ymax=1, color='grey', alpha=twi[1])

    ax.set_ylim([0, 90])

    # Set labels.
    ax.set_ylabel("Altitude")
    ax.set_xlabel(f"{min(time).datetime.date()} [UTC]")

    if show_airmass_yaxis and not _has_twin(ax):
        airmass_ticks = np.array([1, 2, 3])
        altitude_ticks = 90 - np.degrees(np.arccos(1/airmass_ticks))

        ax2 = ax.twinx()
        ax2.set_yticks(altitude_ticks)
        ax2.set_yticklabels(airmass_ticks)
        ax2.set_ylim(ax.get_ylim())
        ax2.set_ylabel('Airmass')

    ax.grid(show_grid)
    return fig, ax
