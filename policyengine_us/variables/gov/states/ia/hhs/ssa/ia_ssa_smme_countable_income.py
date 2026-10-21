from policyengine_us.model_api import *


class ia_ssa_smme_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SMME countable income for Medicaid coverage group"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "SSI countable income plus any SSI payment, combined for a couple whose SSI couple computation applies. Deductions and financial groups of a Medicaid coverage category that differ from SSI are not modeled."
    reference = (
        # Iowa Code 249.3(4)(g)
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        # 441 IAC 51.7(6)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=2",
        "https://hhs.iowa.gov/media/3987/download?inline=#page=77",
    )

    def formula(person, period, parameters):
        # 6-B Income (SMME): income "is determined according to SSI income
        # criteria". ia_ssa compares it with 120 percent of the poverty
        # guideline as Iowa Code 249.3(4)(g) sets it ("at least"; see the NOTE
        # in ia_ssa). ia_ssa uses the guideline for
        # the recipient and any spouse (ia_ssa_has_spouse), so an eligible
        # couple's combined income is compared with the two-person guideline
        # (ia_ssa.yaml Cases 47-49).
        # NOTE: With an ineligible spouse, SSI countable income includes only
        # the income SSI deems from that spouse, and none when the spouse's
        # income is at or below the deeming threshold, while the guideline is
        # still for two people. Group-specific Medicaid budgeting is not
        # modeled.
        income = person("ssi_countable_income", period) + person("ssi", period)
        joint = person("ssi_couple_computation_applies", period)
        return where(joint, person.marital_unit.sum(income), income)
