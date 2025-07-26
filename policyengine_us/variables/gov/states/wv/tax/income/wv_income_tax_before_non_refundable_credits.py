from policyengine_us.model_api import *


class wv_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia income tax before non-refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        taxable_income = tax_unit("wv_taxable_income", period)
        # Calculate for each of the filing statuses and return the appropriate one.
        p = parameters(period).gov.states.wv.tax.income.rates
        filing_status_dict = {
            "single": p.single,
            "separate": p.separate,
            "joint": p.joint,
            "head_of_household": p.head,
            "surviving_spouse": p.surviving_spouse,
        }
        return select_filing_status_value(
            filing_status,
            filing_status_dict,
            taxable_income,
        )
