from policyengine_us.model_api import *


class sc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina taxable income"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=33",
        "https://www.scstatehouse.gov/sess126_2025-2026/bills/4216.htm",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.deductions.sciad
        subtractions = tax_unit("sc_subtractions", period)

        if p.in_effect:
            # H.4216: start from federal AGI; the SCIAD replaces the federal
            # standard and itemized deductions. The additions that reverse
            # deductions taken after AGI (state tax, QBI, OBBBA) no longer
            # apply, but other additions to income (SC1040 line e) still do.
            agi = tax_unit("adjusted_gross_income", period)
            other_additions = tax_unit("sc_other_additions", period)
            return max_(0, agi + other_additions - subtractions)
        else:
            # Traditional calculation from federal taxable income
            taxable_income = tax_unit("taxable_income", period)
            additions = tax_unit("sc_additions", period)
            return max_(0, taxable_income + additions - subtractions)
