from policyengine_us.model_api import *


class dc_medicaid_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "DC Medicaid income eligible"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/alliance",
        "https://dhcf.dc.gov/sites/default/files/dc/sites/dhcf/publication/attachments/Alliance%20and%20ICP%20Program%20Changes%20Resource%20Document.pdf",
    ]

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhcf.medicaid.eligibility
        medicaid_income_level = person("medicaid_income_level", period)

        age = person("age", period)
        is_pregnant = person("is_pregnant", period)
        is_child = age <= 20

        # Different income limits based on category
        # NOTE: NO grandfathering for income - if income exceeds new limit,
        # person will be disenrolled regardless of current enrollment status
        if is_pregnant:
            # Pregnant women up to 324% FPL regardless of immigration status
            income_limit = p.pregnant_income_limit
        elif is_child:
            # Children 0-20: higher limit (unchanged from current)
            income_limit = p.child_income_limit
        else:
            # Adults 21+: Changes from 215% to 138% FPL on 10/1/2025
            # No grandfathering - those over 138% FPL will lose coverage
            income_limit = p.adult_income_limit

        return medicaid_income_level <= income_limit