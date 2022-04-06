from openfisca_us.model_api import *


class additional_medicare_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Additional Medicare Tax"
    unit = USD
    documentation = (
        "Additional Medicare Tax from Form 8959 (included in payrolltax)"
    )

    def formula(tax_unit, period, parameters):
        payroll = parameters(period).irs.payroll
        positive_sey = max_(0, tax_unit("filer_sey", period))
        combined_rate = (
            payroll.medicare.rate.employee
            + payroll.social_security.rate.employee
        )
        line8 = positive_sey * (1 - combined_rate)
        mars = tax_unit("mars", period)
        e00200 = tax_unit("filer_e00200", period)
        exclusion = payroll.medicare.additional.exclusion[mars]
        earnings_over_exclusion = max_(0, e00200 - exclusion)
        line11 = max_(0, exclusion - e00200)
        rate = payroll.medicare.additional.rate
        base = earnings_over_exclusion + max_(0, line8 - line11)
        return rate * base
