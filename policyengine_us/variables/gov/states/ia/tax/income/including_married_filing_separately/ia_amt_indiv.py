from policyengine_us.model_api import *


class ia_amt_indiv(Variable):
    value_type = float
    entity = Person
    label = "Iowa alternative minimum tax when married couples file separately"
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
        p = parameters(period).gov.states.ia.tax.income
        amt = p.alternative_minimum_tax
        if amt.in_effect:
            reg_taxinc = person("ia_taxable_income_indiv", period)
            std_ded = person("ia_standard_deduction_indiv", period)
            itm_ded = person("ia_itemized_deductions_indiv", period)
            prorate_frac = person("ia_prorate_fraction", period)
            proptax = add(person.tax_unit, period, ["real_estate_taxes"])
            additional_proptax_amt_taxinc_applies = itm_ded > std_ded
            additional_proptax_amt_taxinc = (
                additional_proptax_amt_taxinc_applies * prorate_frac * proptax
            )
            amt_taxinc = reg_taxinc + additional_proptax_amt_taxinc
            # compute AMT amount
            us_filing_status = person.tax_unit("filing_status", period)
            fsvals = us_filing_status.possible_values
            filing_status = select(
                [
                    us_filing_status == fsvals.JOINT,
                    us_filing_status == fsvals.SINGLE,
                    us_filing_status == fsvals.SEPARATE,
                    us_filing_status == fsvals.HEAD_OF_HOUSEHOLD,
                    us_filing_status == fsvals.SURVIVING_SPOUSE,
                ],
                [
                    fsvals.SEPARATE,  # couples are filing separately on Iowa form
                    fsvals.SINGLE,
                    fsvals.SEPARATE,
                    fsvals.HEAD_OF_HOUSEHOLD,
                    fsvals.SURVIVING_SPOUSE,
                ],
            )
            amt_threshold = amt.threshold[filing_status]  # Line 23
            amt_exemption = amt.exemption[filing_status]  # Line 24
            netinc = max_(0, amt_taxinc - amt_exemption)  # Line 25
            amount = max_(0, amt_threshold - netinc * amt.fraction)  # Line 27
            gross_amt = max_(0, amt_taxinc - amount) * amt.rate  # Line 29
            base_tax = person("ia_base_tax_indiv", period)  # Line 30
            return max_(0, gross_amt - base_tax)  # Line 31
        return 0
