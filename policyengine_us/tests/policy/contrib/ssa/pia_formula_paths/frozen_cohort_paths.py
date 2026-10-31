"""Reforms for the price-indexing YAML files in this folder.

Frozen price-indexing inputs need an observation dated January 1 of each
eligibility year (tools/social_security/parameters.py, `_frozen_value`). A
YAML inline override always spans 2000-2039 from 2000-01-01, so it cannot
supply them. Core also applies a `reforms:` entry and inline overrides as two
separate reformed systems, so each reform here sets every parameter its file
needs and the file adds no inline override.

Every value is illustrative test data: none makes a claim about any
percentile, price index or maximum-taxable career. Bend points for cohorts
after 2026 are pinned to the model's 2035 projection ($1,756 / $10,588), as
the YAML comments state.
"""

from policyengine_core.model_api import *
from policyengine_core.periods import instant

START, STOP = instant("2000-01-01"), instant("2039-12-31")


def _pin_2035_bend_points(parameters):
    # Cohorts after 2026 read their bend points from the formula scale.
    scale = parameters.gov.ssa.social_security.pia.formula_factors
    scale.brackets[1].threshold.update(start=START, stop=STOP, value=1_756)
    scale.brackets[2].threshold.update(start=START, stop=STOP, value=10_588)
    parameters.gov.contrib.ssa.pia.in_effect.update(start=START, stop=STOP, value=True)


def _progressive_2035(fraction):
    def modify(parameters):
        _pin_2035_bend_points(parameters)
        progressive = parameters.gov.contrib.ssa.pia.progressive_price_indexing
        progressive.in_effect.update(start=START, stop=STOP, value=True)
        progressive.bend_point_fraction.update(start=START, stop=STOP, value=fraction)
        progressive.maximum_aime.update(start=instant("2035-01-01"), value=17_000)
        progressive.maximum_pia_target.update(start=instant("2035-01-01"), value=5_100)
        return parameters

    return modify


def _full_price_indexing(parameters):
    _pin_2035_bend_points(parameters)
    full = parameters.gov.contrib.ssa.pia.full_price_indexing
    full.in_effect.update(start=START, stop=STOP, value=True)
    # The 2032 start cohort is the identity anchor; 2035 scales every factor.
    full.real_wage_scale.update(start=instant("2032-01-01"), value=1)
    full.real_wage_scale.update(start=instant("2035-01-01"), value=0.95)
    return parameters


class progressive_2035_quarter_fraction(Reform):
    def apply(self):
        self.modify_parameters(_progressive_2035(0.25))


class progressive_2035_half_fraction(Reform):
    def apply(self):
        self.modify_parameters(_progressive_2035(0.5))


class full_price_indexing_2035(Reform):
    def apply(self):
        self.modify_parameters(_full_price_indexing)
