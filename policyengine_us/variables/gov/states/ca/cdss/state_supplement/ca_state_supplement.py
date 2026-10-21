from policyengine_us.model_api import *


class ca_state_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "California state supplement"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
        "https://www.law.cornell.edu/cfr/text/20/416.1160",
    )

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ca_state_supplement_payment_standard", period)
        ssi = add(spm_unit, period, ["ssi"])
        person = spm_unit.members
        # CAPI budgets its own members' income (CAPI regulations MPP 49-035),
        # and SSI/SSP counts another member's income only when it is deemed
        # (20 CFR 416.1160(a)), so a CAPI-eligible member's income does not
        # reduce the state supplement.
        capi_eligible = person("ca_capi_eligible_person", period.this_year)
        person_countable_income = person("ssi_countable_income", period)
        countable_income = spm_unit.sum(
            where(capi_eligible, 0, person_countable_income)
        )
        return max_(0, payment_standard - ssi - countable_income)
