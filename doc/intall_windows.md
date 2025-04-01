# Installing on windows

How you install will depend on if you are using Anaconda or vanilla
Python but either way we recommend using virtual environments. If you
really do not want to using virtual environments have a look further
down.

Before you stars, make sure that you have:

*   Python (version 3.12 or above) either vanilla or Anaconda
    (recommended)
*   ASTAP which you can get from the [ASTAP
    website](https://www.hnsky.org/astap.htm) and you may choosealso
    to get a decent star library as well but that is optional

## Anaconda

To install under anaconda you will need to create a directory for KCEXO,
create a virtual environment, install the library and then copy some
helpful scripts:

~~~
    > cd <YOUR ROOT DIRECTORY OF CHOICE>
    > mkdir kcexo
    > cd kcexo
    > conda create -n kcexo anaconda
    > conda activate kcexo
    > git clone https://github.com/dk1010101/kcexo.git
    > pip install kcexo
    > copy kcexo\exec\conda_kc_comp_stars.bat kc_comp_stars.bat
~~~

Profit!

## Vanilla Python

To install under anastraight python you will need to create a directory
for KCEXO, create a virtual environment, install the library and then
copy some helpful scripts:

~~~
    > cd <YOUR ROOT DIRECTORY OF CHOICE>
    > mkdir kcexo
    > cd kcexo
    > python -m venv .kcexo
    > .kcexo\Scripts\activate
    > git clone https://github.com/dk1010101/kcexo.git
    > pip install kcexo
    > copy kcexo\exec\v_kc_comp_stars.bat kc_comp_stars.bat
~~~

From now on you can start the comparator finder tool by running
[kc_comp_stars.bat]{.title-ref} and you can even create a desktop link
for it if you like.

## No Virtual environments

While this is the simplest approach, are you sure? Really sure? OK\...:

~~~
    > cd <YOUR ROOT DIRECTORY OF CHOICE>
    > git clone https://github.com/dk1010101/kcexo.git
    > pip install kcexo
~~~

done. To run the comparator star tool just run:

~~~
    > kc_comp_stars.exe
~~~

Easy.
