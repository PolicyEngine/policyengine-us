from policyengine_us.model_api import *


class mo_ptc_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        core_income = add(
            tax_unit,
            period,
            [
                "mo_adjusted_gross_income",  # Form MO-PTS, line 1
                "tax_exempt_social_security",  # Form MO-PTS, line 2
                "tax_exempt_pension_income",  # Form MO-PTS, line 3
                "tax_exempt_interest_income",  # Form MO-PTS, line 3
            ],
        )
        # compute veterans benefits that are included in gross income
        person = tax_unit.members
        veterans_benefits = person("veterans_benefits", period)
        exclude = person("is_fully_disabled_service_connected_veteran", period)
        included_veterans_benefits = ~exclude * veterans_benefits
        veterans_benefits_income = tax_unit.sum(  # Form MO-PTS, line 5
            included_veterans_benefits
        )
        # compute public assistance that is included in gross income
        public_assistance_income = add(  # Form MO-PTS, line 6
            # The second reference above says that SNAP is not counted as
            #   public assistance income for the MO property tax credit
            tax_unit,
            period,
            [
                "ssi",
                "state_supplement",
                "child_support_received",
                "tanf_person"
            ],
        )
        # compute nonbusiness capital losses that are included in gross income
        nonbusiness_losses = add(  # Form MO-PTS, line 7
            tax_unit,
            period,
            [
                "short_term_capital_losses",
                "long_term_capital_losses",
            ],
        )
        return (  # Form MO-PTS, line 8
            core_income
            + veterans_benefits_income
            + public_assistance_income
            + nonbusiness_losses
        )
