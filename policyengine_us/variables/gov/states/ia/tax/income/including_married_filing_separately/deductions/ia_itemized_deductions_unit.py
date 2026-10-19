from policyengine_us.model_api import *


class ia_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa itemized deductions for tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
        # 2018 IA Schedule A, lines 19 to 24.
        "https://revenue.iowa.gov/media/2298/download?inline=#page=1",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        """
        FROM THE 2021 INSTRUCTIONS (PAGE 46):
          The $10,000 federal cap on the itemized deduction for state and
        local taxes does not apply for Iowa purposes. Taxpayers may still
        deduct eligible state and local taxes paid, independent of the
        federal dollar limitation.
        """
        # compute tax unit's itemized deductions
        p = parameters(period).gov.states.ia.tax.income.deductions.itemized
        if p.applies_federal:
            p_fed = parameters(period).gov.irs.deductions
            return add(tax_unit, period, p_fed.itemized_deductions)
        deductions = add(
            tax_unit,
            period,
            ["itemized_deductions_less_salt", "real_estate_taxes"],
        )
        if p.misc_deduction_retained:
            # 2018: Iowa did not adopt the federal suspension of miscellaneous
            # deductions above 2% of federal AGI (Schedule A lines 19 to 24),
            # so they are added to the federal amounts, which leave them out.
            p_misc = parameters(period).gov.irs.deductions.itemized.misc
            expenses = tax_unit("total_misc_deductions", period)
            floor = p_misc.floor * tax_unit("positive_agi", period)
            deductions += max_(0, expenses - floor)
        return deductions
