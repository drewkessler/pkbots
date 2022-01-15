import eval7
import numpy as np
import pandas as pd


def gen_possible_hands(hole, comm = None, cleared_hands = []):
    """
    Generates all possible hands that the opp could have, given the community cards
    and our estimate of what cards they don't have
    Returns list of Cards in str format
    """

    deck = eval7.Deck() # deck of cards
    hole_cards = [eval7.Card(card) for card in hole]
    for hole_card in hole_cards:
        deck.cards.remove(hole_card)


    if comm: # if there are community cards
        comm_cards = [eval7.Card(card) for card in comm]
        for comm_card in comm_cards:
            deck.cards.remove(comm_card)

    possible_hands = []

    # generating len(deck) choose 2 possible pairings
    for first_card in range(len(deck)):
        for second_card in range(first_card+1,len(deck)):
            possible_hands.append([deck[first_card],deck[second_card]])

    preclearing_str_possible_hands = []

    for hand in possible_hands:
        str_hand = str(hand)
        split = str_hand.split('(')
        str_hand = [split[1][1:3],split[2][1:3]]
        preclearing_str_possible_hands.append(str_hand)
    
    if cleared_hands == []:
        return preclearing_str_possible_hands
    

    str_possible_hands = []
    for str_hand in preclearing_str_possible_hands:
        adding = True
        for cleared_hand in cleared_hands:
            if set(str_hand) == set(cleared_hand): # if the hand has been cleared by our range estimate, using set objects to check for diff orders
                adding = False
        
        if adding:
            str_possible_hands.append(str_hand)
    

    return str_possible_hands



def get_preflop_strength(hole,data):
    """
    retrieving precomputed preflop strength
    """

    key = hole_list_to_key(hole)

    return data[key]

def hole_list_to_key(hole):
            '''
            Converts a hole card list into a key that we can use to query our 
            strength dictionary
            hole: list - A list of two card strings in the engine's format (Kd, As, Th, 7d, etc.)
            '''
            card_1 = hole[0] #get all of our relevant info
            card_2 = hole[1]

            rank_1, suit_1 = card_1[0], card_1[1] #card info
            rank_2, suit_2 = card_2[0], card_2[1]

            numeric_1, numeric_2 = self.rank_to_numeric(rank_1), self.rank_to_numeric(rank_2) #make numeric

            suited = suit_1 == suit_2 #off-suit or not
            suit_string = 's' if suited else 'o'

            if numeric_1 >= numeric_2: #keep our hole cards in rank order
                return rank_1 + rank_2 + suit_string
            else:
                return rank_2 + rank_1 + suit_string


    
def rank_to_numeric(rank):
        '''
        Method that converts our given rank as a string
        into an integer ranking
        rank: str - one of 'A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2'
        '''
        if rank.isnumeric(): #2-9, we can just use the int version of this string
            return int(rank)
        elif rank == 'T': #10 is T, so we need to specify it here
            return 10
        elif rank == 'J': #Face cards for the rest of them
            return 11
        elif rank == 'Q':
            return 12
        elif rank == 'K':
            return 13
        else: #Ace (A) is the only one left, give it the highest rank
            return 14


def calc_strength(hole, iters, community = []):
        ''' 
        Using MC with iterations to evalute hand strength 
        Args: 
        hole - our hole carsd 
        iters - number of times we run MC 
        community - community cards

        returns float of win rate
        '''

        deck = eval7.Deck() # deck of cards
        hole_cards = [eval7.Card(card) for card in hole] # our hole cards in eval7 friendly format

        if community != []:
            community_cards = [eval7.Card(card) for card in community]
            for card in community_cards: #removing the current community cards from the deck
                deck.cards.remove(card)



        for card in hole_cards: #removing our hole cards from the deck
            deck.cards.remove(card)
        
        
        
        score = 0 

        for _ in range(iters): # MC the probability of winning
            deck.shuffle()

            _COMM = 5 - len(community)
            _OPP = 2 

            draw = deck.peek(_COMM + _OPP)  
            
            opp_hole = draw[:_OPP]
            alt_community = draw[_OPP:]

            
            if community == []:
                our_hand = hole_cards  + alt_community
                opp_hand = opp_hole  + alt_community
            else: 

                our_hand = hole_cards + community_cards + alt_community
                opp_hand = opp_hole + community_cards + alt_community


            our_hand_value = eval7.evaluate(our_hand)
            opp_hand_value = eval7.evaluate(opp_hand)

            if our_hand_value > opp_hand_value:
                score += 2 

            if our_hand_value == opp_hand_value:
                score += 1 

            else: 
                score += 0        

        hand_strength = score/(2*iters) # win probability 

        return hand_strength





def calc_strength_against_range(hole, iters, community = [], opp_range = []):
    """
    Calculates strength against a range of hands the opponent could have

    Returns float of win rate
    """
        

    total_score = 0.0
    if opp_range == []:
        opp_range = gen_possible_hands(hole,comm = community)
    for opp_hand in opp_range:


        deck = eval7.Deck() # deck of cards
        hole_cards = [eval7.Card(card) for card in hole] # our hole cards

        if community != []:
            community_cards = [eval7.Card(card) for card in community]
            for card in community_cards: #removing the current community cards from the deck
                deck.cards.remove(card)



        for card in hole_cards: #removing our hole cards from the deck
            deck.cards.remove(card)


        opp_hole_cards = [eval7.Card(card) for card in opp_hand]
        for card in opp_hole_cards: #removing expected opp hole cards from deck
            deck.cards.remove(card)


        score = 0
        for _ in range(iters): # MC the probability of winning
            deck.shuffle()

            _COMM = 5 - len(community)

            draw = deck.peek(_COMM)  
            alt_community = draw

            
            if community == []:
                our_hand = hole_cards  + alt_community
                opp_hand = opp_hole_cards  + alt_community
            else: 

                our_hand = hole_cards + community_cards + alt_community
                opp_hand = opp_hole_cards + community_cards + alt_community


            our_hand_value = eval7.evaluate(our_hand)
            opp_hand_value = eval7.evaluate(opp_hand)

            if our_hand_value > opp_hand_value:
                score += 2 

            elif our_hand_value == opp_hand_value:
                score += 1 

            else: 
                score += 0        

        hand_strength = score/(2*iters) # win probability for this opp_hole
        total_score += hand_strength 

    total_hand_strength = total_score / len(opp_range)
    return total_hand_strength



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




def get_mean_strength_from_range(opp_range_mapping):
    """
    Getting mean strength value from the opp_range_mapping
    """

    strengths = np.array(opp_range_mapping.values())
    return np.mean(strengths)




def get_std_of_range_strengths(opp_range_mapping):
    """
    Getting standard deviation of strengths from an opponent's range
    """

    strengths = np.array(opp_range_mapping.values())
    return np.std(strengths)


if __name__ == "__main__":
    opp_range = gen_possible_hands(["As","Ad"],comm=["Ks","Ah","Ac"],cleared_hands=[["Ac","Ah"]])
    print(opp_range)
    our_hand = ["As","Ad"]
    print(calc_strength_against_range(our_hand,100,opp_range=[["Ac","Kh"]]))    



