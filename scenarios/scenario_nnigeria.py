"""Load initial population, demographics, and network data for the Engwal scenario."""

from collections import namedtuple
from pathlib import Path
from typing import Tuple

import numpy as np
import sciris as sc

from idmlaser.numpynumba import DemographicsByYear

Node = namedtuple("Node", ["name", "index", "population", "counts", "births", "immigrations", "deaths"])


def initialize_nnigeria(model, parameters, num_nodes: int = 0) -> Tuple[int, DemographicsByYear, np.ndarray, np.ndarray]:
    """Initialize the model with the Northern Nigeria scenario."""

    data = sc.load(Path(__file__).parent / "nnigeria_data.obj")

    # get distances between nodes
    distances = np.load(Path(__file__).parent / "nnigeria_distances.npy")

    nodes = [
        Node(
            k,
            index,
            v.population,
            {"I": 0 if v.population < 100_000 else 10},
            np.zeros(parameters.ticks, dtype=np.uint32),
            np.zeros(parameters.ticks, dtype=np.uint32),
            np.zeros(parameters.ticks, dtype=np.uint32),
        )
        for index, (k, v) in enumerate(data.places.items())
    ]
    if num_nodes > 0:
        nodes.sort(key=lambda x: x.population, reverse=True)
        nodes = nodes[:num_nodes]

    nyears = parameters.ticks // 365
    nnodes = len(nodes)
    demographics = DemographicsByYear(nyears, nnodes)
    populations = np.zeros(nnodes, dtype=np.int32)  # initial population (year 0)
    for i, node in enumerate(nodes):
        populations[i] = node.population
    # https://database.earth/population/nigeria/fertility-rate
    demographics.initialize(initial_population=populations, cbr=35.0, mortality=17.0, immigration=0.0)

    # Setup initial conditions (distribution of agents to S, E, I, and R)
    initial = np.zeros((nnodes, 4), dtype=np.uint32)  # 4 columns: S, E, I, R

    for i, node in enumerate(nodes):
        initial[i, 0] = np.uint32(np.round(node.population / parameters.r_naught))
        # initial[i, 1] = 0
        initial[i, 2] = 0 if node.population < 100_000 else 10
        initial[i, 3] = node.population - initial[i, 0:3].sum()

    indices = np.array([node.index for node in nodes], dtype=np.uint32)
    network = distances[indices][:, indices]
    network *= 1000  # convert to meters

    # gravity model: k * pop_1^a * pop_2^b / (N * dist^c)
    a = parameters.a
    b = parameters.b
    c = parameters.c
    k = parameters.k
    totalpop = sum(node.population for node in nodes)
    for i in range(len(nodes)):
        popi = nodes[i].population
        for j in range(i + 1, len(nodes)):
            popj = nodes[j].population
            network[i, j] = network[j, i] = k * (popi**a) * (popj**b) / (network[i, j] ** c)
    network /= totalpop

    outflows = network.sum(axis=0)
    max_frac = parameters.max_frac
    if (maximum := outflows.max()) > max_frac:
        print(f"Rescaling network by {max_frac / maximum}")
        network *= max_frac / maximum

    max_capacity = demographics.population[0, :].sum() + demographics.births.sum() + demographics.immigrations.sum()
    print(f"Initial population: {demographics.population[0, :].sum():>11,}")
    print(f"Total births:       {demographics.births.sum():>11,}")
    print(f"Total immigrations: {demographics.immigrations.sum():>11,}")
    print(f"Max capacity:       {max_capacity:>11,}")

    return (max_capacity, demographics, initial, network)