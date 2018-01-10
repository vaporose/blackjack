#!/usr/bin/env python3


from random import shuffle


class Game:

    def __init__(self, playername, decks):
        # Below line is used primarily for results output, but can be expanded later for saving games.
        self.currentround = 1   # Starting off the game in round 1.
        self.player = Player(playername)
        self.dealer = Player("Dealer")
        self.deck = Deck(decks)  # Initializes the decks, taking 'decks' as the number of decks to use.
        self.allplayers = [self.dealer, self.player]  # Sets up a list of players to be able to iterate through them.
        self.over = False  # Sets whether or not the game is over.

    def new_round(self):
        # In a real game the deck wouldn't be shuffled every round. However, introducing shuffling only occasionally
        # introduces more complexity than will be noticeable in the game.
        self.deck.shuffle()
        for player in self.allplayers:
            player.hands.append(Hand())  # Instantiates a new hand for both the player and dealer and gives them cards
            for x in range(2):
                newcard = self.deck.deal_card()
                player.hands[0].cards.append(newcard)
                if x == 1:
                    player.hands[0].calculate_value()

    def player_actions(self, hand, action="stand"):
        if action == "hit" or action == "double":
            hand.cards.append(self.deck.deal_card())
            hand.calculate_value()
            if hand.bust:
                hand.actions_taken.append("stand")
        if action == "double":
            hand.actions_taken.append(action)
            self.player.bet += self.player.bet*2
        if action == "split":
            # Giving a new hand, splitting the cards from the old hand and dealing a new card to each
            self.player.hands.append(Hand(2))
            self.player.hands[1].cards.append(hand.cards[-1])
            hand.cards.pop(-1)
            for hands in self.player.hands:
                hands.cards.append(self.deck.deal_card())
                hands.calculate_value()
            hand.actions_taken.append(action)
        if action == "stand":
            hand.actions_taken.append(action)

    def player_done(self):
        # Check if each hand is stood
        if all(hand.check_actions("stand") for hand in self.player.hands):
            return True
        else:
            return False

    def end_round(self):
        pass


class Player:

    def __init__(self, name, bank=50):
        self.name = name
        self.bet = 0
        self.hands = []  # These are the hands that the player has.
        self.bank = bank  # The amount of money they start with. Eventually "bank" should be adjustable per-game.
        self.hand_held = 0  # This is used to determine which hand the player is looking at, after splitting

    def place_bet(self, player_bet):
        self.bet = player_bet

    def __str__(self):
        return self.name

    def look_at_hand(self, hand):
        # Prints the hands for play when running the script; else, returns the cards in hand (for eventual UI)
        if __name__ == '__main__':  # Get rid of this mess later
            if self.name == "Dealer":
                hand_name = self.name.title() + "'s hand: "
            else:
                hand_name = "Your hand: " if len(self.hands) < 2 else "Hand " + str(hand.name) + ": "
            hand_value = " " + str(hand.value) + "\n"
            return "\n" + hand_name + hand_value + "\n".join(map(str, hand.cards[:]))

        else:
            return hand.cards[:]

    def switch_hands(self):  # Pick up a different hand (when hands are split)
        if self.hand_held == 0:
            self.hand_held = 1
        else:
            self.hand_held = 0

    def double_check(self):
        # This will do nothing but check whether or not a double is legal
        if self.bet * 2 <= self.bank:
            return True
        else:
            return False


class Hand:
    """This holds values of the current cards. This will be deleted once a round is wrapped up and instantiated again
    when the round begins."""

    def __init__(self, name=1):
        self.name = name  # The "name" is hand 1 or 2. Probably a clunky way to use this.
        self.cards = []  # This holds Card objects
        self.value = 0
        self.bust = False  # Makes the hand bust if its value is over 21
        self.pair = False  # A "pair" are two cards of the same value (gotten from calculate_value)
        self.blackjack = False
        self.actions_taken = []  # The once-only actions the hand has taken this round (double, hit, stand).

    def calculate_value(self):
        self.value = sum([cards.value for cards in self.cards])
        if any(cards.rank == 1 for cards in self.cards) and self.value + 10 <= 21:
            self.value += 10  # If hand.value would be less than 21, makes aces worth 11 instead of 1.
        if self.value > 21:
            self.bust = True
        if len(self.cards) == 2:
            if any(cards.value == 10 for cards in self.cards) and any(cards.rank == 1 for cards in self.cards):
                self.blackjack = True
            if self.cards[0].value == self.cards[1].value:
                self.pair = True
        return self.value

    def check_actions(self, action=None):
        # Returns the length of actions_taken if no action is passed to it.
        if not action:
            return len(self.actions_taken)
        else:  # Determines if the action specified has already been taken
            if action in self.actions_taken:
                return True
            else:
                return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "hand" + str(self.name).title()  # Gives the hand a name. Using "hand" may be dumb.


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
        # Insures that when printing a card, the card is printed as a string and not an object reference. See __str__

    def __str__(self):
        # Whenever this object is printed, print the card name.
        return "%s of %s" % (Card.ranks[self.rank], Card.suits[self.suit])


def play_game():
    """This function should only be run when playing this from the command line. Replace game with variables once out of
    testing and ready for command line release"""
    game = Game('Bob', 2)
    while True:
        print("Round ", game.currentround)  # Printing the round beginning.
        game.new_round()
        game.player.place_bet(get_bet(game.player.bank))
        print("\nDealer has the", game.dealer.hands[0].cards[1], "showing.")  # Prints the dealer's face-up card
        play_hands(game, game.player)
        dealer_actions(game, game.dealer, game.dealer.hands[0])
        break


def play_hands(game, player):
    # Until you Stand or go bust (see player_actions), you will be prompted to take action.
    current_hand = player.hands[player.hand_held]  # Simplifying accessing the current hand as an object and not int
    print(player.look_at_hand(current_hand), "\n")
    action = get_action(player, current_hand)  # Gets from the player what they want to do with the held hand
    if action == "switch":  # Allows player to switch hands, assuming they have previously split hands.
        player.switch_hands()
        print(player.look_at_hand(current_hand), "\n")
    else:
        game.player_actions(current_hand, action)  # Does the specified action, if it wasn't "switch" or quit.
        print(player.look_at_hand(current_hand), "\n")
    if current_hand.check_actions("stand"):  # If they stood, then the hand is maybe over...
        if not game.player_done():  # ... unless not ALL hands have been stood. In which case, switch to other hand.
            player.switch_hands()
        else:
            return  # If they're all done, then exit this function.
    play_hands(game, player)  # If we haven't stood yet, then continue prompting for action on this hand.


def dealer_actions(game, player, hand):
    print("Dealer reveals:\n", player.look_at_hand(hand))
    while hand.value < 16:
        game.player_actions(hand, "hit")
    print(player.look_at_hand(hand))


def get_bet(bank):
    while True:  # Getting the player's bet. This will only accept numbers, and not more than the player's bank.
        entered_bet = input("Place your bet, max " + str(bank) + ":  (Press Q to quit)")
        quit_game(entered_bet)  # Did they press q / Q? Then quit.
        try:
            bet = int(entered_bet)
        except ValueError:
            print("Bet must be a number!")
            continue
        if bet > bank:
            print("Can't bet more than you have!")
            continue
        else:
            break
    return bet


def get_action(player, hand):
    # This is retrieving an action from the player (text only).
    possible_actions = ["stand", "hit"]
    if not hand.check_actions("double") and player.double_check():
        possible_actions.append("double")
    if not hand.check_actions("split") and hand.name == 1:  # Re-implement "and hand.pair:" when done testing splits
        possible_actions.append("split")
    print("You are holding hand " + str(hand.name) + ". Choose an action or press 'S' to switch hands, 'Q' to quit.\n")
    for option in possible_actions:
        print(possible_actions.index(option), ")", option.title())
    action = None
    try:
        selected_action = input("\nEnter 0-" + str(len(possible_actions)-1) + ": ")
        quit_game(selected_action)
        if selected_action == 'S' or selected_action == 's':
            return "switch"
        action = possible_actions[int(selected_action)]
    except IndexError:
        print("Not an option. Please try again.")
    hand.actions_taken.append(action)
    return action


def quit_game(got_key):
    # Quit function. This will probably be removed once we go to a GUI.
    if got_key == "q" or got_key == "Q":
        quit(0)


if __name__ == '__main__':
    play_game()
