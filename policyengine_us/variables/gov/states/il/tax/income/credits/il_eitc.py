from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_like_amount,
)


class il_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www2.illinois.gov/rev/programs/EIC/Pages/default.aspx",
        # 35 ILCS 5/212 bases the IL EIC on the federal IRC 32 credit.
        "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K212",
        # IRC 152(c)(3)(B) waives the qualifying-child age test for permanently and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
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
        p = parameters(period).gov.states.il.tax.income.credits.eitc
        demographic_eligible = (child_count > 0) | tax_unit.any(
            is_head_or_spouse & (age >= p.childless_min_age)
        )
        state_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count,
            demographic_eligible,
            filer_has_tin,
        )
        match = parameters(period).gov.states.il.tax.income.credits.eitc.match
        return state_eitc * match
