from policyengine_us.model_api import *


class ia_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa itemized deductions for tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
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
        else:
            return add(
                tax_unit,
                period,
                ["itemized_deductions_less_salt", "real_estate_taxes"],
            )
