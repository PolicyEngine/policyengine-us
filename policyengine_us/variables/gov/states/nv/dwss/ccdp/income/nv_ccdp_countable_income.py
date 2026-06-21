from policyengine_us.model_api import *


class nv_ccdp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada CCDP countable income"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NV
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Care/Child%20Care%20Manual%20July%202024.pdf#page=55"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.ccdp.income
        # MS 306: countable gross income from the enumerated source list.
        gross_income = add(spm_unit, period, p.countable_income.sources)
        # MS 302.2/302.3: deduct court- or administratively-ordered child
        # support a required member is legally obligated to pay and actually
        # pays. `child_support_expense` is the amount paid out (not received).
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        # MS 302 allows a closed list of income deductions. Besides child
        # support paid, we don't model at the moment:
        #   - MS 302.1 Average Cost of Care (Infant $425 / Toddler $398 /
        #     Preschool $358 / School-Age $209 per child per month), which only
        #     applies to a relative caretaker receiving a Child-Only TANF grant
        #     or to SSI/Kinship child-only cases.
        #   - paid direct cash medical support (Manual Glossary).
        #   - overpayment/wage-advance repayment and the DAA/SSDI rep-payee fee.
        # No earned-income or standard disregard exists in MS 302.
        return max_(gross_income - child_support_paid, 0)
