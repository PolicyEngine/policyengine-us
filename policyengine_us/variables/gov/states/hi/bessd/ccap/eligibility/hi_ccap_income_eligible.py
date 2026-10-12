from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class hi_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=15"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.income
        countable_income = spm_unit("hi_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        # Monthly gross income must not exceed 85% of the State Median
        # Income for a family of the same size (HAR 17-798.2-9(b)(1)).
        annual_smi = smi(size, state, period.this_year, parameters)
        monthly_limit = annual_smi * p.smi_rate / MONTHS_IN_YEAR
        income_eligible = countable_income <= monthly_limit
        # The income test is waived for family units receiving child
        # protective services (HAR 17-798.2-9(b)(1)(B)). The foster-parent
        # waiver under (b)(1)(A) is not modeled because no licensed
        # foster-parent input exists at the moment.
        has_protective_services = (
            add(spm_unit, period, ["receives_or_needs_protective_services"]) > 0
        )
        return income_eligible | has_protective_services
