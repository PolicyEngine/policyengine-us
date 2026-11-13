from policyengine_us.model_api import *


class ma_gross_income_loss_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA gross income loss adjustment for Form 1 lines 6 and 7"
    unit = USD
    definition_period = YEAR
    reference = ("https://www.mass.gov/doc/2024-form-1-instructions/download",)
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # MA Form 1 allows losses on lines 6a, 6b, and 7 to offset
        # other 5.0% income. irs_gross_income floors each source at
        # zero for each person, so this variable captures the losses that
        # were dropped, person by person: one spouse's loss offsets the
        # other spouse's income on the joint return.
        # Line 10 instruction: "Be sure to subtract any losses
        # in lines 6 or 7."
        # irs_gross_income leaves out tax unit dependents, whose items are
        # on their own returns, so their losses are left out here too.
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        sources = [
            # Line 6a: Business/profession loss (Schedule C)
            "self_employment_income",
            "sstb_self_employment_income",
            # Line 6b: Farm loss (Schedule F)
            "farm_operations_income",
            # Line 7: Rental, partnership, S-corp, farm rent losses
            "rental_income",
            "partnership_s_corp_income",
            "farm_rent_income",
        ]
        losses = 0
        for source in sources:
            losses += tax_unit.sum(not_dependent * min_(person(source, period), 0))
        return losses
