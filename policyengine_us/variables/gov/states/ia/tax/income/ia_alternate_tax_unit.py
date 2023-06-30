from policyengine_us.model_api import *


class ia_alternate_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa alternate tax calculated using worksheet"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # compute alternate tax following worksheet in the instructions
        p = parameters(period).gov.states.ia.tax.income.alternate_tax
        # ... determine alternate tax deduction
        elder_head = tax_unit("age_head", period) >= p.elderly_age
        elder_spouse = tax_unit("age_spouse", period) >= p.elderly_age
        is_elder = elder_head | elder_spouse
        alt_ded = where(is_elder, p.deduction.elderly, p.deduction.nonelderly)
        # ... determine alternate tax amount
        alt_taxinc = max_(0, tax_unit("ia_modified_income", period) - alt_ded)
        alt_tax = alt_taxinc * p.rate
        # ... alternate tax is not available to single filing units
        filing_status = tax_unit("filing_status", period)
        is_single = filing_status == filing_status.possible_values.SINGLE
        return where(is_single, np.inf, alt_tax)
