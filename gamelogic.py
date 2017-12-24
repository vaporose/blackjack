from random import shuffle


class Game:

    def __init__(self, playername, decks):
        # Below line is used primarily for results output, but can be expanded later for saving games.
        self.currentround = 1   # Starting off the game in round 1.
        self.player = Player(playername)  # Initializes the player, and gives them a name.
        self.dealer = Player()  # Initializes the dealer.
        self.deck = Deck(decks)  # Initializes the decks, taking 'decks' as the number of decks to use.
        self.allplayers = [self.dealer, self.player]  # Sets up a list of players to be able to iterate through them.
        self.over = False  # Sets whether or not the game is over.

    def new_round(self, player_bet):
        # In a real game the deck wouldn't be shuffled every round. However, introducing shuffling only occasionally
        # introduces more complexity than will be noticeable in the game.
        self.deck.shuffle()
        for player in self.allplayers:
            player.hands.append(Hand())  # Instantiates a new hand for both the player and dealer and gives them cards
            for x in range(2):
                newcard = self.deck.deal_card()
                player.hands[0].cards.append(newcard)
        self.player.place_bet(player_bet)
        if __name__ == '__main__':   # For console testing/printing, prints what's in hands.
            hand = self.player.hands[0]
            print(self.player.look_at_hand())  # Printing the player's hand.
            print("\nDealer has the", self.dealer.hands[0].cards[1])
            if hand.blackjack:
                print("Blackjack!")


class Player:

    def __init__(self, name=None):
        if not name:
            name = 'Dealer'
        self.name = name
        self.bet = 0
        self.hands = []
        self.bank = 50

    def place_bet(self, player_bet):
        self.bet = player_bet

    def __str__(self):
        return self.name

    def look_at_hand(self, hand_held=0):
        # Prints the hands for unit testing; else, returns the cards in hand (for eventual UI)
        if __name__ == '__main__':
            handname = "Your hand: " if len(self.hands) < 2 else "Hand " + str(hand_held + 1)
            return "\n" + handname + "\n" + "\n".join(map(str, self.hands[hand_held].cards[:]))

        else:
            return self.hands[hand_held].cards[:]


class Hand:

    def __init__(self):
        self.cards = []
        self.value = sum([cards.value for cards in self.cards])
        if any(cards.rank == 1 for cards in self.cards) and self.value + 10 <= 21:
            self.value += 10
        self.bust = False  # Makes the hand bust if its value is over 21
        self.pair = False
        self.blackjack = False

    def calculate_value(self):
        self.value = sum([cards.value for cards in self.cards])
        # If the hand would be less than 21, makes aces worth 11.
        if any(cards.rank == 1 for cards in self.cards) and self.value + 10 <= 21:
            self.value += 10
        if self.value > 21:
            self.bust = True
        if len(self.cards) == 2:
            if any(cards.value == 10 for cards in self.cards) and any(cards.rank == 1 for cards in self.cards):
                self.blackjack = True
            if self.cards[0].value == self.cards[1].value:
                self.pair = True
        return self.value


class Deck:
    """Creating a deck object. This is more accurately conceptualized as multiple decks -- however, since all the decks
    are shuffled together to create a single set of cards, it is in essence just one big mega-deck."""

    def __init__(self, num_decks):
        self.cards = []
        for deck in range(num_decks):  # For the number of decks specified, add all the cards.
            self.cards += (Card(rank, suit) for rank in range(1, 14) for suit in 'chsd')
            # chsd = list for suits (clubs, hearts, spades, diamonds).

    def shuffle(self):
        #  Shuffles the deck. This is called in Game.new_round
        shuffle(self.cards)

    def deal_card(self):
        newcard = self.cards[-1]
        self.cards.pop()
        return newcard


class Card:
    suits = {'c': 'Clubs', 'h': 'Hearts', 's': 'Spades', 'd': 'Diamonds'}
    ranks = {1: 'Ace', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine',
             10: 'Ten', 11: 'Jack', 12: 'Queen', 13: 'King'}

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.value = rank if rank < 11 else 10  # Setting card value. Face cards (rank 11-13) are worth 10.

    def __repr__(self):
        return self.__str__()
        # Insures that when printing a card, the card is printed as a string and not an object. See __str__ below.

    def __str__(self):
        # Whenever this object is printed, print the card name.
        return "%s of %s" % (Card.ranks[self.rank], Card.suits[self.suit])


if __name__ == '__main__':
    game = Game('Bob', 2)
    while not game.over:
        print("Round ", game.currentround)  # Printing the round beginning.
        while True:  # Getting the player's bet. This will only accept numbers, and not more than the player's bank.
            try:
                bet = int(input("Place your bet. Cannot exceed " + str(game.player.bank) + ".  "))
            except ValueError:
                print("Bet must be a number!")
                continue
            if bet > game.player.bank:
                print("Can't bet more than you have!")
                continue
            else:
                break
        game.new_round(bet)
        break
