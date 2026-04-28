from policyengine_us.model_api import *


class ky_ssp(Variable):
    value_type = float
    entity = Person
    label = "Kentucky State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.KY
    exhaustive_parameter_dependencies = "gov.states.ky.dcbs.ssp"
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=7671",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=5",
    )

    def formula(person, period, parameters):
        # §8(2): supplement = max(0, standard_of_need − countable_income).
        # For eligible joint couples (§9(2)), SSI already attributes combined
        # income equally to each spouse via ssi_marital_{earned,unearned}_income,
        # and per-person standards stored in payment_standard (half of couple
        # totals for CARETAKER) reproduce the §9(2)(b) "one-half of the
        # deficit to each" outcome without explicit marital_unit averaging.
        #
        # APPROXIMATION: Per OMVOLV examples, the Caretaker "Eligible Couple,
        # One Receives Care" standard ($1,552) is paid entirely to the care
        # receiver (per MS 1200 §B.6). This model stores that standard as
        # per-person ($776) and pays each spouse an equal share. The household
        # total matches the regulation exactly; only the per-spouse split
        # differs.
        payment_standard = person("ky_ssp_payment_standard", period)
        countable_income = person("ssi_countable_income", period)
        eligible = person("ky_ssp_eligible", period)
        return max_(0, payment_standard - countable_income) * eligible
