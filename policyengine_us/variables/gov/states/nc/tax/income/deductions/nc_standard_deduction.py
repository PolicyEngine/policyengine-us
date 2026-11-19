from policyengine_us.model_api import *


class nc_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html"
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.nc.tax.income
        # North Carolina imports eligibility for the federal standard deduction.
        # A separate filer whose spouse itemizes federally has a zero amount.
        spouse_itemizes = tax_unit("separate_filer_itemizes", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(
            separate & spouse_itemizes, 0, p.deductions.standard.amount[filing_status]
        )
