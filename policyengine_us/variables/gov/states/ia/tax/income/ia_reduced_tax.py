from policyengine_us.model_api import *


class ia_reduced_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa income tax reduced amount for single tax units"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=60"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=60"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # logic follows Tax Reduction Worksheet
        modified_income = tax_unit("ia_modified_income", period)  # Line 1
        p = parameters(period).gov.states.ia.tax.income.tax_reduction
        is_elderly = tax_unit("age_head", period) >= p.elderly_age
        modified_income_threshold = where(  # Line 2
            is_elderly, p.threshold.elderly, p.threshold.nonelderly
        )
        amount = max_(0, modified_income - modified_income_threshold)  # Line 3
        # reduced tax available only to single tax units
        filing_status = tax_unit("filing_status", period)
        is_single = filing_status == filing_status.possible_values.SINGLE
        return where(is_single, amount, np.inf)
        # see ia_income_tax_before_refundable_credits formula for variable use
