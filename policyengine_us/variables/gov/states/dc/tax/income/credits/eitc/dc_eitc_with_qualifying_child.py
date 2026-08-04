from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_like_amount,
)


class dc_eitc_with_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC with qualifying children"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04",  # (f)
        # IRC 152(c)(3)(B) waives the qualifying-child age test for permanently and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # D.C. Law 23-149 extends the EITC to ITIN filers and ITIN qualifying
        # children, overriding the federal IRC section 32 SSN-only rule.
        person = tax_unit.members
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # IRC 152(c)(3)(B) waives the age test for a permanently and totally
        # disabled dependent, matching the federal eitc_child_count.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        qualifying_child = (
            person("is_qualifying_child_dependent", period) | is_disabled_dependent
        ) & has_tin
        child_count = tax_unit.sum(qualifying_child)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        federal_like_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count,
            child_count > 0,
            filer_has_tin,
        )
        p = parameters(period).gov.states.dc.tax.income.credits
        return federal_like_eitc * p.eitc.with_children.match
