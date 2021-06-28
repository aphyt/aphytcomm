__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"


def wavelength_to_rgb(wavelength):
    r = 0.0
    g = 0.0
    b = 0.0
    wavelength = float(wavelength)
    if (wavelength >= 380.0) & (wavelength < 440.0):
        r = -1.0*(wavelength-440.0)/(440.0-380.0)
        g = 0.0
        b = 1.0
    elif (wavelength >= 440.0) & (wavelength < 490.0):
        r = 0.0
        g = (wavelength-440.0)/(490.0-440.0)
        b = 1.0
    elif (wavelength >= 490.0) & (wavelength < 510.0):
        r = 0.0
        g = 1.0
        b = (-1.0*(wavelength-510.0))/(510.0-490.0)
    elif (wavelength >= 510.0) & (wavelength < 580.0):
        r = (wavelength-510.0)/(580.0-510)
        g = 1.0
        b = 0.0
    elif (wavelength >= 580.0) & (wavelength < 645.0):
        r = 1.0
        g = (-1.0*(wavelength-645.0))/(645.0-580.0)
        b = 0.0
    elif (wavelength >= 645.0) & (wavelength < 780.0):
        r = 1.0
        g = 0.0
        b = 0.0
    return round(r * 255.0), round(g * 255.0), round(b * 255.0)


def wavelength_to_rgb2(wavelength):
    r = 0.0
    g = 0.0
    b = 0.0
    wavelength = float(wavelength)
    if (wavelength >= 400.0) & (wavelength < 410.0):
        t = (wavelength - 400.0) / (410.0 - 400.0)
        r = r + (0.33 * t) - (0.20 * t * t)
    elif (wavelength >= 410.0) & (wavelength < 475.0):
        t = (wavelength - 410.0) / (475.0 - 410.0)
        r = 0.14 - (0.13 * t * t)
    elif (wavelength >= 545.0) & (wavelength < 595.0):
        t = (wavelength - 545.0) / (595.0 - 545.0)
        r = r + (1.98 * t) - (t * t)
    elif (wavelength >= 595.0) & (wavelength < 650.0):
        t = (wavelength - 595.0) / (650.0 - 595.0)
        r = 0.98 + (0.06 * t) - (0.40 * t * t)
    elif (wavelength >= 650.0) & (wavelength < 700.0):
        t = (wavelength - 650.0) / (700.0 - 650.0)
        r = 0.65 - (0.84 * t) + (0.20 * t * t)
    if (wavelength >= 415.0) & (wavelength < 475.0):
        t = (wavelength - 415.0) / (475.0 - 415.0)
        g = g + (0.80 * t * t)
    elif (wavelength >= 475.0) & (wavelength < 590.0):
        t = (wavelength - 475.0) / (590.0 - 475.0)
        g = 0.8 + (0.76 * t) - (0.80 * t * t)
    elif (wavelength >= 585.0) & (wavelength < 639.0):
        t = (wavelength - 585.0) / (639.0 - 585.0)
        g = 0.84 - (0.84 * t)
    if (wavelength >= 400.0) & (wavelength < 475.0):
        t = (wavelength - 400.0) / (475.0 - 400.0)
        b = b + (2.20 * t) - (1.50 * t * t)
    elif (wavelength >= 475.0) & (wavelength < 560.0):
        t = (wavelength - 475.0) / (560.0 - 475.0)
        b = 0.7 - t + (0.30 * t * t)
    return round(r * 256.0), round(g * 256.0), round(b * 256.0)
