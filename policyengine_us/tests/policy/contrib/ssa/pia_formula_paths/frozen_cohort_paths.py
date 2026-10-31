"""Dated cohort values for the price-indexing YAML files in this folder.

Frozen price-indexing inputs must have an observation dated January 1 of each
eligibility year (tools/social_security/parameters.py, `_frozen_value`). A
YAML inline override always spans 2000-2039 from 2000-01-01, so these reforms
supply the cohort-dated values. Every value is illustrative test data: none
makes a claim about any percentile, price index or maximum-taxable career.
"""

from policyengine_core.model_api import *
from policyengine_core.periods import instant


def _progressive_2035_maximum_path(parameters):
    progressive = parameters.gov.contrib.ssa.pia.progressive_price_indexing
    progressive.maximum_aime.update(start=instant("2035-01-01"), value=17_000)
    progressive.maximum_pia_target.update(start=instant("2035-01-01"), value=5_100)
    return parameters


def _full_price_indexing_scale_path(parameters):
    scale = parameters.gov.contrib.ssa.pia.full_price_indexing.real_wage_scale
    # The 2032 start cohort is the identity anchor; 2035 scales every factor.
    scale.update(start=instant("2032-01-01"), value=1)
    scale.update(start=instant("2035-01-01"), value=0.95)
    return parameters


class progressive_2035_maximum_path(Reform):
    def apply(self):
        self.modify_parameters(_progressive_2035_maximum_path)


class full_price_indexing_scale_path(Reform):
    def apply(self):
        self.modify_parameters(_full_price_indexing_scale_path)
