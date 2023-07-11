from policyengine_us.model_api import *


class ms_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the MS aged exemptions part of the parameter tree.
        p = parameters(period).gov.states.ms.tax.income.exemptions.aged

        # Get the individual filer's age.
        age_head = tax_unit("age_head", period)

        # Determine if head of household (filer) is eligible.
        head_eligible = (age_head >= p.age_threshold).astype(int)

        # Get the spouse age, if applicable.
        age_spouse = tax_unit("age_spouse", period)

        # Determine whether spouse is eligible (>= age 65).
        joint = filing_status == filing_status.possible_values.JOINT
        spouse_eligible = ((age_spouse >= p.age_threshold) * joint).astype(int)

        # Calculate total aged exemption.
        return (head_eligible + spouse_eligible) * p.amount
