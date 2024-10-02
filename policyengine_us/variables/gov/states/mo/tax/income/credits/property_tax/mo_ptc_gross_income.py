from policyengine_us.model_api import *


class mo_ptc_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # line numbers in comments below refer to 2021 Form MO-PTS
        person = tax_unit.members
        # compute core person-level income included in PTC gross income
        sources = [
            "mo_adjusted_gross_income",  # line 1
            "tax_exempt_pension_income",  # line 3
            "tax_exempt_interest_income",  # line 3
        ]
        core_income = tax_unit.sum(add(person, period, sources))
        # compute social security included in PTC gross income (line 2)
        exempt_socsec_benefits = tax_unit("tax_exempt_social_security", period)
        # compute veterans benefits included in PTC gross income (line 5)
        veterans_benefits = person("veterans_benefits", period)
        exclude = person("is_fully_disabled_service_connected_veteran", period)
        included_veterans_benefits = ~exclude * veterans_benefits
        veterans_benefits_income = tax_unit.sum(included_veterans_benefits)
        # compute person-level public assistance included in PTC gross income
        pa_sources = parameters(
            period
        ).gov.states.mo.tax.income.credits.property_tax.public_assistance_types
        public_assistance_income = tax_unit.sum(
            add(person, period, pa_sources)  # line 6
        )
        # compute nonbusiness capital losses in PTC gross income (line 7)
        nonbusiness_losses = tax_unit("limited_capital_loss", period)
        return (  # line 8
            core_income
            + exempt_socsec_benefits
            + veterans_benefits_income
            + public_assistance_income
            + nonbusiness_losses
        )
