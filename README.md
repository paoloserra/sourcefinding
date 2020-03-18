# sourcefinding
Various programs/tools for source finding and cleaning of Apertif HI cubes


### Step 1: sourcefinding.py
```
python sourcefinding.py -t <taskid> -b <beams> -c <cubes>
```
Default for beams is 0-39 (all).  
Default for cubes is 1,2,3 (nearest cubes where we expect direct detections).
Uses a parameter file called `parameter_template_4sig.par` or `parameter_template_10sig.par` when appropriate.
Does continuum filtering first, currently using the SoFiA-1 strategy (although this will change).  Then does source finding using SoFiA-2.
Tries to check if it should do an initial high threshold cleaning (10 sigma) or not.  This seems to work on the survey data that has been tested, but not on some hand picked SVC data. 
Parameters probably need to be tweaked.

Output:  
`HI_image_cube*_filtered_sof1.fits` - used in `checkmasks.py`  
`HI_image_cube*_4sig_cat.txt`  
`HI_image_cube*_4sig_cat.xml` - could probably get rid of this  
`HI_image_cube*_4sig_chan.fits`  
`HI_image_cube*_4sig_mask-2d.fits` - used in `checkmasks.py`  
`HI_image_cube*_4sig_mask.fits` - used in `clean.py`  
`HI_image_cube*_4sig_mom0.fits`  
`HI_image_cube*_4sig_mom1.fits`  
`HI_image_cube*_4sig_mom2.fits`  
`HI_image_cube*_4sig_rel.eps `  

### Step 2: checkmasks.py
```
python checkmasks.py -t <taskid> -b <beams>
```
Default for beams is 0-39 (all).  
Plots the mask from continuum filtering (in grey) and the 2D masks of the source finding (in color) for the nearest 3 cubes or ignores if they aren't present.
Plots the HI spectrum for all sources found in `sourcefinding.py`.

Output: `HI_imaging_4sig_summary.png` and `HI_imaging_4sig_summary_spec.png`.  
(`10sig` if sources were found in high threshold source finding round).

### Step 3: (only in the case of perfect masks) clean.py
```
python clean.py -t <taskid> -b <beams> -c <cubes>
```
Default for beams is 0-39 (all).  
Default for cubes is 1,2,3 (nearest cubes where we expect direct detections).  
Ignores beam/cube combinations which don't have a SoFiA mask generated by sourcefinding.py.  (If a catalog file is present, but not mask, program crashes out.  Means something went wrong with `sourcefinding.py`)
Cleans the HI emission based on input mask files.  Any source selection needs to be done by hand at the moment, before running this program.  Program just takes the output mask from SoFiA results and cleans with that to 0.5 sigma.

Output:  
`HI_image_cube*_clean.fits` cleaned cube  
`HI_image_cube*_model.fits` model cube  
`HI_image_cube*_residual.fits` residual cube  
And a bunch of Miriad files that aren't cleaned up at the moment.  

### To Do:
Create moment maps based on the existing SoFiA masks & cleaned cubes?
