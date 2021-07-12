#!/usr/bin/env python3
'''
##############################################################
# Author:               John Vant
# Email:              jvant@asu.edu
# Affiliation:   ASU Biodesign Institute
# Date Created:          210710
##############################################################
# Usage:  python make_maps.py or ./scripts/make_maps.py
##############################################################
# Notes:  Run this in the git directory
##############################################################
'''
# Imports
import os
import numpy as np

def mymkdir(s):
    if not os.path.exists(s):
        os.makedirs(s)
    else:
        print("\nThe dir exists!!!\n%s\n" % s)


def bash(bashCommand):
    import subprocess
    print("\nBashCommand:\n%s\n" % (bashCommand))
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode("utf-8")
    if not error == None:
        error = error.decode("utf-8")
    print("StandardOutput:\n%s\nError:%s\n" % (output, error))
    return output, error


def write_output(bash_command, output_name):
    out, err = bash_command
    fout = open(output_name + ".out" ,"w")
    fout.write(out)
    fout.close()
    if not err == None:
        ferr = open(output_name + ".err" ,"w")
        ferr.write(err)
        ferr.close()


class System:
    '''
    Class for converting map coefficients files to potential files ready to use in MDFF.
    '''
    PHENIX_BIN = "/packages/phenix/1.14-3260/phenix-1.14-3260/build/bin"
    VMD_BIN = "/home/jvant/Documents/Programs/VMD/vmd-1.9.4a48/Local/bin"

    
    def __init__(self, pdbid, exp_method):
        if os.path.isfile(f"{self.VMD_BIN}/vmd") and os.path.isfile(f"{self.PHENIX_BIN}/phenix.maps"):
            self.pdbid_l = pdbid.lower()
            self.pdbid_u = pdbid.upper()
            self.exp_method = exp_method
            self.top_dir = os.getcwd()
            mymkdir("systems")
            system_dir = "%s/systems/%s" % (os.getcwd(), self.pdbid_l)
            mymkdir(system_dir)
            self.system_dir = system_dir
            self.download_files()
        else:
            print(f'''
            Could not find one of the following binaries:\n
            {self.VMD_BIN}/vmd
            {self.PHENIX_BIN}/phenix.maps
            System has not been initiated!!!
            ''')
            exit()


    def __str__(self):
        return f"\nPDBID: {self.pdbid_u}\nExperimental Method: {self.exp_method}"


    def download_files(self):
        os.chdir(self.system_dir)
        bash("wget https://files.rcsb.org/download/%s.pdb" % (self.pdbid_u))
        # bash("wget https://edmaps.rcsb.org/maps/%s_2fofc.dsn6" % (self.pdbid_l))
        bash("wget http://edmaps.rcsb.org/coefficients/%s.mtz" % (self.pdbid_l))
        os.chdir(self.top_dir)
        
        
    def convert_mtz_to_dx(self, resolution):
        '''Use Phenix and VMD binaries to convert map coefficients (.mtz) to voxel 
        format (.ccp4) and finally convert the .ccp4 map to a potential map (.dx)'''

        # Create resolution directory
        resolution = str(resolution)
        os.chdir(self.system_dir)
        mymkdir(resolution)
        os.chdir(resolution)

        # Phenix convert mtz to ccp4
        fout = open("maps.params", "w")        
        pdbfile = f"{self.system_dir}/{self.pdbid_u}.pdb"
        mtzfile = f"{self.system_dir}/{self.pdbid_l}.mtz"
        fout.write(map_params_script % (pdbfile, mtzfile, resolution))  # write params file
        fout.close()
        write_output(bash(f"{self.PHENIX_BIN}/phenix.maps maps.params"), "phenix_maps")

        # VMD convert ccp4 to dx
        fout = open("vmd_voltool_pot_convert.tcl", "w")
        dx_outfile_name = self.pdbid_u + "_Cryst_dimmer.dx"
        fout.write(vmd_voltool_pot_convert_script % (dx_outfile_name))  # write tcl file
        fout.close()
        write_output(bash(f"{self.VMD_BIN}/vmd -dispdev text -e vmd_voltool_pot_convert.tcl"), "vmd_voltool_pot_convert")
        
        os.chdir(self.top_dir)



map_params_script = f'''
maps {{
input {{
pdb_file_name = %s
reflection_data {{
file_name = %s
labels = None
high_resolution = %s
low_resolution = None
outliers_rejection = True
french_wilson_scale = True
french_wilson {{
max_bins = 60
min_bin_size = 40
}}
sigma_fobs_rejection_criterion = None
sigma_iobs_rejection_criterion = None
r_free_flags {{
file_name = None
label = None
test_flag_value = None
ignore_r_free_flags = False
}}
}}
}}
output {{
directory = None
prefix = phenix.maps
fmodel_data_file_format = mtz
include_r_free_flags = False
}}
scattering_table = wk1995 it1992 *n_gaussian neutron electon
wavelength = None
bulk_solvent_correction = True
anisotropic_scaling = True
skip_twin_detection = False
omit {{
method = *simple
selection = None
}}
map {{
map_type = 2mFo-DFc
format = xplor *ccp4
file_name = phenix.maps.ccp4
fill_missing_f_obs = False
grid_resolution_factor = 1/4.
region = *selection cell
atom_selection = None
atom_selection_buffer = 3
sharpening = False
sharpening_b_factor = None
exclude_free_r_reflections = False
isotropize = True
}}
}}
'''    

vmd_voltool_pot_convert_script = '''
# VMD Script
voltool pot -threshold 1 -i phenix.maps.ccp4 -o %s
exit
'''

systems = [["4zns", "xtal"]]
resolutions = ["None", "1", "3", "5", "7"]
if __name__ == "__main__":
    while not os.path.isdir(".git") or not os.path.isdir("scripts"):
        os.chdir("..")
        print("Not in the right directory\nNow in %s" % (os.getcwd()))
    print("Running script from %s" % (os.getcwd()))

    for sys in systems:
        PDB4ZNS = System(sys[0], sys[1])
        for res in resolutions:
            PDB4ZNS.convert_mtz_to_dx(res)


exit()
