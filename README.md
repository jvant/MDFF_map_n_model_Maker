# MDFF_map_n_model_Maker
Contained in this repository is a method using Phenix and VMD to convert crystal structure map coefficients (.mtz) into potentials (.dx) amendable to use in NAMD's MDFF plugin.

## Running
Edit scripts/make_maps.py and edit the following python list to select your model.  Include the  PDBID and "xtal" (will include more functionality in the future) as shown below.

`systems = [["4zns", "xtal"], ["6qpr","xtal"]]`


Update the paths to your Phenix and VMD bins by changing the following static variables in scripts/make_maps.py

`PHENIX_BIN = "/packages/phenix/1.14-3260/phenix-1.14-3260/build/bin"`
`VMD_BIN = "/home/jvant/Documents/Programs/VMD/vmd-1.9.4a48/Local/bin"`

On the command line run the following from any directory in this git repository

`./make_maps.py`

Thats all for now!
