import eval7


def gen_possible_hands(hole, comm = None):

    deck = eval7.Deck() # deck of cards
    hole_cards = [eval7.Card(card) for card in hole]
    for hole_card in hole_cards:
        deck.remove(hole_card)


    if not comm: # if there are community cards
        comm_cards = [eval7.Card(Card) for card in comm]
        for comm_card in comm_cards:
            deck.remove(comm_card)

    possible_hands = []

    # generating len(deck) choose 2 possible pairings
    for first_card in range(len(deck)):
        for second_card in range(first_card+1,len(deck)):
            possible_hands.append([deck[first_card],deck[second_card]])

    return possible_hands



def gen_possible_boards(hole, opp_hole, comm):
    """
    Only use at flop or turn
    """

    deck = eval7.Deck()
    comm_cards = [eval7.Card(card) for card in comm]

    for card in hole+opp_hole+comm:
        deck.remove(eval7.Card(card))


    possible_boards = []

    if len(comm) == 3:
        for turn in range(len(deck)):
            for river in range(turn+1, len(deck)):
                possible_boards.append(comm_cards+[deck[turn],deck[river]])
    
    elif len(comm) == 4:
        for river in deck:
            possible_boards.append(comm_cards+river)

    return possible_boards