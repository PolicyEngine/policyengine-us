from policyengine_us.model_api import *


class ia_amt_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa alternative minimum tax when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=55"
        "https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=55"
        "https://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        # compute Iowa AMT taxable income
        reg_taxinc = person("ia_taxable_income_joint", period)
        std_ded = person("ia_standard_deduction_joint", period)
        itm_ded = person("ia_itemized_deductions_joint", period)
        is_head = person("is_tax_unit_head", period)
        proptax = add(person.tax_unit, period, ["real_estate_taxes"])
        amt_taxinc = where(
            itm_ded > std_ded,
            reg_taxinc + is_head * proptax,
            reg_taxinc,
        )
        # compute AMT amount
        p = parameters(period).gov.states.ia.tax.income
        amt = p.alternative_minimum_tax
        filing_status = person.tax_unit("filing_status", period)
        amt_threshold = amt.threshold[filing_status]  # Line 23
        amt_exemption = amt.exemption[filing_status]  # Line 24
        netinc = max_(0, amt_taxinc - amt_exemption)  # Line 25
        amount = max_(0, amt_threshold - netinc * amt.fraction)  # Line 27
        gross_amt = max_(0, amt_taxinc - amount) * amt.rate  # Line 29
        base_tax = person("ia_base_tax_joint", period)  # Line 30
        return max_(0, gross_amt - base_tax)  # Line 31
