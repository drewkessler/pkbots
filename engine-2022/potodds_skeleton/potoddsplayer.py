'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from runout import gen_possible_boards, gen_possible_hands

import eval7
import random


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
    
        self.opp_raises = 0.0
        self.opp_calls = 0.0
        self.hands_played = 0.0

    def calc_strength(self, hole, iters, comm = None):
        '''
        A Monte carlo method that estimates the win probability of a pair of hole cards 
        Args:
        hole: list of 2 hole cards 
        iters: number of times the sim is run
        '''

        deck = eval7.Deck() #deck of cards
        hole_cards = [eval7.Card(card) for card in hole] #list of our hole cards

        for card in hole_cards:
            deck.cards.remove(card)

        comm_cards = []
        if not comm: # if there are community cards
            comm_cards = [eval7.Card(card) for card in comm] # list of our community cards
            for card in comm_cards:
                deck.cards.remove(card)

        score = 0

        for _ in range(iters):
            deck.shuffle()

            _COMM = 5 - len(comm_cards) 
            _OPP = 2

            draw = deck.peek(_COMM+_OPP)

            opp_hole = draw[:_OPP]
            community = draw[_OPP:] + comm_cards

            our_hand = hole_cards + community
            opp_hand = opp_hole + community

            our_hand_value = eval7.evaluate(our_hand)
            opp_hand_value = eval7.evaluate(opp_hand)

            if our_hand_value > opp_hand_value:
                score += 2 
            
            if our_hand_value == opp_hand_value:
                score += 1 
            
            else:
                score += 0
        
        hand_strength = score/(2*iters)

        return hand_strength



    def calc_potential(self, hole, comm):
        """
        ONLY CALL AT FLOP OR TURN
        Calculates positive and negative potential for a given hand. They are defined as:
        Positive potential: of all possible games with the current hand, all
        scenarios where the agent is behind but ends up winning are calculated.
        Negative potential: of all possible games with the current hand, all the
        scenarios where the agent is ahead but ends up losing are calculated.
        These values are used in conjunction with hand strength to estimate the effective
        hand strength value of a hand/pocket
        The 3 * 3 matrix that is create looks like this
               AHEAD | TIE | BEHIND
        AHEAD | 991     5     432
        TIE   | 100     90     1
        BEHIND| 874     0      581
        A quick explanation:
        matrix[AHEAD][AHEAD] represents the number of times the bot's hand was stronger than
        the opponents before and after generating possible boards.
        matrix[BEHIND][AHEAD] represents the number of times the bot's hand was weaker than the
        opponents before generating possible boards, but became the stronger hand after.
        The others follow the same logic.
        :param board: (list) a list of 3-5 Card objects that depict the current visible game board
        :param pocket: (list) a list of 2 Card objects that depict the bot's current hand
        :return:
                (list) containing the positive potential and negative potential respectively."""

        AHEAD = 0
        TIED = 1
        BEHIND = 2

        my_potential = [[0]*3 for _ in range(3)]
        p_total = [0,0,0]

        hole_cards = [eval7.Card(card) for card in hole]
        comm_cards = [eval7.CArd(card) for card in comm]

        other_pockets = gen_possible_hands(hole, comm = comm)

        ind = None
        our_init_value = eval7.evaluate(hole_cards+comm_cards)
        
        # go through each possible pocket the opponent and eval against mine
        for opp_pocket in other_pockets:
            opp_init_value = eval7.evaluate(opp_pocket+comm_cards)

            if our_init_value > opp_init_value: # we're ahead
                ind = AHEAD

            elif our_init_value == opp_init_value: # we're tied
                ind = TIED
            
            else: # we're behind
                ind = BEHIND



            #check possible future boards
            for possible_board in gen_possible_boards(hole,opp_pocket,comm):
                our_end_value = eval7.evaluate(hole+possible_board)
                opp_end_value = eval7.evaluate(opp_pocket+possible_board)

                if our_end_value > opp_end_value: # we're ahead
                    my_potential[ind][AHEAD] += 1
                
                elif our_end_value == opp_end_value: # we're tied
                    my_potential[ind][TIED] += 1
                
                else: # we're behind
                    my_potential[ind][BEHIND] += 1

                p_total[ind] += 1

            
        
        pos_potential, neg_potential = 0.0,0.0
        try:
            pos_potential = (my_potential[BEHIND][AHEAD] + my_potential[BEHIND][TIED]/2.0 + my_potential[TIED][AHEAD]/2.0)
        except ZeroDivisionError:
            pos_potential = (my_potential[BEHIND][AHEAD] + my_potential[BEHIND][TIED]/2.0 + my_potential[TIED][AHEAD]/2.0) / (p_total[BEHIND] + p_total[TIED]/2.0 + float(1E-5))


        try:
            neg_potential = (my_potential[AHEAD][BEHIND] + (my_potential[TIED][BEHIND]/2.0) +(my_potential[AHEAD][TIED]/2.0)) / (p_total[AHEAD] + (p_total[TIED]/2.0))
        except ZeroDivisionError:
                        neg_potential = (my_potential[AHEAD][BEHIND] + (my_potential[TIED][BEHIND]/2.0) +(my_potential[AHEAD][TIED]/2.0)) / (p_total[AHEAD] + (p_total[TIED]/2.0) + float(1E-5))

        
        return [pos_potential,neg_potential]

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

        if street == 5:
            self.hands_played += 1
        
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
        stacks = [my_stack, opp_stack] #keep track of our stacks
        
        min_raise, max_raise = round_state.raise_bounds()
        my_action = None


        if my_stack - 1.5*(1000-self.hands_played) > opp_stack + (1000-self.hands_played):
            return FoldAction()


        pot_total = my_contribution + opp_contribution #total contributed at start of hand 

        if street<3: #we're preflop
            raise_amount = int(my_pip + continue_cost + 0.2*(pot_total + continue_cost))
        else:
            raise_amount = int(my_pip + continue_cost + 0.3*(pot_total + continue_cost))

        raise_amount = max([min_raise, raise_amount]) #make sure we have a valid raise
        raise_amount = min([max_raise, raise_amount])        

        raise_cost = raise_amount - my_pip #how much it costs to make that raise

        if (RaiseAction in legal_actions and (raise_cost <= my_stack)): #only consider raising if the hand we have is strong
            temp_action = RaiseAction(raise_amount)
        elif (CallAction in legal_actions and (continue_cost <= my_stack)): #only consider raising if the hand we have is strong
            temp_action = CallAction()
        elif CheckAction in legal_actions:
            temp_action = CheckAction()
        else:
            temp_action = FoldAction()

        _MONTE_CARLO_ITERS = 300
        strength = self.calc_strength(my_cards, _MONTE_CARLO_ITERS, comm = board_cards)

        if continue_cost > 0: # if opponent has bet
            self.opp_raises += 1
            _SCARY = continue_cost/pot_total * 0.15 # adjusting evaluation of opp strength by scaling relative to pot-sized bet
            
            p_strength = 0.0
            if street == 3 or street == 4:
                pos_potential, neg_potential = self.calc_potential(my_cards, board_cards)
                p_strength = strength * (1- neg_potential) + (1-strength) * pos_potential

            _SCARY = continue_cost/pot_total * 0.15 # adjusting evaluation of opp strength by scaling relative to pot-sized bet
            if p_strength != 0.0: 
                adj_strength = max([0, p_strength - _SCARY])
            else: 
                adj_strength = max([0, strength - _SCARY])
            pot_odds = continue_cost/(pot_total + continue_cost)

            if adj_strength >= pot_odds:
                if self.hands_played >= 200:
                    if self.opp_raises/self.hands_played >= 0.2 and strength > 0.8 and (street == 4 or street == 5): # exploitative all-in
                        my_action = RaiseAction(max_raise)
                        print("hello"+str(max_raise)+" "+str(self.hands_played))
                if adj_strength > 0.55 and random.random() < adj_strength:
                    my_action = temp_action
            
                else:
                    my_action = CallAction()
            else:
                my_action = FoldAction()
        
        else: # if we're first to act
            if random.random() < strength:
                my_action = temp_action
            
            else:
                my_action = CheckAction()

        return my_action
        


if __name__ == '__main__':
    run_bot(Player(), parse_args())