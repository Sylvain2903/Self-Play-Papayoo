import random as rand


'''Suit identification (iden)'''
'''  0 : payoo '''
'''  1 : clubs  '''
'''  2 : hearts  '''
'''  3 : spades  '''
'''  4 : diamonds  '''

payoo = 0
clubs = 1
hearts = 2
spades = 3
diamonds = 4
suits = ["p", "c", "h", "s", "d"]

numSuits = 5
minRank = 1
maxRank = 10


class Card:
    def __init__(self, rank, suit):
        self.rank = Rank(rank)
        self.suit = Suit(suit)

    def __lt__(self, other):
        return self.suit < other.suit or (self.suit == other.suit and self.rank < other.rank)

    def __ge__(self, other):
        return not (self < other)

    def __gt__(self, other):
        return self.rank > other.rank or (self.rank == other.rank and self.suit > other.suit)

    def __le__(self, other):
        return not (self > other)

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __ne__(self, other):
        return not (self == other)

    def rank(self):
        return self.rank

    def suit(self):
        return self.suit

    def __str__(self):
        return self.rank.__str__() + self.suit.__str__()


class Suit:
    def __init__(self, iden):
        self.iden = iden
        self.string = ''
        if iden == -1:
            self.string = "Unset"
        elif iden <= 4:
            self.string = suits[iden]
        else:
            print('Invalid card identifier')

    def __eq__(self, other):
        return self.iden == other.iden

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.iden < other.iden

    def __gt__(self, other):
        return self.iden > other.iden

    def __ge__(self, other):
        return not (self < other)

    def __le__(self, other):
        return not (self > other)

    def __str__(self):
        return self.string


"""Ranks indicated by numbers 1-10 for standard suits, and 1-20 for payoo"""


class Rank:
    def __init__(self, rank):
        self.rank = rank
        if 1 <= rank <= 20:
            self.string = str(rank)
        else:
            print('Invalid rank identifier')

    def __lt__(self, other):
        return self.rank < other.rank

    def __ge__(self, other):
        return not (self < other)

    def __gt__(self, other):
        return self.rank > other.rank

    def __le__(self, other):
        return not (self > other)

    def __eq__(self, other):
        return self.rank == other.rank

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return self.string


class Hand:
    def __init__(self):
        self.hand = []

    def size(self):
        return len(self.hand)

    def add_card(self, card):
        self.hand.append(card)

    def sort(self):
        self.hand.sort()

    def get_random_card(self):
        temp = rand.randint(0, self.size())
        card = self.hand[temp]
        return card

    @classmethod
    def str2card(cls, str_card):
        if len(str_card) == 0:
            return None

        suit = str_card[len(str_card)-1].lower()  # get the suit from the string
        try:
            suit_iden = suits.index(suit)
        except Exception as e:
            print('Invalid suit')
            print(e)
            return None

        card_rank = str_card[0:len(str_card)-1]  # get rank from string
        try:
            card_rank = card_rank.upper()
        except AttributeError:
            pass

        return Card(card_rank, suit_iden)

    def contains_card(self, card):
        for c in self.hand:
            if c.__eq__(card):
                return 1
        return 0

    def play_card(self, card_rank, suit_iden):
        card = Card(card_rank, suit_iden)
        for c in self.hand:
            if c.__eq__(card):
                return card
        return None

    def remove_card(self, card):
        if self.contains_card(card):
            self.hand.remove(card)

    def has_suit(self, suit):
        for c in self.hand:
            if c.suit == suit:
                return True
        return False

    def __str__(self):
        string = ''
        for card in self.hand:
            string += card.__str__() + ' '
        return string


class Deck:
    def __init__(self):
        self.deck = []
        for suit in range(0, numSuits):
            for rank in range(minRank, maxRank+1):
                self.deck.append(Card(rank, suit))
        for rank in range(11, 21):
            self.deck.append(Card(rank, 0))

    def __str__(self):
        deck_str = ''
        for card in self.deck:
            deck_str += card.__str__() + '\n'
        return deck_str

    def shuffle(self):
        rand.shuffle(self.deck, rand.random)

    def deal(self):
        return self.deck.pop(0)

    def sort(self):
        self.deck.sort()

    def size(self):
        return len(self.deck)


class Player:
    def __init__(self, index):
        self.index = index
        self.hand = Hand()
        self.score = 0
        self.cards_collected = []

    def add_card(self, card):
        self.hand.add_card(card)
        if self.hand.size() == 15:
            self.hand.sort()

    def play(self, card):
        if self.hand.contains_card(card):
            self.hand.remove_card(card)

    def has_suit(self, suit):
        return self.hand.has_suit(suit)

    def remove_card(self, card):
        self.hand.remove_card(card)

    def collected_card(self, card):
        for c in self.cards_collected:
            if c == card:
                return 1
        return 0

    def reset(self):
        self.score = 0
        self.cards_collected = []


class Trick:
    def __init__(self):
        card = Card(1, -1)
        self.trick = [card] * 4
        self.suit = Suit(-1)
        self.num_cards_in_trick = 0
        self.highest = 0
        self.winner = -1

    def reset(self):
        card = Card(1, -1)
        self.trick = [card, card, card, card]
        self.suit = Suit(-1)
        self.num_cards_in_trick = 0
        self.highest = 0
        self.winner = -1

    def set_trick_suit(self, card):
        self.suit = card.suit

    def add_card(self, card, index):
        if self.num_cards_in_trick == 0:  # if this is the first card added, set the trick suit
            self.set_trick_suit(card)
        self.trick[index] = card
        self.num_cards_in_trick += 1

        if card.suit == self.suit:
            if card.rank.rank > self.highest:
                self.highest = card.rank.rank
                self.winner = index

    def __str__(self):
        string = ''
        for card in self.trick:
            string += card.__str__() + ' '
        return string

