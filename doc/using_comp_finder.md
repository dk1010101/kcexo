# Using the comparator star finding tool

Selecting good comparator stars is a tricky process and using SIMBAD
website etc is a pain. The comparator tool helps with this process by
using actual (reduced) science images and annotating possible comparator
stars on it while allowing these stars to be filtered in various ways.
Additionally it also highlights known variable stars so that they are
definitely *not* chosen. For example:

![Example of the comparator star finder tool in action](doc/images/comp_stars/main.png)

The comparator tools expects science images to be fully reduced, so with
bias (is on CCD), dark and flats subtracted. This science image is then
used to define the field of view using WCS if the image had already been
solved. It not, it is solved using ASTAP. WCS, ideally should also have
SIP. The WCS is used to work out the FOV extent as well as for
translating cursor movements in the RA/DEC coordinates. This FOV is then
used to query SIMBAD for all stars in the field (up to some fixed
magnitude which is arbitrarily set to 16). The stars then have their
colour calculated and are plotted on the science image while all the
star details are presented in a table underneath. The image can be
zoomed, translated, flipped or mirrored and stretched in various ways to
help you locate the stars on whatever other tool you may be using (HOPS,
we hope). If you really want, you can also export the star table to CSV.

Note that **all** stars in the field are returned and that this includes
variable stars (which are highlighted in yellow on the science image).
This is so that you can be sure NOT to choose them as comparators. Of
course, all stars are variable but that is a conversation for some other
time\...

As a reminder, when selecting the \"best\" comparator stars you should
select stars that are:

*   not variable (ie not highlighted in yellow),
*   close to the target star,
*   have similar colour to the target star so that their B-V or
    Gbp-Grp values are similar to the target\'s,
*   have similar magnitude to the target star (ideally in the band you
    are using but good luck with that if you are using r, cR or
    beyond),
*   are not saturated, so be careful of stars that are brighter than
    the target. You can do a rough guesstimate of the flux by
    stretching the image a bit and looking at the star flux spread.
    Stars with the similar brightness will be of similar size.

Good Luck!

