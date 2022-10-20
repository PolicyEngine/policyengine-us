from policyengine_us.model_api import *
import warnings

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")


class ma_limited_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Limited Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-schedule-nts-l-nrpy-no-tax-status-and-limited-income-credit/download"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ma_agi", period)
        exemption_threshold = tax_unit(
            "ma_income_tax_exemption_threshold", period
        )
        lic = parameters(
            period
        ).gov.states.ma.tax.income.credits.limited_income_credit
        income_level = agi / exemption_threshold
        eligible = income_level <= lic.income_limit
        income_tax = tax_unit("ma_income_tax_before_credits", period)
        income_over_threshold = max_(0, agi - exemption_threshold)
        tax_cap = lic.percent * income_over_threshold
        excess_tax = max_(0, income_tax - tax_cap)
        return eligible * excess_tax
