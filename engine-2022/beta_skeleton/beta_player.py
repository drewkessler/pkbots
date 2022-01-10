'''
Simple example pokerbot, written in Python.
'''
import random
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from support import *


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.opp_range = []
        self.opp_range_mapping = {} # mapping opp_range to expected win rate


    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot


        my_action = None
        min_raise, max_raise = round_state.raise_bounds()
        pot_total = my_contribution + opp_contribution # total in pot

        if street < 3: # we're preflop
            raise_amount = int(my_pip + continue_cost + 0.2*(pot_total + continue_cost))
        else:
            raise_amount = int(my_pip + continue_cost + 0.5*(pot_total + continue_cost))


        raise_cost = raise_amount - my_pip # how much it costs to make said raise
        if (RaiseAction in legal_actions and (raise_cost <= my_stack)): #only consider raising if the hand we have is strong
            temp_action = RaiseAction(raise_amount)
        elif (CallAction in legal_actions and (continue_cost <= my_stack)): #only consider raising if the hand we have is strong
            temp_action = CallAction()
        elif CheckAction in legal_actions:
            temp_action = CheckAction()
        else:
            temp_action = FoldAction()


        _MONTE_CARLO_ITERS= 100
        
        # calculating the strength of the current expected opp_range
        opp_range = self.opp_range.copy()
        for potential_opp_hand in opp_range:
            alreadyTaken = False

            for card in board_cards:
                if card in potential_opp_hand:
                    alreadyTaken = True
                
            if not alreadyTaken:
                self.opp_range_mapping[tuple(potential_opp_hand)] = calc_strength(potential_opp_hand, _MONTE_CARLO_ITERS, community = board_cards)
            else: # cleared out of the range
                self.opp_range.remove(potential_opp_hand)
                if tuple(potential_opp_hand) in self.opp_range_mapping.keys():
                    del self.opp_range_mapping[tuple(potential_opp_hand)]

        
        if continue_cost > 0:

            pot_odds = continue_cost / (pot_total + continue_cost) # calculating pot odds of staying continuation cost
            
            # updating estimate of opponent's range
            current_range_in_mapping = list(self.opp_range_mapping.keys())
            for potential_opp_hand_tuple in current_range_in_mapping:

                potential_opp_hand = list(potential_opp_hand_tuple) # converting the key from tuple to list

                if self.opp_range_mapping[potential_opp_hand_tuple] <= get_mean_strength_from_range(self.opp_range_mapping) * 1.5:
                    if potential_opp_hand in self.opp_range:
                        self.opp_range.remove(potential_opp_hand)
                        del self.opp_range_mapping[potential_opp_hand_tuple]

            
            # getting our strength against expected opp_range
            strength_against_range = calc_strength_against_range(my_cards, int(_MONTE_CARLO_ITERS/33), community = board_cards, opp_range = self.opp_range)


            if strength_against_range >= pot_odds:

                if strength_against_range > 0.5 and random.random() < strength_against_range:
                    my_action = temp_action
                
                else: 
                    my_action = CallAction()

            else: # negative ev

                my_action = FoldAction()



        else: # continuation cost is 0

            if random.random() < calc_strength(my_cards, _MONTE_CARLO_ITERS, community = board_cards):
                my_action = temp_action
            
            else:
                my_action = CheckAction()


        return my_action
            



if __name__ == '__main__':
    run_bot(Player(), parse_args())
