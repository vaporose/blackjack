#!/usr/bin/env python


from random import shuffle


class Game:
    """Game object supplies logic for when the game is done, what happens when round begins and ends, and owns the Deck
    and Players instance objects"""

    def __init__(self, playername, decks):
        self.currentround = 0  # Used primarily
        self.deck = Deck(decks)  # Initializes the decks, taking 'decks' as the number of decks to use.
        self.players = [Player("Dealer"), Player(playername)]
        self.over = False  # Game is over when the player is out of money.

    def new_round(self):
        # In a real game the deck wouldn't be shuffled every round. However, introducing shuffling only occasionally
        # introduces more complexity than will be noticeable in the game.
        self.currentround += 1
        self.deck.shuffle()
        for player in self.players:
            player.hands.append(Hand(player, self.deck))
            # Instantiates a new hand for both the player and dealer and gives them cards
            for x in range(2):
                player.hands[0].hit()

    def player_done(self):
        """
        Check if each hand is stood
        :return: True if all hands are stood; False if not.
        """
        if all(len(hand.actions) < 1 for hand in self.players[1].hands):
            return True
        else:
            return False

    def check_winner(self):
        """
        This goes through all players except the dealer to see if they win.
        Doing it this way to render this expandable for multiple players, even though only one is implemented so far.
        :return: The messages on win_values (local variable).
        """
        win_values = {0: "lose", 1: "win", 2: "push"}
        win_messages = []
        # Check if the player has won or not
        for player in self.players[1:]:
            result = player.check_winner(self.players[0].hands[0])
            win_messages.append(win_values[result])
            if result == 1:
                player.bank += player.bet * 2
        return win_messages

    def end_round(self):
        # todo: Create logging function to record gameplay
        """
        Performs end-round cleanup by removing cards in players' hands and adding them to the deck Shoe
        """
        for player in self.players:
            for hand in player.hands:
                self.deck.shoe.extend(hand.cards)
                del hand
            player.hands.clear()
            player.bet = 0
        if self.players[1].bank <= 0:  # If the player doesn't have any money left, games is over.
            self.game_over()

    def game_over(self):
        # todo: Extend with end of game logging
        """
        Sets what occurs when the game is determined to be over.
        """
        self.over = True


class Player:
    """Represents one player. In this text-only version of the game, only one player is possible."""

    def __init__(self, name, bank=50):
        self.name = name
        self.bet = 0
        self.hands = []  # These are the hands that the player has.
        self.bank = bank  # The amount of money they start with. Eventually "bank" should be adjustable per-game.
        self.hand_held = 0  # This is used to determine which hand the player is looking at, after splitting

    def place_bet(self, player_bet, validate=False):
        """
        Determines if a bet is validate, and places it if "Validate" is not set to False.
        :param player_bet: Variable
        :param validate: If set to True, this method will only check if a bet can be made, and not place the bet.
        :return: True if bet is valid, False if bet is not valid (including type errors)
        """
        try:
            bet = int(player_bet)
            if bet <= 0 or bet > self.bank:
                raise ValueError
        except ValueError:
            print("ERROR: Invalid bet: ", player_bet, "Bet must be a number between 1 and " + str(self.bank))
            return False
        except TypeError:
            print("ERROR: Invalid bet:", player_bet, "Bet must be an integer.")
            return False
        else:
            if not validate:  # If we're not just checking to see if the bet is good, then go ahead and change things.
                self.bet += bet
                self.bank -= bet
                return True
            else:
                return True

    def switch_hands(self, hand=None):
        """
        Pick up a different hand (when hands are split)
        :param hand:  Compatibility for more than 2 hands. Hand should be the self.hands index of the new hand.
        """
        if not hand:
            if self.hand_held == 0:
                self.hand_held = 1
            else:
                self.hand_held = 0
        else:
            self.hand_held = hand

    def check_winner(self, dealer):
        """
        Checks the hand for win conditions and returns what it finds based on below:
        0 == Loss
        1 == Win
        2 == Push (loss, but used separately for recording/printing values).
        :param dealer: Instance of the dealer's hand.
        :return:
        """
        winning_hand = None
        for hand in self.hands:
            if not hand.bust and hand.value == max(hands.value for hands in self.hands):
                winning_hand = hand
        if not winning_hand:
            return 0  # If winning_hand isn't set, all hands were bust. Therefore, loss.
        elif dealer.bust or winning_hand.value > dealer.value:
            return 1  # If the dealer went bust or if player hand is higher than the dealer's hand, win.
        elif dealer.value == winning_hand.value:
            return 2  # Player pushes if neither went bust and player didn't win
        else:
            return 0  # All other permutations result in the player losing their bet and not pushing.

    # Player reprints

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


class Hand:
    """This holds values of the current cards. This will be deleted once a round is wrapped up and instantiated again
    when the round begins."""

    def __init__(self, owner, deck, name=1):
        self.name = name  # The "name" is hand 1 or 2. Probably a clunky way to use this.
        self.cards = []  # This holds Card objects
        self.owner = owner
        self.deck = deck
        self.value = 0
        self.actions = [self.hit] if self.owner.name == "Dealer" else self.check_actions()

    # General hand functions

    def check_actions(self):
        """
        Evaluates the actions the player can perform.
        :return: Returns a list of actions (methods in hand) that can be done.
        """
        actions = {"stand": self.stand, "hit": self.hit}
        if self.value > 21:
            self.stand()  # If the player is bust, go to Stand straight away
        if self.owner.place_bet(self.owner.bet, True):
            actions.update({"double": self.double})
        if len(self.cards) == 2 and self.cards[0].value == self.cards[1].value:
            actions.update({"split": self.split})
        return actions

    # Hand actions

    def stand(self):
        # todo: In UI version, make sure to retain check to determine if self.actions is empty for end of round.
        """
        Removing all actions available.
        """
        self.actions.clear()

    def hit(self):
        """
        Gets a card from the deck (necessitating the self.deck value), and adds it to self.cards. Also adds the card's
        value to self.value.
        """
        card = self.deck.deal_card()
        self.value += card.value
        if card.value == 1 and self.value + 10 <= 21:  # todo: Remove check on UI version, this should be its own funct.
            self.value += 10
        self.cards.append(card)
        if self.value > 21:  # todo: Remove on ui version?
            self.stand()

    def double(self):
        """
        Places a bet and get a card. This is validated separately in the place_bet method.
        """
        self.owner.place_bet(self.owner.bet)
        del self.actions["double"]
        self.hit()

    def split(self):
        """
        Giving a new hand, splitting the cards from the old hand and dealing a new card to each
        """
        self.owner.hands.append(Hand(self.owner, self.deck, 2))
        self.owner.hands[1].cards.append(self.cards[-1])
        self.cards.pop(-1)
        del self.actions["split"]
        for hands in self.owner.hands:
            hands.hit()

    # Hand reprint values

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "hand" + str(self.name).title()  # Gives the hand a name. Using "hand" may be dumb.


class Deck:
    """Creating a deck object. This is more accurately conceptualized as multiple decks -- however, since all the decks
    are shuffled together to create a single set of cards, it is in essence just one big mega-deck."""

    def __init__(self, num_decks):
        self.cards = []
        self.shoe = []  # Cards that have already been played.
        for deck in range(num_decks):  # For the number of decks specified, add all the cards.
            self.cards += (Card(rank, suit) for rank in range(1, 14) for suit in 'chsd')
            # chsd = list for suits (clubs, hearts, spades, diamonds).

    def shuffle(self):
        """
        Shuffles the deck. This is called in Game.new_round
        """
        shuffle(self.cards)

    def deal_card(self):
        """
        This takes the top card off the deck and returns it. It also will check if the deck is empty, and reshuffle it
        based on the cards in self.shoe
        :return: A card object
        """
        if not len(self.cards):  # If the deck doesn't have enough cards left, then reshuffle
            self.cards.extend(self.shoe)  # Add the contents of the shoe back to the deck
            self.shuffle()
            self.shoe.clear()  # Empty the shoe!
        newcard = self.cards[-1]
        self.cards.pop()
        return newcard


class Card:
    """Card objects contain its rank and suit but do nothing on their own."""
    suits = {'c': 'Clubs', 'h': 'Hearts', 's': 'Spades', 'd': 'Diamonds'}
    ranks = {1: 'Ace', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine',
             10: 'Ten', 11: 'Jack', 12: 'Queen', 13: 'King'}

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.value = rank if rank < 11 else 10  # Setting card value. Face cards (rank 11-13) are worth 10.

    # Card reprints

    def __repr__(self):
        """
        Insures that when printing a card, the card is printed as a string and not an object reference. See __str__
        :return: self.__str__()
        """
        return self.__str__()

    def __str__(self):
        """
        Whenever this object is printed, print the card name.
        :return: The card rank and suit in readable english
        """
        return "%s of %s" % (Card.ranks[self.rank], Card.suits[self.suit])

# Text-only functions (will not work with GUI)


def play_game(playername, decks):
    """This function should only be run when playing this from the command line."""
    game = Game(playername, decks)
    play_round(game, game.players[1], game.players[0])
    print("You're out of money -- game over! You lasted " + str(game.currentround - 1) + " rounds.")


def play_round(game, player, dealer):
    """
    A single round in the text version.
    :param game: Instance of the Game object. Required.
    :param player: Instance of a Player object. Required.
    :param dealer: Instance of a specific Player with the name attribute "Dealer". Required.
    :return: Exits the function when game over criteria are satisfied
    """
    get_bet(player)
    game.new_round()
    print("*"*10 + "\nRound ", game.currentround)  # Printing the round beginning.
    print("\nDealer has the", dealer.hands[0].cards[1], "showing.")  # Prints the dealer's face-up card
    play_hands(game, player)
    dealer_actions(dealer.hands[0])
    print("You " + " ".join(game.check_winner()) + ".\nNew bank: ", player.bank)
    if input("Press Y to continue or anything else to quit.") not in ("y", "Y"):
        quit(0)
    game.end_round()
    if game.over:
        return
    else:
        play_round(game, player, dealer)


def play_hands(game, player):
    """
    Prompting for player action. Until you Stand or go bust (see player_actions), you will be prompted to take action.
    :param game: Instance of Game object. Required.
    :param player: Instance of Player object. Required.
    :return: Exits the function when no actions are left.
    """
    current_hand = player.hands[player.hand_held]  # Simplifying accessing the current hand as an object and not int
    print(look_at_hand(current_hand), "\n")
    get_action(current_hand)  # Gets from the player what they want to do with the held hand
    if not len(current_hand.actions):  # If they stood, then the hand is maybe over...
        if not game.player_done():  # ... unless not ALL hands have been stood. In which case, switch to other hand.
            player.switch_hands()
        else:
            return  # If they're all done, then exit this function.
    play_hands(game, player)  # If we haven't stood yet, then continue prompting for action on this hand."""


def look_at_hand(hand):
    """
    Prints a list of cards in the player's hand.
    :param hand: Instance of a specific hand (player-only)
    :return: Newline-spaced list of cards, and the hand value.
    """
    hand_value = "\nValue: " + str(hand.value) + "\n"
    return hand_value + "\n".join(map(str, hand.cards[:]))


def dealer_actions(hand):
    """
    Dealer's action. They will only ever hit, or stand.
    :param hand: Instance of the Dealer (player object)'s hand Hand.
    """
    spacer = "\n" + "*"*30 + "\n"  # Makes the printing pretty.
    print(spacer + "Dealer reveals:\n", look_at_hand(hand))
    while hand.value < 17:
        hand.actions[0]()
    print("\nDealer's final hand: ", look_at_hand(hand), spacer)


def get_bet(player):
    """
    Getting the player's bet. This will only accept numbers, and not more than the player's bank.
    :param player: Instance of Player class.
    :return: Exits the function when the bet is retrieved and placed successfully.
    """
    entered_bet = input("Place your bet, max " + str(player.bank) + ":  (Press Q to quit)")
    if entered_bet in ("q", "Q"):  # Allows quitting while entering bet
        quit(0)
    else:
        if not player.place_bet(entered_bet):
            get_bet(player)
        else:
            return


def get_action(hand):
    """
    Retrieves available actions for the specified hand, invoking hand.actions
    :param hand: Instance of a specific Hand object. Required.
    :return: Return only when player switches hands. Otherwise, exit from function will occur when the action is done.
    """
    possible_actions = [option for option in hand.actions]
    print("You are holding hand " + str(hand.name) + ". Choose an action:\n")
    for a in possible_actions:
        print(str(possible_actions.index(a)) + ":", a.title())
    switch = ", S to switch hands)" if len(hand.owner.hands) > 1 else ")"
    print("\n (press Q to quit" + switch + "\n")
    try:
        selected_action = input("Enter 0-" + str(len(possible_actions) - 1) + ": ")
        if selected_action in ("q", "Q"):
            quit(0)
        elif selected_action in ("s", "S"):
            hand.owner.switch_hands()
            return
        action = possible_actions[int(selected_action)]
    except IndexError:
        print("Not an option. Please try again.")
    else:
        hand.actions[action]()


if __name__ == '__main__':
    play_game("Bob", 1)
