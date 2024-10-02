from policyengine_us.model_api import *


class or_wfhdc_has_qualified_individual_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Check if household has eligible individuals for Oregon Working Family Household and Dependent Care Credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Check if the household has a child or disabled member other than the household head.
        # Note that a disabled spouse is a qualifying individual.
        person = tax_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)
        head = person("is_tax_unit_head", period)
        qualifying_individuals = (age <= p.child_age_limit) | (
            disabled & ~head
        )

        return tax_unit.any(qualifying_individuals)
