from otree.api import *

doc = """
This is a common pool resource game designed to test how anonymity affects cooperation among people
"""


class C(BaseConstants):
    NAME_IN_URL = 'anonymous_cpr'
    NUM_PLAYERS = 8
    NUM_UNIQUE_GROUPS = 4
    PLAYERS_PER_GROUP = int(NUM_PLAYERS/NUM_UNIQUE_GROUPS)
    NUM_ROUNDS = 1
    PAYOFF = 100
    COST_MULTIPLIER = 70
    RESOURCE = 100
    GROUP_TYPES = ['NA_chat','A','NA','A_chat']


class Subsession(BaseSubsession):
    def creating_sessions(self):
        if self.round_number == 1:
            self.group_randomly()
        else:
            self.group_like_round(1)


class Group(BaseGroup):
    shared_resource = models.IntegerField(initial=C.RESOURCE)
    total_extraction = models.IntegerField(initial=0)
    round_extraction = models.IntegerField(initial=0)


class Player(BasePlayer):
    username = models.StringField(label="Username")
    extraction = models.IntegerField(initial = 0, min=0)
    cost = models.FloatField()
    total_extraction = models.IntegerField(intial = 0)

def extraction_max(player : Player):
    players = player.group.get_players()
    extractions = [p.extraction for p in players]
    tot_extractions = sum(extractions)
    if (C.RESOURCE - tot_extractions)<(int((C.RESOURCE / C.PLAYERS_PER_GROUP)) + 10):
        return C.RESOURCE - tot_extractions
    else:
        return int(C.RESOURCE / C.PLAYERS_PER_GROUP)+10
        # FUNCTIONS

def get_group_type(id_number):
    index = id_number % C.NUM_UNIQUE_GROUPS
    return C.GROUP_TYPES[index]

def set_payoffs(group: Group):
    players = group.get_players()
    extractions = [p.extraction for p in players]
    group.round_extraction = sum(extractions)
    group.total_extraction += group.round_extraction
    group.shared_resource -= group.round_extraction

    if group.shared_resource == 0:
        group.shared_resource = 1

    for p in players:
        if p.extraction == 0:
            p.cost = 0
            p.payoff = 0
            p.total_extraction = 0
        else:
            p.cost = (p.extraction * group.round_extraction * C.COST_MULTIPLIER) / C.RESOURCE
            p.payoff = (p.extraction*C.PAYOFF) - p.cost
            p.total_extraction = p.extraction
            if p.round_number!=1:
                p.total_extraction += p.in_round(p.round_number-1).total_extraction


# PAGES

class IntroOne(Page):
    @staticmethod
    def vars_for_template(player : Player):
        return {
            'group_size':C.PLAYERS_PER_GROUP-1,
            'payoff':C.PAYOFF,
            'amount_coal':C.RESOURCE,
            'rounds':C.NUM_ROUNDS,
            'group_type': get_group_type(player.group.id_in_subsession),
        }

    timeout_seconds = 90
    form_model = 'player'
    form_fields = {"username"}

class IntroTwo(Page):
    @staticmethod
    def vars_for_template(player : Player):
        return {
            'group_size':C.PLAYERS_PER_GROUP-1,
            'payoff':C.PAYOFF,
            'amount_coal':C.RESOURCE,
            'rounds':C.NUM_ROUNDS,
            'group_type': get_group_type(player.group.id_in_subsession),
        }

    timeout_seconds = 90

class IntroThree(Page):
    @staticmethod
    def vars_for_template(player : Player):
        return {
            'group_size':C.PLAYERS_PER_GROUP-1,
            'payoff':C.PAYOFF,
            'amount_coal':C.RESOURCE,
            'rounds':C.NUM_ROUNDS,
            'group_type': get_group_type(player.group.id_in_subsession),
            'multiplier':C.COST_MULTIPLIER,
            'max_extraction':(int(C.RESOURCE / C.PLAYERS_PER_GROUP)+10),
        }
    timeout_seconds = 90

class ExtraInfoOne(Page):
    @staticmethod
    def is_displayed(self):
        return (get_group_type(self.group.id_in_subsession) == 'NA_chat') or (get_group_type(self.group.id_in_subsession) == 'NA')
    timeout_seconds = 90

class ExtraInfoTwo(Page):
    @staticmethod
    def is_displayed(self):
        return (get_group_type(self.group.id_in_subsession) == 'A_chat') or (get_group_type(self.group.id_in_subsession) == 'NA_chat')

    timeout_seconds = 90


class Extract(Page):
    @staticmethod
    def is_displayed(self):
        return (get_group_type(self.group.id_in_subsession) == 'A') or (get_group_type(self.group.id_in_subsession) == 'NA')

    timeout_seconds = 300

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number != 1:
            player.username = player.in_round(1).username

        return {
            'group_size':C.PLAYERS_PER_GROUP,
            'payoff':C.PAYOFF,
            'amount_coal':C.RESOURCE,
            'rounds':C.NUM_ROUNDS,
            'group_type': get_group_type(player.group.id_in_subsession),
            'remaining_coal': player.group.shared_resource,
            'extracted_coal': player.group.total_extraction,
        }

    form_model = 'player'
    form_fields = {"extraction"}

class ExtractN(Page):
    @staticmethod
    def is_displayed(self):
        return (get_group_type(self.group.id_in_subsession) == 'A_chat') or (get_group_type(self.group.id_in_subsession) == 'NA_chat')

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number != 1:
            player.username = player.in_round(1).username

        return {
            'group_size':C.PLAYERS_PER_GROUP,
            'payoff':C.PAYOFF,
            'amount_coal':C.RESOURCE,
            'rounds':C.NUM_ROUNDS,
            'group_type': get_group_type(player.group.id_in_subsession),
            'remaining_coal': player.group.shared_resource,
            'extracted_coal': player.group.total_extraction,
        }


    form_model = 'player'
    form_fields = {"extraction"}
    timeout_seconds = 300


class Results(Page):
    @staticmethod
    def is_displayed(self):
        return get_group_type(self.group.id_in_subsession) == 'A'
    @staticmethod
    def vars_for_template(player : Player):
        return {
            "extraction":player.extraction,
            "payoff":player.payoff,
            "cost":player.cost,
            "remaining_coal":player.group.shared_resource,
            "extracted_coal":player.group.round_extraction,
            "total_extraction":player.group.total_extraction,
        }

    timeout_seconds = 90


class ResultsN(Page):
    @staticmethod
    def is_displayed(self):
        return get_group_type(self.group.id_in_subsession) == 'NA_chat'

    @staticmethod
    def vars_for_template(player : Player):

        players = player.group.get_players()
        extractions = sorted([(p.username, p.total_extraction) for p in players], key=lambda x: x[1], reverse=True)

        return {
            "extraction":player.extraction,
            "payoff":player.payoff,
            "cost":player.cost,
            "remaining_coal":player.group.shared_resource,
            "extracted_coal":player.group.round_extraction,
            "total_extraction":player.group.total_extraction,
            "extractions":extractions,
        }

    timeout_seconds = 90


class ResultsRankings(ResultsN):
    @staticmethod
    def is_displayed(self):
        return get_group_type(self.group.id_in_subsession) == 'NA'

    timeout_seconds = 90


class ResultsChat(ResultsN):
    @staticmethod
    def is_displayed(self):
        return get_group_type(self.group.id_in_subsession) == 'A_chat'

    timeout_seconds = 90


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


page_sequence = [IntroOne, IntroTwo, IntroThree, ExtraInfoOne, ExtraInfoTwo, Extract, ExtractN, ResultsWaitPage, Results, ResultsRankings, ResultsChat, ResultsN]
