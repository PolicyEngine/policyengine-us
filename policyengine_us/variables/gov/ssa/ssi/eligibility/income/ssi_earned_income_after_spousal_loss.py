from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_earned_income_after_spousal_loss(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income after self-employment losses of either spouse"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1111.htm",
        "https://secure.ssa.gov/poms.nsf/lnx/0500820210",
    )
    documentation = (
        "SSI budget earned income after applying own business losses to own "
        "earnings, then any excess business loss of a co-resident spouse. "
        "Residual losses do not reduce unearned income. The signed individual "
        "earnings remain available in ssi_earned_income for other programs."
    )

    def formula(person, period, parameters):
        earned = person("ssi_earned_income", period)
        if not np.any(earned < 0):
            return earned
        spouse = _ssi_spouse_index(person, period)
        spouse_earned = where(spouse >= 0, earned[np.maximum(spouse, 0)], 0)
        # POMS SI 00820.210 B.2.c applies losses to own earnings first,
        # then to the spouse's earnings, including an ineligible spouse.
        # Each positive earner absorbs only the other spouse's excess loss;
        # the loss-maker's zero balance prevents double netting when pooled.
        return max_(earned + min_(spouse_earned, 0), 0)
