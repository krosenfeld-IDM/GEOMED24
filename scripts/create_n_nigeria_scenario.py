"""
Take Nigeria data and create a scenario for N. Nigeria
For data structure see
https://github.com/krosenfeld-IDM/laser-technology-comparison/blob/main/EnglandAndWales/data/csvstopy.py
TODO: add MCV1 and birth rate per place
"""

import os
from pathlib import Path
import sciris as sc
import numpy as np
# from refdat_location_admin02 import data_dict
from nigeria import lgas # dict in form of ()
# "LOCATION": ((SIZE, YEAR), (X_VAL, Y_VAL), AREA)
import matplotlib.pyplot as plt

def calc_distance(lat1, lon1, lat2, lon2):
    # convert to radians
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    # haversine formula (https://en.wikipedia.org/wiki/Haversine_formula)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    d = RE * c
    return d

if __name__ == "__main__":

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    RE = 6371.0 # Earth radius in km

    # initialize final data structure
    data = sc.dictobj()
    data.placenames = []
    data.places = {}

    cnt = 0
    lat = []
    lon = []
    id = []
    # loop through the subnational components in the lgas dict 
    # (includes nationa, state, and lga)
    lga_id = 0
    for k,v in lgas.items():
        subnational_id = k.split(':')
        if len(subnational_id) == 5: # e.g., k = 'AFRO:NIGERIA:SOUTH_WEST:OYO:SURULERE'
            lga_id += 1
            if subnational_id[2].startswith('NORTH'):
                data.placenames.append(k)
                data.places[k] = sc.dictobj({'population': v[0][0], 'latitude': v[1][1], 'longitude': v[1][0]})
                lon.append(v[1][0])
                lat.append(v[1][1])
                id.append(lga_id)
                cnt += 1
    print(f"Total number of LGAs: {cnt}")

    # calculate distance matrix
    distances = np.zeros((cnt,cnt))
    for i in range(cnt):
        for j in range(i):
            d = calc_distance(lat[i], lon[i], lat[j], lon[j])
            distances[i,j] = d
            distances[j,i] = d

    # save scenario
    np.save(Path(ROOT_DIR).parent / "scenarios" / "nnigeria_distances.npy", distances)
    sc.saveobj(Path(ROOT_DIR).parent / "scenarios" / "nnigeria_data.obj", data)

    plt.figure()
    plt.plot(lon,lat,'.')
    plt.savefig(Path(ROOT_DIR).parent / "figures" / "nigeria_lga_lat_lon.png")


    plt.figure()
    plt.plot(distances[np.triu_indices(cnt)],'.')
    plt.savefig(Path(ROOT_DIR).parent / "figures" / "nigeria_lga_distances.png")
    print("done")