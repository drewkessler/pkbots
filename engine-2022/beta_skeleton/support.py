import eval7
import numpy as np


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








def get_mean_strength_from_range(opp_range_mapping):
    """
    Getting median strength value from the opp_range_mapping
    """

    strengths = np.array(opp_range_mapping.values())
    return np.mean(strengths)

if __name__ == "__main__":
    opp_range = gen_possible_hands(["As","Ad"],comm=["Ks","Ah","Ac"],cleared_hands=[["Ac","Ah"]])
    print(opp_range)
    our_hand = ["As","Ad"]
    print(calc_strength_against_range(our_hand,100,opp_range=opp_range))    



