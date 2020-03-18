from glob import glob
import os

from astropy.io import ascii
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
# %matplotlib


def chan2freq(channels=None):
    frequencies = (channels * hdu_filter[0].header['CDELT3'] + hdu_filter[0].header['CRVAL3']) * u.Hz
    return frequencies


taskid = '190915041'
beams = range(40)
cubes = [1, 2, 3]

HI_restfreq = 1420405751.77 * u.Hz
optical_HI = u.doppler_optical(HI_restfreq)

cube_name = 'HI_image_cube'
colors = ['purple', 'blue', 'black']
plt.close('all')
for b in beams:
    loc = '/tank/hess/apertif/' + taskid + '/B0' + str(b).zfill(2) + '/'
    source_per_beam = 0
    results = glob(loc + '*4sig_mask-2d.fits')

    if len(results) > 0:
        header = fits.getheader(results[0])
        wcs = WCS(header)
        fig_im, ax_im = plt.subplots(1, 3, figsize=(15, 5), subplot_kw={'projection': wcs})

        for c in cubes:
            if os.path.isfile(loc + cube_name + '{}_4sig_cat.txt'.format(c)):
                cat = ascii.read(loc + cube_name + '{}_4sig_cat.txt'.format(c))
                source_per_beam += len(cat)
        fig_spec, ax_spec = plt.subplots(source_per_beam, 1, figsize=(15, 3*source_per_beam), squeeze=False)

        previous = 0
        for c in cubes:
            hdu_filter = fits.open(loc + cube_name + '{}_filtered_sof1.fits'.format(c))
            filter2d = hdu_filter[0].data[0, :, :]
            filter2d[np.isnan(filter2d)] = 9.
            filter2d[filter2d < 9] = np.nan

            if os.path.isfile(loc + cube_name + '{}_4sig_cat.txt'.format(c)):
                cat = ascii.read(loc + cube_name + '{}_4sig_cat.txt'.format(c))
                print("Found {} sources in Beam {:02} Cube {}".format(len(cat), b, c))
                hdu_mask = fits.open(loc + cube_name + '{}_4sig_mask-2d.fits'.format(c))
                mask2d = hdu_mask[0].data[:, :]

                mask2d=np.asfarray(mask2d)
                mask2d[mask2d<1] = np.nan

                cube_frequencies = chan2freq(np.array(range(hdu_filter[0].data.shape[0])))
                optical_velocity = cube_frequencies.to(u.km/u.s, equivalencies=optical_HI)

                ax_im[c-1].imshow(filter2d, cmap='Greys_r', vmax=10, vmin=8)
                ax_im[c-1].imshow(mask2d, cmap='gist_rainbow')
                ax_im[c-1].set_title("Cube {}".format(c))
                for s in range(len(cat)):
                    ax_im[c-1].text(cat['col3'][s] + np.random.uniform(-40, 40), cat['col4'][s] + np.random.uniform(-40, 40),
                             cat['col2'][s], color='black')
                    # print(cat['col2'][s], wcs.pixel_to_world(cat['col3'][s], cat['col4'][s]).to_string('hmsdms'))
                    spectrum = np.sum(hdu_filter[0].data[:,mask2d==cat['col2'][s]],axis=1)
                    maskmin = chan2freq(cat['col10'][s]).to(u.km/u.s, equivalencies=optical_HI).value
                    maskmax = chan2freq(cat['col11'][s]).to(u.km/u.s, equivalencies=optical_HI).value
                    ax_spec[previous + s, 0].plot([optical_velocity[-1].value,optical_velocity[0].value], [0, 0], '--', color='gray')
                    ax_spec[previous + s, 0].plot(optical_velocity, spectrum, c=colors[c-1])
                    ax_spec[previous + s, 0].plot([maskmin, maskmin], [np.nanmin(spectrum), np.nanmax(spectrum)], ':', color='gray')
                    ax_spec[previous + s, 0].plot([maskmax, maskmax], [np.nanmin(spectrum), np.nanmax(spectrum)], ':', color='gray')
                    ax_spec[previous + s, 0].set_title("Beam {:02}, Cube {}, Source {}".format(b, c, cat['col2'][s]))
                    ax_spec[previous + s, 0].set_xlim(optical_velocity[-1].value,optical_velocity[0].value)
                    ax_spec[previous + s, 0].set_ylabel("Integrated Flux")
                    if (previous + s == source_per_beam - 1): ax_spec[previous + s, 0].set_xlabel("Optical Velocity [km/s]")
                previous += len(cat)

                hdu_mask.close()

            else:
                print("NO sources in Beam {:02} Cube {}".format(b, c))
                ax_im[c - 1].imshow(filter2d, cmap='Greys_r', vmax=10, vmin=8)
                ax_im[c - 1].set_title("Cube {}".format(c))
                ax_im[c - 1].axis('off')

            hdu_filter.close()

        fig_im.savefig(loc + 'HI_image_4sig_summary.png', bbox_inches='tight')
        fig_spec.savefig(loc + 'HI_image_4sig_summary_spec.png', bbox_inches='tight')
        plt.close(fig_im)
        plt.close(fig_spec)
    else:
        print("NO sources found in any cube for Beam {:02}".format(b))
