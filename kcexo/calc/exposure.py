
import numpy as np

filter_extinction = {
    'U': 0.6,
    'B': 0.4,
    'V': 0.2,
    'R': 0.1,
    'I': 0.08
}

filter_mag_zeropoint = {
    'U': 5.50e+05,
    'B': 3.91e+05,
    'V': 8.66e+05,
    'R': 1.10e+06,
    'I': 6.75e+05
}

def calc_exposure(filter: str,
                  mag_start: float,
                  mag_end: float,
                  dmag: float,
                  tel_diam: float,
                  qe: float,
                  readnoise: float,
                  pixsize: float,
                  skymag: float,
                  airmass: float,
                  exptime: float,
                  fwhm: float,
                  aper_rad: float):
    if mag_start > mag_end or dmag <= 0.0:
        raise ValueError("invalid magnitude start/end or delta values")
    if tel_diam <= 0.0:
        raise ValueError("invalid telescope diameter, must be greater than 0")
    if qe <= 0.0 or qe > 1.0:
        raise ValueError("invalid QE, must be between 0.0 and 1.0")
    if pixsize <= 0.0:
        raise ValueError("invalid pixel size, must be greater than 0")
    if readnoise <= 0.0:
        raise ValueError("invainvalid readnoise, must be >= 0")
    if skymag < 0.0 or skymag > 100.0:
        raise ValueError("invalid skymag, must be between 0.0 and 100.0 (whatever 100 would be...)")
    if exptime <= 0.0:
        raise ValueError("invalid exposure time, must be greater than 0")
    if aper_rad <= 0.0:
        raise ValueError("id aperture radius, must be greater than 0")
    
    extinct_coeff: float = filter_extinction.get(filter, 0.2)
    nphoton: float = filter_mag_zeropoint.get(filter, 4.32e+06)
    
     # how many pixels are inside the aperture?
    npix = (np.pi * aper_rad * aper_rad) / (pixsize * pixsize)
    
    # what fraction of star's light falls within aperture?
    fraction = fraction_inside(fwhm, aper_rad, pixsize)
    
    res = []
    for mag in np.linarrangespace(mag_start, mag_end, dmag):
        
        # calculate # of electrons collected on the CCD from star, total
        x = (10.0**(-0.4*mag)) * nphoton
        x *= exptime
        x *= np.pi * tel_diam * tel_diam * 0.25
        x *= qe
        star_electrons = x
        
        # decrease the # of electrons from star, due to extinction 
        x = airmass * extinct_coeff
        star_electrons *= 10**(-0.4*x)
        
        # now calculate # of electrons collected on CCD from sky, per pixel
        x = (10.0**(-0.4 * skymag)) * nphoton
        x *= exptime
        x *= np.pi * tel_diam * tel_diam * 0.25
        x *= qe
        x *= pixsize * pixsize
        sky_electrons_per_pix = x
        
        # this is the total number of electrons from star inside aperture
        star_electrons *= fraction

        # this is the total number of electrons from sky inside aperture
        sky_electrons = sky_electrons_per_pix * npix

        # this is the total number of electrons from readout in aperture 
        read_electrons = readnoise * readnoise * npix
        
        # now we can calculate signal-to-noise
        signal = star_electrons
        noise = np.sqrt(read_electrons + sky_electrons + star_electrons)
        signal_to_noise = signal / noise
        
        res.append((mag, star_electrons, sky_electrons, read_electrons, signal_to_noise))
    
    return res


def fraction_inside(fwhm, radius, pixsize) -> float:
    
    # how many pieces do we sub-divide pixels into?
    piece = 20

    # sanity check
    if pixsize <= 0.0:
        raise ValueError("radius must be greater than zero")
    
    # rescale FWHM and aperture radius into pixels (instead of arcsec)
    fwhm /= pixsize
    radius /= pixsize

    max_pix_rad = 30

    # check to make sure user isn't exceeding our built-in limits
    if radius >= max_pix_rad:
        print(f"Warning: radius exceeds limit of {max_pix_rad}")
    

    # these values control the placement of the star on the pixel grid:
    #    (0,0) to make the star centered on a junction of four pixels
    #    (0.5, 0.5) to make star centered on one pixel
    psf_center_x = 0.5;
    psf_center_y = 0.5;

    sigma2 = fwhm / 2.35
    sigma2 = sigma2 * sigma2
    radius2 = radius * radius
    bit = 1.0 / piece

    rad_sum = 0.0
    all_sum = 0.0

    for i in np.arrange(0.0-max_pix_rad, max_pix_rad, 1.0): 
        for j in np.arrange(0.0-max_pix_rad, max_pix_rad, 1.0):
            # now, how much light falls into pixel (i, j)?
            pix_sum = 0.0
            for k in range(piece):
                x = (i - psf_center_x) + (k + 0.5) * bit
                fx = np.exp(-(x * x) / (2.0 * sigma2))

                for l in range(piece):
                    y = (j - psf_center_y) + (l + 0.5) * bit
                    fy = np.exp(-(y * y) / (2.0 * sigma2))
                    
                    inten = fx * fy
                    this_bit =  inten * bit * bit
                    pix_sum += this_bit
                    
                    rad2 = x * x +  y * y
                    if rad2 <= radius2:
                        rad_sum += this_bit

            all_sum += pix_sum

    ratio = rad_sum / all_sum
    return ratio
