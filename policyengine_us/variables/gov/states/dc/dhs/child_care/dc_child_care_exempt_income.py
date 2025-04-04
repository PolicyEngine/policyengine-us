from policyengine_us.model_api import *


class dc_child_care_exempt_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Exempt income for DC Childcare Subsidy"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        # Get exempt income sources from parameters
        exempt_sources = parameters(
            period
        ).gov.states.dc.dhs.child_care.exempt_income
        person = spm_unit.members

        # Initialize total exempt income
        exempt_income = 0

        # Add each exempt income source
        for source in exempt_sources:
            # Handle person-level variables
            if source in [
                "social_security",
                "ssi",
                "unemployment_compensation",
                "child_support_received",
                "eitc",
            ]:
                exempt_income += spm_unit.sum(person(source, period))
            # Handle SPM unit level variables
            elif source in ["tanf", "snap", "wic"]:
                exempt_income += spm_unit(source, period)
            # Tax refunds and other sources not directly available
            elif source in [
                "tax_refunds",
                "foster_care_payments",
                "non_recurring_income",
            ]:
                # These are placeholders for income sources we don't have direct variables for
                pass

        return exempt_income
