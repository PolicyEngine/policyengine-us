from policyengine_us.model_api import *


class ca_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Renter Tax Credit"
    unit = USD
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17053.5",
        # Nonrefundable Renter's Credit Qualification Record.
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=25",
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # Check eligibility based on state, rent, filing status, and income.
        p = parameters(period).gov.states.ca.tax.income.credits.renter
        agi = tax_unit("ca_agi", period)
        has_rent = add(tax_unit, period, ["rent"]) > 0
        filing_status = tax_unit("filing_status", period)
        income_cap = p.income_cap[filing_status]
        income_eligible = agi <= income_cap
        # RTC 17053.5(d)(2) excludes an individual only after an actual claim
        # and residence with that claimant for more than half the year.
        # The form uses claimability; follow the actual-claim statute.
        # The form's stopping questions also omit the individual scope of
        # (d)(2). An eligible joint filer keeps $120 under (a)(1)(A).
        # Subsection (d)(3) expressly extends the homeowner exclusion to a
        # spouse; subsection (d)(2) does not extend the dependent exclusion.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        excluded = person("claimed_as_dependent_on_another_return", period) & person(
            "lives_with_claiming_taxpayer", period
        )
        has_qualified_renter = tax_unit.any(filer & ~excluded)
        eligible = income_eligible & has_rent & has_qualified_renter
        # Determine amount if eligible based on filing status.
        amount_if_eligible = p.amount[filing_status]
        # Return eligibility * (amount if eligible).
        return eligible * amount_if_eligible
