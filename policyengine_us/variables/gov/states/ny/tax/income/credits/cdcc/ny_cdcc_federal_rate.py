from policyengine_us.model_api import *


class ny_cdcc_federal_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CDCC federal-style decimal (Form IT-216 line 10)"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://www.tax.ny.gov/pdf/2021/inc/it216i_2021.pdf#page=6",
        "https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        # Form IT-216 line 10 takes this decimal from the Table for line 10,
        # based on recomputed federal AGI (IT-201 line 19a). New York does not
        # use the federal Form 2441 rate, so the 2021 ARPA rates do not apply.
        p = parameters(period).gov.states.ny.tax.income.credits.cdcc.federal_rate
        agi = tax_unit("adjusted_gross_income", period)
        steps = np.ceil(max_(0, agi - p.start) / p.increment)
        return max_(p.min, p.max - steps * p.step)
