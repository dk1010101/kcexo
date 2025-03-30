Collection of exoplanet-related classes and operations
======================================================

What is included?
-----------------

At the moment, there are two main components:
    1. a library with various approaches to calculate and plan exoplanet observations
    2. a tool `kc_comp_stars.exe` that can be used to analyse existing reduced images
       and find decent comparator stars. Finding decent comparator stars is not guaranteed...


Using the comparator tool
-------------------------

The comparator tools expects to be given a good, reduced, science frame that will be used to
determine instrument's field of view. This FOV is then used to query SIMBAD for all stars in
the field (up to some fixed magnitude which is arbitrarily set to 16). The stars then have their
colour calculated and are then plotted on the science image while all the details are presented
in a table. The image can be zoomed, translated, flipped or mirrored and stretched in various 
ways to help you locate the stars on whatever other tool you may be using (HOPS, we hope). If you 
really want, you can also export the star table to CSV.

Note that all stars are returned and that known variable stars are highlighted in yellow. This
is so that you can be sure NOT to choose them as comparators. Of course, all stars are variable
stars but that is a conversation for some other time...

To run the tool just install the library::

    > git clone https://github.com/dk1010101/kcexo.git
    > pip install kcexo

then run the tool (on windows)::

    > kc_comp_stars.exe

Profit!


Debt
----

This collection is based on work by many other people. Some of the code was directly lifted from
Angelos Tsiaras's HOPS package and we are eternally grateful to him for writing this code. We also used

    * `astropy`
    * `astroplan`
    * `numpy`
    * `pyvo`
    * `scipy`
    * `matplotlib`
    * `wxpython`

which are all awesome libraries!

Additionally we "borrowed" the code for range slider from Gabriel Pasa (https://gist.github.com/gabrieldp/e19611abead7f6617872d33866c568a3). 
Thank you Gabriel!


License
-------

This project is Copyright (c) Daniel Kustrin and licensed under
the terms of the GNU GPL v3+ license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

Contributing
------------

We love contributions! kcexo is open source,
built on open source, and we'd love to have you help out!

**Imposter syndrome disclaimer**: We want your help. No, really.

Please make changes, improvements or more! Just let us know ahead of time.

Being an open source contributor doesn't just mean writing code, either. You can
help out by writing documentation, tests, or even giving feedback about the
project. Some of these contributions may be the most valuable to the project as
a whole, because you're coming to the project with fresh eyes, so you can see
the errors and assumptions that seasoned contributors have glossed over.
