from policyengine_us.model_api import *


class is_ca_cvrp_normal_rebate_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for CVRP normal rebate"
    documentation = (
        "Eligible for California Clean Vehicle Rebate Project (CVRP) normal rebate"
    )
    reference = (
        "https://cleanvehiclerebate.org/en/eligibility-guidelines",
        # CVRP Implementation Manual: gross annual income is Form 1040 lines
        # 1-7 and Schedule 1 lines 1-8, before adjustments.
        "http://web.archive.org/web/20220305190415/https://cleanvehiclerebate.org/sites/default/files/docs/nav/transportation/cvrp/documents/CVRP-Implementation-Manual.pdf#page=13",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        # AGI must be less than the threshold. The program counts income
        # before adjustments, so the 2020 charitable deduction for
        # non-itemizers (Form 1040 line 10b) does not lower it.
        tax_unit = person.tax_unit
        agi = tax_unit("adjusted_gross_income", period) + tax_unit(
            "charitable_contributions_ald", period
        )
        filing_status = person.tax_unit("filing_status", period)
        caps = parameters(period).gov.states.ca.calepa.carb.cvrp.income_cap
        return agi <= caps[filing_status]
