from policyengine_us.model_api import *


class oh_qualifying_capital_gain_deduction(Variable):
    value_type = float
    entity = Person
    label = "Ohio qualifying capital gain deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.79(B); R.C. 5747.01(A)(34)
        "https://codes.ohio.gov/ohio-revised-code/section-5747.79",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.deductions.qualifying_capital_gain
        if not p.in_effect:
            return 0
        # The lesser of the qualifying capital gain or the deductible payroll.
        # The model counts capital gains as nonbusiness income, so none of
        # this gain is also deducted as business income under (A)(28).
        gain = max_(person("oh_qualifying_capital_gain", period), 0)
        payroll = max_(
            person("oh_qualifying_capital_gain_deductible_payroll", period), 0
        )
        return min_(gain, payroll)
