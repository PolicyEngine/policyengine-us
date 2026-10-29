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
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=25",
    )

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ca_state_supplement_payment_standard", period)
        ssi = add(spm_unit, period, ["ssi"])
        person = spm_unit.members
        # SSI/SSP counts another member's income only when it is deemed
        # (20 CFR 416.1160(a)), and CAPI budgets its own members' income (CAPI
        # regulations MPP 49-035). So the countable income of a member who
        # fails SSI's citizen or qualified-noncitizen test, whether or not
        # CAPI-eligible, is not added, unless that member is in an SSI couple
        # computation: it splits the couple's income between the spouses, so
        # both halves count against the couple's SSI/SSP.
        # NOTE: SSI couple status ignores SSI's noncitizen test (issue 10481).
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        meets_ssi_immigration_test = is_citizen | is_qualified_noncitizen
        in_couple_computation = person("ssi_couple_computation_applies", period)
        counted = meets_ssi_immigration_test | in_couple_computation
        person_countable_income = person("ssi_countable_income", period)
        countable_income = spm_unit.sum(where(counted, person_countable_income, 0))
        return max_(0, payment_standard - ssi - countable_income)
