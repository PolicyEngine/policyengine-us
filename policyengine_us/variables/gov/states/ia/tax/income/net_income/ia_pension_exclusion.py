from policyengine_us.model_api import *


class ia_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=26"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=26"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.net_income
        # determine eligibility for pension exclusion
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        # ... determine age eligibility
        is_an_elder = person("age", period) >= p.pension_exclusion.minimum_age
        is_elderly = (is_head & is_an_elder) | (is_spouse & is_an_elder)
        # ... determine disability eligiblity
        has_disability = person("is_permanently_and_totally_disabled", period)
        is_disabled = (is_head & has_disability) | (is_spouse & has_disability)
        # ... determine exclusion eligibility
        is_eligible = is_elderly | is_disabled
        # determine pension exclusion amount
        pension = person("taxable_pension_income", period)
        uncapped_exclusion = tax_unit.sum(is_eligible * pension)
        filing_status = tax_unit("filing_status", period)
        exclusion_cap = p.pension_exclusion.maximum_amount[filing_status]
        return min_(uncapped_exclusion, exclusion_cap)
