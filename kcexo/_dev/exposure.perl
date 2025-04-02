# FROM http://spiff.rit.edu/richmond/signal.shtml
#
#!/usr/bin/perl -w
# Perl script to handle HTML interface to the "signal-to-noise" program.
#    MWR 1/15/2001
# 
# Modified to add some choices for QE and sky brightness.
#    MWR 1/21/2001
#
# Modified to include list of parameters at top of output.
#    MWR 1/22/2001
#
# Added extinction into calculations.
#    MWR 3/7/2001
#        
# Fixed typo in list of zero-point photon flux for B-band
#    was      $nphot = 3.91e+06;
#    now      $nphot = 3.91e+05;
#    MWR 4/18/2002
#
# Fixed small error in "fraction_inside_slow", which was incorrectly
#    _adding_ the area of each sub-pixel unit to the sum at the end
#    of each pixel's calculation, instead of _multiplying_ the intensity
#    times this area.  Thanks to John Mahony for noticing this.
#    MWR 4/6/2003
#
# Fixed a bug in addition of light within 
#    the given aperture; wasn't handling addition of light within fractional
#    pixel apertures properly.  Thanks to David Whysong.
#    MWR 3/2/2004
#
# Modified to make the "fraction_inside_slow" function more accurate.
#      - now assumes star falls on center of one pixel (not junction of 4)
#      - now integrate explicitly over all four quadrants of the PSF,
#           instead of just doing one quadrant
#      - fix expression for x,y position of each sub-pixel location
#      - decreased "max_pix_rad" from 50->30 to speed up a bit
#    MWR 8/30/2004
#
# Moved from stupendous to spiff.  
#      - changed from "require ./cgi-lib.pl" to "use CGI", 
#              and modified function calls accordingly
#    MWR 12/28/2016
#
# Replaced 'CgiDie' with regular old 'die', 
#         after using CGI::Carp to cause 'die' to send messages to browser
#    MWR 12/29/2018
#
# Replaced 'HtmlBot' with 'CGI::HtmlBot' to fix my earlier oversight.
#
#    MWR 7/5/2020

use strict;
#require "./cgi-lib.pl";
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Math::Cephes qw(:misc);
use Math::Cephes qw(:utils);

$ENV{'PATH'} = '/bin:/usr/bin:' ;

MAIN:
{


  my (%input,   # The CGI data
      $text,    # Munged version of the text field entered by the user
      $debug,
      $a, $b, $c, $x,   # some variables we'll use
      $pi,
      $filter,
      $nmagstep,    
      $nphoton,
      $mag,
      $tel_diam,          # in centimeters
      $fixed_qe, $var_qe, $qe,
      $pixsize,
      $readnoise,
      $fixed_sky, $var_sky, $skymag,
      $airmass,
      $extinct_coeff,
      $exptime,
      $fwhm,
      $aper_rad,
      $dmag,
      $mag_start, $mag_end,
      $star_electrons,
      $sky_electrons,
      $sky_electrons_per_pix,
      $read_electrons,
      $npix,
      $fraction,
      $signal, 
      $noise,
      $signal_to_noise,
      $result,  # result of SQL query,
      $field);  

  # set this to 1 for lots of debugging messages
  $debug = 0;

  $pi = 3.14159;

  # Read in all the variables set by the form
  &CGI::ReadParse(\%input);


  # Check that everything has been entered
  foreach $field (qw(source user_name filter mag_start mag_end dmag 
                     tel_diam fixed_qe var_qe pixsize readnoise 
                     fixed_sky var_sky airmass 
                     exptime fwhm aper_rad)) {
#   &CGI::CgiDie("Error: Missing field '$field'\n") unless defined $input{$field};
   die("Error: Missing field '$field'\n") unless defined $input{$field};
  }

  print &CGI::PrintHeader;
  print &CGI::HtmlTop ("Signal-to-noise calculations");

  # create local variables for the RA, Dec, mag limits -- is convenient 
  $filter = $input{'filter'} ;
  $mag_start = $input{'mag_start'} ;
  $mag_end = $input{'mag_end'} ;
  $dmag = $input{'dmag'} ;
  $tel_diam = $input{'tel_diam'} ;
  $fixed_qe = $input{'fixed_qe'} ;
  $var_qe = $input{'var_qe'} ;
  $readnoise = $input{'readnoise'} ;
  $pixsize = $input{'pixsize'} ;
  $fixed_sky = $input{'fixed_sky'} ;
  $var_sky = $input{'var_sky'} ;
  $airmass = $input{'airmass'} ;
  $exptime = $input{'exptime'} ;
  $fwhm = $input{'fwhm'} ;
  $aper_rad = $input{'aper_rad'} ;

  #
  # check for validity of values supplied by user

  if (($mag_start > $mag_end) || ($dmag <= 0.0)) {
#    &CGI::CgiDie("Error: invalid magnitude start/end or delta values ") ;
    die("Error: invalid magnitude start/end or delta values ") ;
  }
  if ($tel_diam <= 0.0) {
#    &CGI::CgiDie("Error: invalid telescope diameter, must be greater than 0 ") ;
    die("Error: invalid telescope diameter, must be greater than 0 ") ;
  }

  if ($fixed_qe eq "use value at right") {
    $qe = $var_qe;
    if ($debug > 0) {
      printf "<br> qe based on var value is ..%s.. <br> \n", $qe;
    }
  } else {
    $qe = $fixed_qe;
    $qe =~ s/.*: //;
    if ($debug > 0) {
      printf "<br> qe based on fixed value is ..%s.. <br> \n", $qe;
    }
  }
  if (($qe <= 0.0) || ($qe > 1.0)) {
#    &CGI::CgiDie("Error: invalid QE, must be between 0.0 and 1.0 ") ;
    die("Error: invalid QE, must be between 0.0 and 1.0 ") ;
  }

  if ($pixsize <= 0.0) {
#    &CGI::CgiDie("Error: invalid pixel size, must be greater than 0 ") ;
    die("Error: invalid pixel size, must be greater than 0 ") ;
  }
  if ($readnoise < 0.0) {
#    &CGI::CgiDie("Error: invalid readnoise, must be >= 0 ") ;
    die("Error: invalid readnoise, must be >= 0 ") ;
  }

  if ($fixed_sky eq "use value at right") {
    $skymag = $var_sky;
    if ($debug > 0) {
      printf "<br> skymag based on var value is ..%s.. <br> \n", $skymag;
    }
  } else {
    $skymag = $fixed_sky;
    $skymag =~ s/.*: //;
    if ($debug > 0) {
      printf "<br> skymag based on fixed value is ..%s.. <br> \n", $skymag;
    }
  }
  if (($skymag < 0.0) || ($skymag > 100.0)) {
#    &CGI::CgiDie("Error: invalid skymag, must be between 0.0 and 100.0 ") ;
    die("Error: invalid skymag, must be between 0.0 and 100.0 ") ;
  }

  if ($exptime <= 0.0) {
#    &CGI::CgiDie("Error: invalid exposure time, must be greater than 0 ") ;
    die("Error: invalid exposure time, must be greater than 0 ") ;
  }
  if ($fwhm <= 0.0) {
#    &CGI::CgiDie("Error: invalid FWHM, must be greater than 0 ") ;
    die("Error: invalid FWHM, must be greater than 0 ") ;
  }
  if ($aper_rad <= 0.0) {
#    &CGI::CgiDie("Error: invalid aperture radius, must be greater than 0 ") ;
    die("Error: invalid aperture radius, must be greater than 0 ") ;
  }

  # get the extinction coefficient appropriate for this filter
  $extinct_coeff = get_extinct_coeff($filter);


  if ($debug > 0) {
    print "here is a list of the variables you entered...\n";
    print "<p>\n";
    print "filter ..$filter.. <br>";
    print "mag_start ..$mag_start.. mag_end ..$mag_end.. dmag ..$dmag..<br>";
    print "tel_diam ..$tel_diam.. <br>";
    print "qe ..$qe.. <br>";
    print "pixsize ..$pixsize.. <br>";
    print "readnoise ..$readnoise.. <br>";
    print "skymag ..$skymag.. <br>";
    print "airmass ..$airmass.. <br>";
    print "extinction_coeff ..$extinct_coeff.. <br>";
    print "exptime ..$exptime.. <br>";
    print "fwhm ..$fwhm.. <br>";
    print "aper_rad ..$aper_rad.. <br>";
  }


  print "<pre>";

  # print out values we'll use in the calculations, for reference

  if (1 == 1) {
    printf "Filter:     $filter \n";
    printf "Tel_diam:   $tel_diam (cm) \n";
    printf "Overall QE: $qe \n";
    printf "Pixsize:    $pixsize (arcsec/pixel) \n";
    printf "Readnoise   $readnoise (electrons) \n";
    printf "Sky mag:    $skymag (mag/sq.arcsec) \n";
    printf "Airmass:    $airmass \n";
    printf "Ext_coeff:  $extinct_coeff \n";
    printf "Exptime:    $exptime (sec) \n";
    printf "FWHM:       $fwhm (arcsec) \n";
    printf "Aper_rad:   $aper_rad (arcsec) \n";
    printf "\n";
  }

  # prepare to perform calculations

  # get the number of photons from a mag-zero star per sq.cm. per sec
  #    (this should be a function taking as arg the filter)
  $nphoton = mag_zeropoint($filter);
  if ($nphoton < 0) {
    printf "Error: bad magnitude zeropoint for filter %s?\n", $filter;
    print "</pre>" ;
    print &CGI::HtmlBot("HtmlBot");
    exit(0);
  }
  
  
  # how many pixels are inside the aperture?
  $npix = ($pi*$aper_rad*$aper_rad)/($pixsize*$pixsize);

  # what fraction of star's light falls within aperture?
  #   use this for quicker, less accurate result
  # $fraction = fraction_inside($fwhm, $aper_rad);
  if ($debug > 0) {
    printf "npix %7.2f  fraction %6.3f  \n", $npix, $fraction;
  }
  #
  # or use this for slower, more accurate result
  $fraction = fraction_inside_slow($fwhm, $aper_rad, $pixsize);
  if ($debug > 0) {
    printf "npix %7.2f  fraction %6.3f  \n", $npix, $fraction;
  }

  # now enter the main loop
  for ($mag = $mag_start; $mag <= $mag_end; $mag += $dmag) {

    # calculate # of electrons collected on the CCD from star, total
    $x = pow(10.0, -0.4*$mag)*$nphoton;
    $x *= $exptime;
    $x *= $pi*$tel_diam*$tel_diam*0.25;
    $x *= $qe;
    $star_electrons = $x;

    # decrease the # of electrons from star, due to extinction 
    $x = $airmass * $extinct_coeff;
    $star_electrons *= pow(10.0, -0.4*$x);

    # now calculate # of electrons collected on CCD from sky, per pixel
    $x = pow(10.0, -0.4*$skymag)*$nphoton;
    $x *= $exptime;
    $x *= $pi*$tel_diam*$tel_diam*0.25;
    $x *= $qe;
    $x *= $pixsize*$pixsize;
    $sky_electrons_per_pix = $x;

    if ($debug > 0) {
      printf "<br> mag %5.2f   star_e %10.4e  sky_e %10.4e <br>\n",
          $mag, $star_electrons, $sky_electrons_per_pix;
    }

    # this is the total number of electrons from star inside aperture
    $star_electrons *= $fraction;

    # this is the total number of electrons from sky inside aperture
    $sky_electrons = $sky_electrons_per_pix*$npix;

    # this is the total number of electrons from readout in aperture 
    $read_electrons = $readnoise*$readnoise*$npix;

    # now we can calculate signal-to-noise
    $signal = $star_electrons;
    $noise = sqrt($read_electrons + $sky_electrons + $star_electrons);
    $signal_to_noise = $signal/$noise;

    # print out the answer
    printf "mag %6.2lf:  star %12.0lf sky %10.0lf read %7.0lf -> S/N %9.2lf ",
          $mag, $star_electrons, $sky_electrons, $read_electrons, 
          $signal_to_noise;
    printf "\n";

  }

  print "</pre>" ;
  print &CGI::HtmlBot("HtmlBot");

  exit(0);
}


############################################################################
# PROCEDURE: fraction_inside
# 
# DESCRIPTION: figure out what fraction of a star's light falls within
#              the aperture.  We assume that the starlight has a circular
#              gaussian distribution with FWHM given by the first argument
#              (with units of arcsec).  We calculate the fraction of 
#              that light which falls within an aperture of radius given
#              by second argument (with units of arcsec).
#              
# RETURNS:     the fraction of light within aperture.
#
sub fraction_inside {


  my(
    $fwhm,           # FWHM of gaussian distribution of light
    $radius,         # radius of circular aperture
    $sigma,
    $z, 
    $x1, $x2,
    $large,
    $ratio
    );

  $fwhm = $_[0];
  $radius = $_[1];

  $large = 1000.0;

  # calculate how far out the "radius" is in units of "sigmas" 
  $sigma = $fwhm/2.35;
  $z = $radius/($sigma*1.414);
  
  # now, we assume that a radius of "large" is effectively infinite
  $x1 = erf($z);
  $ratio = ($x1*$x1);

  return($ratio);
}



############################################################################
# PROCEDURE: fraction_inside_slow
# 
# DESCRIPTION: figure out what fraction of a star's light falls within
#              the aperture.  We assume that the starlight has a circular
#              gaussian distribution with FWHM given by the first argument
#              (with units of arcsec).  
#               
#              This function goes to the trouble of calculating how
#              much of the light falls within fractional pixels defined
#              by the given radius of a synthetic aperture.  It is slow,
#              but more accurate than the "fraction_inside" function.
#
#              3/2/2004  Fixed a bug in addition of light within 
#                        the given aperture; wasn't handling fractional
#                        pixel apertures properly.  Thanks to David Whysong.
#                        MWR
#
#              8/30/2004 By default, the code now assumes that the star
#                        is centered on a pixel (not on the junction of 
#                        four adjacent pixels).  It now also takes into
#                        account the pixel size.
#              
# RETURNS:     the fraction of light within aperture.
#
sub fraction_inside_slow {


  my(
    $fwhm,                # arg 1: FWHM in arcsec
    $radius,              # arg 2: radius of aperture, in arcsec
    $pixsize,             # arg 3: size of a pixel, in arcsec
    $i, $j, $k, $l, 
    $max_pix_rad,
    $sigma2, 
    $x, $y, 
    $fx, $fy,
    $psf_center_x, $psf_center_y,
    $ratio,
    $bit, 
    $this_bit,
    $pix_sum,
    $all_sum,
    $rad_sum,
    $rad2, $radius2,
    $inten,
    $piece
    );

  # how many pieces do we sub-divide pixels into?
  $piece = 20;

  $fwhm = $_[0];
  $radius = $_[1];
  $pixsize = $_[2];

  # sanity check
  if ($pixsize <= 0.0) {
    printf "\nError: radius %lf must be greater than zero\n", $pixsize;
    return(0.0);
  }

  # rescale FWHM and aperture radius into pixels (instead of arcsec)
  $fwhm /= $pixsize;
  $radius /= $pixsize;

  $max_pix_rad = 30;

  # check to make sure user isn't exceeding our built-in limits
  if ($radius >= $max_pix_rad) {
    printf "\nWarning: radius exceeds limit of %d </b> \n", $max_pix_rad;
  }

  # these values control the placement of the star on the pixel grid:
  #    (0,0) to make the star centered on a junction of four pixels
  #    (0.5, 0.5) to make star centered on one pixel
  $psf_center_x = 0.5;
  $psf_center_y = 0.5;

  $sigma2 = $fwhm / 2.35;
  $sigma2 = $sigma2*$sigma2;
  $radius2 = $radius*$radius;
  $bit = 1.0/$piece;

  $rad_sum = 0.0;
  $all_sum = 0.0;

  for ($i = 0.0 - $max_pix_rad; $i < $max_pix_rad; $i++) {
    for ($j = 0.0 - $max_pix_rad; $j < $max_pix_rad; $j++) {
      

      # now, how much light falls into pixel (i, j)?
      $pix_sum = 0.0;
      for ($k = 0; $k < $piece; $k++) {

        $x = ($i - $psf_center_x) + ($k + 0.5)*$bit;
        $fx = exp(-($x*$x)/(2.0*$sigma2));

        for ($l = 0; $l < $piece; $l++) {
 
          $y = ($j - $psf_center_y) + ($l + 0.5)*$bit;
          $fy = exp(-($y*$y)/(2.0*$sigma2));
         
          $inten = $fx*$fy;
          $this_bit = $inten*$bit*$bit;
          $pix_sum += $this_bit;
        
          $rad2 = $x*$x + $y*$y;
          if ($rad2 <= $radius2) {
            $rad_sum += $this_bit;
          }
        }
      }
      $all_sum += $pix_sum;
    }
  }

  $ratio = $rad_sum / $all_sum;
  if (0) {
    printf " rad_sum %lf  all_sum %lf  -> ratio = %lf \n", 
              $rad_sum , $all_sum, $ratio;
  }

  return($ratio);

}
      

############################################################################
# PROCEDURE: mag_zeropoint
# 
# DESCRIPTION: Given a filter name, return the number of photons per
#              square centimeter per second which a star of zero'th 
#              magnitude would produce above the atmosphere.
#              We assume that the star has a spectrum like Vega's.
#              
#              The numbers are pre-calculated and we just pick the
#              appropriate one for the given filter.
#              
# RETURNS:     Number of photons per sq.cm. per sec from zero'th mag star.
# 
sub mag_zeropoint {

  my(
    $filter,
    $nphot
  );
   

  $filter = $_[0];
  $nphot = -1;

  if ($filter eq "none") { 
    $nphot = 4.32e+06;
  } 
  if ($filter eq "U") { 
    $nphot = 5.50e+05;
  } 
  if ($filter eq "B") { 
    $nphot = 3.91e+05;
  } 
  if ($filter eq "V") { 
    $nphot = 8.66e+05;
  } 
  if ($filter eq "R") { 
    $nphot = 1.10e+06;
  } 
  if ($filter eq "I") { 
    $nphot = 6.75e+05;
  } 

  if ($nphot == -1) {
    printf "Error: bad filter %s\n", $filter;
  }
  
  return($nphot);
}


############################################################################
# PROCEDURE: get_extinct_coeff
# 
# DESCRIPTION: Given a filter name, return an extinction coefficient.
#              The numbers are only approximate.
#              We use the V-band value if there's no filter.
#              
# RETURNS:     Extinction coefficient (mag/airmass)
# 
sub get_extinct_coeff {

  my(
    $filter,
    $coeff
  );
   

  $filter = $_[0];
  $coeff = -1;

  if ($filter eq "none") { 
    $coeff = 0.20;
  } 
  if ($filter eq "U") { 
    $coeff = 0.60;
  } 
  if ($filter eq "B") { 
    $coeff = 0.40;
  } 
  if ($filter eq "V") { 
    $coeff = 0.20;
  } 
  if ($filter eq "R") { 
    $coeff = 0.10;
  } 
  if ($filter eq "I") { 
    $coeff = 0.08;
  } 

  if ($coeff == -1) {
    printf "Error: bad filter %s\n", $filter;
  }
  
  return($coeff);
}



