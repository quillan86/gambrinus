from typing import Optional, Any
import numpy as np


class FlavorAlgorithmService:
    sucrose_mw = 342.3
    ethanol_mw = 46.08
    ethanol_density = 0.789

    @classmethod
    def ethanol_concentration(cls, abv: float) -> float:
        # 1.4% = taste threshold
        result = abv * cls.ethanol_density / (1 - abv) * 1000 * 1000 / cls.ethanol_mw # in mM
        return result

    @classmethod
    def sugar_concentration(cls, sg: float) -> float:
        brix = (143.254 * sg**3 - 648.670 * sg**2 + 1125.805 * sg - 620.389)
        result = brix * sg * 10 * 1000 / cls.sucrose_mw # mg/L
        return result

    @classmethod
    def hill_equation(cls, concentration: float, threshold: float) -> float:
        """
        Assume one element for now.
        :param concentration:
        :param threshold:
        :return:
        """
        n = 1.0
        half_concentration = np.exp(2.0) * threshold

        intensity = 100.0/(1.0 + 1.0/((concentration/half_concentration)**n))
        return intensity

    @classmethod
    def run(cls, graph: dict):
        if len(graph.get('recipes', [])) == 0:
            return {
                'Name of Beer': "",
                'Unnormalized Flavor Profile': {},
                'Normalized Flavor Profile': {}
            }
        recipe = graph['recipes'][0]
#        og: float = recipe.get('og', 1.0) # specific gravity
        fg: float = recipe.get('fg', 1.0) # specific gravity
        ibu: float = recipe.get('ibu', 0.0) # in mM
        abv: float = recipe.get('abv', 0.0) # unitless L/L
        name = recipe.get('name', 'Beer')

        # calculate levels
        maltose_concentration = cls.sugar_concentration(fg) # in mM
        ethanol_concentration = cls.ethanol_concentration(abv) # in mM
        isohumulone_concentration = ibu # in mM

        # extract thresholds
        flavor_edges = graph['r7_edges']
        flavor_molecules = [edge['start']['name'] for edge in flavor_edges]

        # get indices
        isohumulone_idx = flavor_molecules.index('Isohumulone')
        maltose_idx = flavor_molecules.index('Maltose')
        ethanol_idx = flavor_molecules.index('Ethanol')

        # get thesholds
        isohumulone_threshold = flavor_edges[isohumulone_idx]['properties']['threshold']
        maltose_threshold = flavor_edges[maltose_idx]['properties']['threshold']
        ethanol_threshold = flavor_edges[ethanol_idx]['properties']['threshold']

        bitter_intensity: float = cls.hill_equation(isohumulone_concentration, isohumulone_threshold)
        sweet_intensity: float = cls.hill_equation(maltose_concentration, maltose_threshold)
        alcohol_intensity: float = cls.hill_equation(ethanol_concentration, ethanol_threshold)

        taste_normalization = bitter_intensity + sweet_intensity
        odor_normalization = alcohol_intensity
        texture_normalization = alcohol_intensity

        flavor_profile_unnormalized = {
            "taste": {
                'bitter': round(bitter_intensity, 2),
                'sweet': round(sweet_intensity, 2),
            },
            "odor": {
                "alcoholic": round(alcohol_intensity, 2)
            },
            "texture": {
                'warming': round(alcohol_intensity, 2)
            }
        }

        flavor_profile_normalized = {
            "taste": {
                'bitter': round(bitter_intensity / taste_normalization * 100, 2),
                'sweet': round(sweet_intensity / taste_normalization * 100, 2),
            },
            "odor": {
                "alcoholic": round(alcohol_intensity / odor_normalization * 100, 2)
            },
            "texture": {
                'warming': round(alcohol_intensity / texture_normalization * 100, 2)
            }
        }

        flavor_profile = {
            'Name of Beer': name,
            'Unnormalized Flavor Profile': flavor_profile_unnormalized,
            'Normalized Flavor Profile': flavor_profile_normalized
        }

        return flavor_profile

