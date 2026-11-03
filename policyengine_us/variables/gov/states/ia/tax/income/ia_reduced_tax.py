from policyengine_us.model_api import *


class ia_reduced_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa income tax reduced amount for single tax units"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline#page=60",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline#page=60",
        "https://revenue.iowa.gov/media/4152/download?inline#page=18",
        "https://revenue.iowa.gov/media/4435/download?inline#page=18",
        "https://www.legis.iowa.gov/docs/code/2022/422.5.pdf#page=3",
        # PDF pages 1-2
        "https://www.legis.iowa.gov/docs/code/2024/422.5.pdf#page=1",
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
        # The reduction is for single tax units. Iowa Code 422.5 withholds it
        # from a claimed dependent only when the claiming person's net income
        # is over the limit; the worksheet's wider bar on any filer "claimed
        # as a dependent on another person's Iowa return" gives way to it.
        # Otherwise the cap is infinite, so it cannot erase tax.
        filing_status = tax_unit("filing_status", period)
        is_single = filing_status == filing_status.possible_values.SINGLE
        disqualified = tax_unit("ia_claimed_filer_income_disqualified", period)
        return where(is_single & ~disqualified, amount, np.inf)
        # see ia_income_tax_before_refundable_credits formula for variable use
