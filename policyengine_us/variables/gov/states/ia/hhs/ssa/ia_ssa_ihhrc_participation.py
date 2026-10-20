from policyengine_us.model_api import *


class ia_ssa_ihhrc_participation(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA in-home health-related care client participation"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    reference = (
        # 441 IAC 177.2(1)"f"-"g" and 177.8(2)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.177.pdf#page=1",
        # PDF pages 41-43, 49
        "https://hhs.iowa.gov/media/3987/download?inline=#page=41",
    )

    def formula(person, period, parameters):
        # 6-B Home Maintenance Allowance (IHHRC) prints the SSI individual and
        # couple standards ($994 and $1,491) and gives the couple allowance
        # "even if only one spouse receives in-home health-related care", so
        # the federal benefit rates are used and an SSI reform carries over.
        # A child's marital unit has one member and receives the individual
        # standard.
        ssi = parameters(period).gov.ssa.ssi
        income = person("ia_ssa_care_countable_income", period)
        deductions = max_(person("ia_ssa_care_additional_deductions", period), 0)
        has_spouse = person.marital_unit.nb_persons() == 2
        maintenance = where(has_spouse, ssi.amount.couple, ssi.amount.individual)
        deductions = where(has_spouse, person.marital_unit.sum(deductions), deductions)
        participation = max_(income - maintenance - deductions, 0)
        # No client participation is required in a first partial month.
        return where(
            person("ia_ssa_ihhrc_initial_partial_month", period), 0, participation
        )
