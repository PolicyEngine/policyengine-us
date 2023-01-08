from policyengine_us.model_api import *


class md_socsec_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD social security subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-ii-maryland-adjusted-gross-income/section-10-208-effective-until-712024-subtractions-from-federal-adjusted-gross-income-state-adjustments"
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=14"
    )
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        unit_tss = person.tax_unit("tax_unit_taxable_social_security", period)
        # allocate unit_tss to head and spouse in proportion to social_security
        unit_socsec = person.tax_unit("tax_unit_social_security", period)
        unit_has_socsec = unit_socsec > 0
        ind_socsec = person("social_security", period)
        is_spouse = person("is_tax_unit_spouse", period)
        spouse_frac = min_(
            1, where(is_spouse & unit_has_socsec, ind_socsec / unit_socsec, 0)
        )
        unit_spouse_frac = person.tax_unit.sum(spouse_frac)
        is_head = person("is_tax_unit_head", period)
        head_frac = where(is_head & unit_has_socsec, 1 - unit_spouse_frac, 0)
        unit_head_frac = person.tax_unit.sum(head_frac)
        """
        print("\n******************************************")
        print("unit_tss=", unit_tss)
        print("unit_socsec", unit_socsec)
        print("ind_socsec", ind_socsec)
        print("spouse_frac=", spouse_frac)
        print("unit_spouse_frac=", unit_spouse_frac)
        print("head_frac=", head_frac)
        print("unit_head_frac=", unit_head_frac)
        """
        return select(
            [is_head, is_spouse, ~(is_head | is_spouse)],
            [unit_head_frac * unit_tss, unit_spouse_frac * unit_tss, 0],
        )
