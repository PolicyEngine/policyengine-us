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

        # ORS 315.264 takes the qualifying individuals of IRC 21(b)(1): a
        # child dependent (a return on which a filer can be claimed has no
        # dependents, IRC 152(b)(1)); a disabled dependent, determined without
        # regard to 152(b)(1); and a disabled spouse. Schedule OR-WFHDC:
        # "the word 'you' also refers to your spouse".
        person = tax_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        spouse = person("is_tax_unit_spouse", period)
        head = person("is_tax_unit_head", period)
        joint = tax_unit("tax_unit_married", period)
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        child = dependent & (age <= p.child_age_limit) & ~dependent_filer
        disabled_dependent = dependent & disabled
        # On a joint return either spouse can be the other's qualifying
        # individual.
        disabled_spouse = disabled & (spouse | head) & joint
        qualifying_individuals = child | disabled_dependent | disabled_spouse

        return tax_unit.any(qualifying_individuals)
