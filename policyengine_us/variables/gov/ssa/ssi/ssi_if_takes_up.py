from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ssi_if_takes_up(Variable):
    value_type = float
    entity = Person
    label = "SSI if takes up"
    documentation = (
        "Supplemental Security Income the person would receive if they "
        "take up the program, regardless of reported take-up."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1382",
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(e)(2)",
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(f)(5)",
    )

    def formula(person, period, parameters):
        if parameters(period).gov.ssa.ssi.abolish_ssi:
            return 0

        # Apply floor: SSI cannot be negative
        benefit = max_(0, person("uncapped_ssi", period))

        # 20 CFR 416.1163(e)(2): 'Your SSI benefit under the deeming rules
        # cannot be higher than it would be if deeming did not apply.
        # Therefore, your benefit is the lesser of the amount computed under
        # the rules in paragraph (d)(2) of this section or the amount
        # remaining after we subtract only your own countable income from an
        # individual's Federal benefit rate.'
        without_deeming = max_(
            0, person("uncapped_ssi_without_spousal_deeming", period)
        )
        deemed_benefit = min_(benefit, without_deeming)
        # 416.1163(f)(5): while the $30 Federal benefit rate applies, we do
        # not deem an ineligible spouse's income, so only the person's own
        # countable income counts.
        arrangement = person("ssi_federal_living_arrangement", period)
        in_medical_facility = (
            arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        deemed_benefit = where(in_medical_facility, without_deeming, deemed_benefit)

        deeming_applies = person("is_ssi_spousal_deeming_applies", period.this_year)
        return where(deeming_applies, deemed_benefit, benefit)
