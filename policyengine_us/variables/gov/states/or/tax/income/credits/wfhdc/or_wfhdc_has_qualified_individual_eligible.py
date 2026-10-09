from policyengine_us.model_api import *


class or_wfhdc_has_qualified_individual_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Check if household has eligible individuals for Oregon Working Family Household and Dependent Care Credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2025.pdf#page=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Check if the household has a child, a disabled dependent, or a
        # disabled spouse. On a joint return "you" also means your spouse,
        # so either married filer is the other's qualifying spouse; a single
        # filer is not their own qualifying individual.
        person = tax_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        married = tax_unit.project(tax_unit.any(person("is_tax_unit_spouse", period)))
        qualifying_individuals = (age <= p.child_age_limit) | (
            disabled & (~head_or_spouse | married)
        )

        return tax_unit.any(qualifying_individuals)
