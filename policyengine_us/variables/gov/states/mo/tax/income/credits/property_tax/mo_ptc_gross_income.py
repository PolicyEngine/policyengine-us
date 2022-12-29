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
        person = tax_unit.members
        # compute core person-level income included in PTC gross income
        core_inc = add(
            person,
            period,
            [
                "mo_adjusted_gross_income",  # Form MO-PTS, line 1
                "tax_exempt_pension_income",  # Form MO-PTS, line 3
                "tax_exempt_interest_income",  # Form MO-PTS, line 3
            ],
        )
        core_income = tax_unit.sum(core_inc)
        tax_exempt_socsec_benefits = tax_unit(
            "tax_exempt_social_security",  # Form MO-PTS, line 2
            period,
        )
        # compute veterans benefits included in PTC gross income
        veterans_benefits = person("veterans_benefits", period)
        exclude = person("is_fully_disabled_service_connected_veteran", period)
        included_veterans_benefits = ~exclude * veterans_benefits
        veterans_benefits_income = tax_unit.sum(
            # Form MO-PTS, line 5
            included_veterans_benefits
        )
        # compute public assistance included in PTC gross income
        pa_inc = add(
            person,
            period,
            [
                # Form MO-PTS, line 6
                "ssi",
                "state_supplement",
                "child_support_received",
                "tanf_person",
            ],
        )
        public_assistance_income = tax_unit.sum(pa_inc)
        # compute nonbusiness capital losses included in PTC gross income
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
            + tax_exempt_socsec_benefits
            + veterans_benefits_income
            + public_assistance_income
            + nonbusiness_losses
        )
