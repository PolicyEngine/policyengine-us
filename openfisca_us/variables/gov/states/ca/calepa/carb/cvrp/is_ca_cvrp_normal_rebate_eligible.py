from openfisca_us.model_api import *


class is_ca_cvrp_normal_rebate_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for CVRP normal rebate"
    documentation = "Eligible for California Clean Vehicle Rebate Project (CVRP) normal rebate"
    reference = "https://cleanvehiclerebate.org/en/eligibility-guidelines"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        # AGI must be less than the threshold.
        agi = person.tax_unit("adjusted_gross_income", period)
        filing_status = person.tax_unit("filing_status", period)
        caps = parameters(period).gov.states.ca.calepa.carb.cvrp.income_cap
        return agi <= caps[filing_status]
