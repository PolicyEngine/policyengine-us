from policyengine_us.model_api import *


class ia_is_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "whether or not exempt from Iowa income tax because of low income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=37"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=37"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        is_single = filing_status == filing_status.possible_values.SINGLE
        p = parameters(period).gov.states.ia.tax.income.tax_exempt
        elderly_head = tax_unit("age_head", period) >= p.elderly_age
        elderly_spouse = tax_unit("age_spouse", period) >= p.elderly_age
        is_elderly = elderly_head | elderly_spouse
        pil = p.income_limit
        modified_income_limit = where(
            is_single,
            where(is_elderly, pil.single_elderly, pil.single_nonelderly),
            where(is_elderly, pil.other_elderly, pil.other_nonelderly),
        )
        return tax_unit("ia_modified_income", period) <= modified_income_limit
