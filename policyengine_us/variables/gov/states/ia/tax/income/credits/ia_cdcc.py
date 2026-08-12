from policyengine_us.model_api import *


class ia_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf#page=2",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=86",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf#page=2",
        "https://revenue.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=86",
        "https://revenue.iowa.gov/taxes/tax-guidance/individual-income-tax/1040-expanded-instructions/child-dependent-care-credit",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # Pre-2023: the percentage table is keyed on Iowa net income
        # (IA 1040 line 26, columns A and B combined), per the Line 60
        # worksheet and Iowa Admin. Code r. 701-304.15.
        federal_cdcc = tax_unit("cdcc_potential", period)
        net_income = add(tax_unit, period, ["ia_net_income"])
        p = parameters(period).gov.states.ia.tax.income
        return federal_cdcc * p.credits.child_care.fraction.calc(net_income)

    def formula_2023(tax_unit, period, parameters):
        # The 2022 Iowa tax reform (HF 2317) shifted Iowa's tax base to
        # federal taxable income, so the post-reform consolidated path
        # is the operative measure for the CDCC fraction lookup and it
        # already inherits federal Schedule 1-A deductions such as the
        # OBBBA enhanced senior deduction.
        federal_cdcc = tax_unit("cdcc_potential", period)
        taxable_income = tax_unit("ia_taxable_income_consolidated", period)
        p = parameters(period).gov.states.ia.tax.income
        return federal_cdcc * p.credits.child_care.fraction.calc(taxable_income)
