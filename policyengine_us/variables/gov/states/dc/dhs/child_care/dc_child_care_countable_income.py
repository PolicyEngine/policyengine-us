from policyengine_us.model_api import *


class dc_child_care_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Countable income for DC Childcare Subsidy"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        # Get countable income sources from parameters
        countable_sources = parameters(
            period
        ).gov.states.dc.dhs.child_care.countable_income
        person = spm_unit.members

        # Initialize total countable income
        countable_income = 0

        # Add each countable income source
        for source in countable_sources:
            # Handle person-level variables
            if source in [
                "earned_income",
                "self_employment_income",
                "alimony_received",
                "pension_income",
            ]:
                countable_income += spm_unit.sum(person(source, period))
            # Handle SPM unit level variables
            elif source in ["rental_income"]:
                # Note: this might be person-level in the actual implementation,
                # but we're handling at the unit level for demonstration
                if hasattr(spm_unit, source):
                    countable_income += spm_unit(source, period)
            # Education grants and retirement distributions not directly available
            elif source in ["education_grants", "retirement_distributions"]:
                # These are placeholders for income sources we don't have direct variables for
                pass

        # Subtract exempt income
        exempt_income = spm_unit("dc_child_care_exempt_income", period)
        countable_income = max_(0, countable_income - exempt_income)

        return countable_income
