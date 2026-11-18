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
        # California excludes an individual under RTC 17053.5(d)(2) after an actual claim
        # and residence with that claimant for more than half the year.
        # Follow the actual-claim statute rather than the form's claimability test.
        # FTB also stops readers without addressing (d)(2)'s individual scope.
        # An eligible joint filer keeps $120 for 2025 under (a)(1)(A).
        # Legislators expressly extend the homeowner exclusion to a spouse
        # in (d)(3), but keep the dependent exclusion individual in (d)(2).
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
