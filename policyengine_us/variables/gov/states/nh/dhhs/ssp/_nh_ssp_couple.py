"""Couples that share one New Hampshire adult category assistance group."""

import numpy as np

from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


def nh_ssp_spouse(person, period):
    """Row of each person's co-resident spouse in a shared group, or -1.

    Spouses share a group only when both live independently; care categories
    are one-person groups (SPA NH-26-0001 Section E). The SSI spouse test
    keeps a default marital unit from pairing a parent with their child.
    """
    arrangement = person("nh_ssp_living_arrangement", period)
    independent = arrangement == arrangement.possible_values.INDEPENDENT
    spouse = _ssi_spouse_index(person, period)
    shared = independent & (spouse >= 0) & independent[np.maximum(spouse, 0)]
    return np.where(shared, spouse, -1)


def spouse_value(values, spouse, default=0):
    """Each person's spouse's value, or the default without a spouse."""
    return np.where(spouse >= 0, values[np.maximum(spouse, 0)], default)
