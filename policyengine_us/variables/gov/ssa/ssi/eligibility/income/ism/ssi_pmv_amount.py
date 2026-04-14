from policyengine_us.model_api import *


class ssi_pmv_amount(Variable):
    value_type = float
    entity = Person
    label = "SSI presumed maximum value amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
        "https://secure.ssa.gov/poms.nsf/lnx/0500835300",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320150",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi
        is_joint = person("ssi_claim_is_joint", period)
        deeming_applies = person("is_ssi_spousal_deeming_applies", period)

        # Per POMS SI 00835.300 and SI 00835.901:
        #   Individual / joint couple: PMV = 1/3 × FBR + $20
        #   Joint couple PMV is unit-level; the /2 in ssi_countable_income
        #   splits it per-person.
        #
        # Per POMS SI 01320.150: when spousal deeming applies, the PMV
        # is halved to 1/6 × couple FBR + $10, because the deeming path
        # in ssi_countable_income does NOT do a /2 split.
        applicable_fbr = where(
            is_joint | deeming_applies,
            p.amount.couple,
            p.amount.individual,
        )
        pmv_monthly = (
            applicable_fbr * p.income.ism.pmv_fbr_fraction + p.income.exclusions.general
        )
        pmv_monthly = where(deeming_applies, pmv_monthly / 2, pmv_monthly)
        return pmv_monthly * MONTHS_IN_YEAR
