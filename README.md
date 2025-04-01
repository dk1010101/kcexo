![KCEXO](doc/images/kcexo.png)

# Collection of exoplanet-related classes and operations

## What is included?

At the moment, there are two main components:

 1.  a library collecting various calculations and data manipulations that are useful for planning and analysing exoplanet observations
 2.  a tool that can help in finding the \"best\" comparator stars for an exoplanet or variable star observation


## Installing KCEXO

To install the library you will need:

* [python](https://www.python.org/downloads/) but we recommend [anaconda](https://www.anaconda.com/download)
* [GIT](https://git-scm.com/downloads)
* [ASTAP](https://www.hnsky.org/astap.htm)

For installing on Windows have a look [here](doc/install_windows.md)
and for Linux have a look [here](doc/install_linux.md). If you are on
Mac, well, have a look at Linux as Mac is really just re-badged BSD UNIX which is close to linux
so that should/may work.

## Usage

You can find more information about how to use the comparator finder tool [here](doc/using_comp_finder.md).

## Future

There are a couple of tools being developed, one that can be used for
planning of exoplanet observations longer-term and one that is used for
more short term (day-before) [planning](doc/planner.md).

## Debt

This collection is based on work by many other people. Some of the code
was directly lifted from Angelos Tsiaras\'s [HOPS
package](https://github.com/ExoWorldsSpies/hops). Angelos is a star and
we are eternally grateful to him for writing this code. We also used

* [astropy](https://www.astropy.org/)
* [astroplan](https://astroplan.readthedocs.io/en/stable/)
* [astroquery](https://astroquery.readthedocs.io/en/latest/)
* [pyvo](https://pyvo.readthedocs.io/en/latest/)
* [numpy](https://numpy.org/)
* [scipy](https://scipy.org/)
* [matplotlib](https://matplotlib.org/)
* [wxpython](https://www.wxpython.org/)

which are all awesome libraries!

Additionally, we \"borrowed\" code for range sliders from Gabriel Pasa
(<https://gist.github.com/gabrieldp/e19611abead7f6617872d33866c568a3>).
Thank you Gabriel!

## License

This project is Copyright (c) Daniel Kustrin and licensed under the
terms of the GNU GPL v3+ license. This package is based upon the
(much modified) [Openastronomy packaging
guide](https://github.com/OpenAstronomy/packaging-guide) which is
licensed under the BSD 3-clause licence. 

## Contributing

We love contributions! kcexo is open source, built on open source, and
we\'d love to have you help out!

Please make changes, improvements or more! Just let us know ahead of
time.

Being an open source contributor doesn\'t just mean writing code,
either. You can help out by writing documentation, tests, or even giving
feedback about the project. Some of these contributions may be the most
valuable to the project as a whole, because you\'re coming to the
project with fresh eyes, so you can see the errors and assumptions that
seasoned contributors have glossed over.
