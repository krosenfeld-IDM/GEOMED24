"""
From https://github.com/krosenfeld-IDM/202407_laser/blob/main/cl_comps/run_simulation.py
"""

from pathlib import Path
import numpy as np
import os
import sys

from idmlaser.utils import PropertySet

if __name__ == "__main__":

    meta_params = PropertySet()
    meta_params.ticks = 365 * 1
    meta_params.nodes = 0
    meta_params.seed = 20240612
    meta_params.output = Path.cwd() / "outputs"

    model_params = PropertySet()
    model_params.exp_mean = np.float32(7.0)
    model_params.exp_std = np.float32(1.0)
    model_params.inf_mean = np.float32(7.0)
    model_params.inf_std = np.float32(1.0)
    model_params.r_naught = np.float32(14.0)
    model_params.seasonality_factor = np.float32(0.1)
    model_params.seasonality_offset = np.int32(182.5)

    model_params.beta = model_params.r_naught / model_params.inf_mean

    # Northern Nigeria Scenario
    meta_params.scenario = "northern_nigera"

    # network parameters (we derive connectivity from these and distance)
    net_params = PropertySet()
    net_params.a = np.float32(1.0)   # pop1 power
    net_params.b = np.float32(1.0)   # pop2 power
    net_params.c = np.float32(2.0)   # distance power
    net_params.k = np.float32(500.0) # scaling factor
    net_params.max_frac = np.float32(0.05) # max fraction of population that can migrate

    from scenario_nnigeria import initialize_nnigeria  # noqa: E402, I001
    params = PropertySet(meta_params, model_params, net_params)
    max_capacity, demographics, initial, network = initialize_nnigeria(None, params, params.nodes)    # doesn't need a model, yet

    from datetime import datetime

    params.prng_seed = datetime.now(tz=None).microsecond  # noqa: DTZ005

    # CPU based implementation
    from idmlaser.models.numpynumba import NumbaSpatialSEIR  # noqa: I001, E402, RUF100
    model = NumbaSpatialSEIR(params)

    # GPU based implementation with Taichi
    # from idmlaser.models import TaichiSpatialSEIR  # noqa: I001, E402, RUF100
    # model = TaichiSpatialSEIR(params)

    model.initialize(max_capacity, demographics, initial, network)

    model.run(params.ticks)

    metrics = model.metrics
    columns = metrics.columns[1:]
    cumulative = 0
    for column in columns:
        total = metrics[column].sum()
        print(f"{column:20}: {total:11,} μs")
        cumulative += total
    print("====================================")
    print(f"total               : {cumulative:11,} μs")

    # paramfile, npyfile = model.finalize()