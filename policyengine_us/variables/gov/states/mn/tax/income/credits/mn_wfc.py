from policyengine_us.model_api import *


class mn_wfc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota working family credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/2021/cite/290.0671"
        "https://www.revisor.mn.gov/statutes/cite/290.0671"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cwfc
        # determine count of eligible dependents using EITC rules
        count = tax_unit("eitc_child_count", period)
        # determine pre-phaseout credit amount using EITC earnings
        earnings = tax_unit("filer_adjusted_earnings", period)
        capped_earn = min_(
            earnings,
            p.wfc.pre_cwfc_legislation.phase_in.earnings_maximum.calc(count),
        )
        amount = capped_earn * p.wfc.pre_cwfc_legislation.phase_in.rate.calc(
            count
        )
        # determine phaseout reduction
        agi = tax_unit("adjusted_gross_income", period)
        income = max_(earnings, agi)
        filing_status = tax_unit("filing_status", period)
        income_threshold = where(
            filing_status == filing_status.possible_values.JOINT,
            p.wfc.pre_cwfc_legislation.phase_out.threshold.joint.calc(count),
            p.wfc.pre_cwfc_legislation.phase_out.threshold.other.calc(count),
        )
        excess_income = max_(0, income - income_threshold)
        reduction = (
            excess_income
            * p.wfc.pre_cwfc_legislation.phase_out.rate.calc(count)
        )
        # determine credit amount after phaseout if eligible
        eligible = tax_unit("mn_wfc_eligible", period)
        return eligible * max_(0, amount - reduction)
