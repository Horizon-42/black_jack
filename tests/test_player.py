import unittest
from models.player import Player
from models.card import Card, Suit, Rank
from models.hand import PlayerHand

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.ace_clubs = Card(Suit.Clubs, Rank.ACE)
        self.ace_hearts = Card(Suit.Hearts, Rank.ACE)
        self.king_spades = Card(Suit.Spades, Rank.KING)
        self.queen_diamonds = Card(Suit.Diamonds, Rank.QUEEN)
        self.three_clubs = Card(Suit.Clubs, Rank.THREE)
        self.ten_clubs = Card(Suit.Clubs, Rank.TEN)
        self.five_hearts = Card(Suit.Hearts, Rank.FIVE)
        self.two_spades = Card(Suit.Spades, Rank.TWO)
        self.seven_diamonds = Card(Suit.Diamonds, Rank.SEVEN)
        self.nine_clubs = Card(Suit.Clubs, Rank.NINE)
        self.king_hearts = Card(Suit.Hearts, Rank.KING) # For pair testing

    def test_player_initialization(self):
        player = Player(id=1, bank_money=1000)
        self.assertEqual(player.id, 1)
        self.assertEqual(player.get_bank_amount(), 1000)
        self.assertIsNone(player._Player__hand)
        self.assertEqual(player._Player__splited_hands, [])
        self.assertEqual(player._Player__all_hands, [])
        self.assertEqual(player.get_insurance_amount(), 0)
        self.assertEqual(player._Player__main_bet, 0)

        # Test invalid initializations
        with self.assertRaises(ValueError):
            Player(id=-1, bank_money=100)
        with self.assertRaises(ValueError):
            Player(id=1, bank_money=-50)
        with self.assertRaises(ValueError):
            Player(id="abc", bank_money=100)

    def test_init_hand(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.ace_clubs, self.king_spades], 100)
        self.assertIsNotNone(player._Player__hand)
        self.assertEqual(player._Player__main_bet, 100)
        self.assertEqual(player._Player__hand.bet, 100)
        self.assertEqual(player.get_bank_amount(), 900) # Bank should be reduced by bet

        with self.assertRaises(ValueError):
            player.init_hand([self.ace_clubs, self.king_spades, self.five_hearts], 50) # More than two cards
        with self.assertRaises(TypeError):
            player.init_hand(["not a card", self.five_hearts], 50) # Not Card objects

        # Test invalid bet money
        with self.assertRaises(ValueError):
            player.init_hand([self.ace_clubs, self.king_spades], -10)
        with self.assertRaises(ValueError):
            player.init_hand([self.ace_clubs, self.king_spades], 0)
        with self.assertRaises(ValueError):
            player.init_hand([self.ace_clubs, self.king_spades], 2000) # Not enough chips

    def test_get_bank_amount(self):
        player = Player(id=1, bank_money=500)
        self.assertEqual(player.get_bank_amount(), 500)
        player.init_hand([self.two_spades, self.three_clubs], 50)
        self.assertEqual(player.get_bank_amount(), 450)

    def test_get_insurance_amount(self):
        player = Player(id=1, bank_money=500)
        self.assertEqual(player.get_insurance_amount(), 0)
        player.init_hand([self.two_spades, self.three_clubs], 100)
        player.insurance() # Insurance is 100 // 2 = 50
        self.assertEqual(player.get_insurance_amount(), 50)

    def test_has_pair(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.king_spades, self.king_hearts], 100)
        self.assertTrue(player.has_pair())

        player.reset()
        # all ten points cards are considered pairs
        player.init_hand([self.king_spades, self.queen_diamonds], 100)
        self.assertTrue(player.has_pair())

        player.reset()
        player.init_hand([self.ace_clubs, self.ace_hearts], 100)
        self.assertTrue(player.has_pair())

        player.reset()
        player.init_hand([self.five_hearts, self.two_spades], 100)
        self.assertFalse(player.has_pair())  # No pair

        player.reset()
        player.init_hand([self.five_hearts, self.seven_diamonds], 100)
        player.hit(self.five_hearts)  # Hand: 12 points, no pair
        self.assertFalse(player.has_pair())  # No hand initialized

        player.reset()
        self.assertFalse(player.has_pair()) # No hand initialized

    def test_stand(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 50) # Hand: 12 points
        
        player.stand()
        self.assertEqual(len(player._Player__all_hands), 1)
        self.assertEqual(player._Player__all_hands[0].points, 12)
        self.assertIsNone(player._Player__hand) # Current hand should be moved

        # Test standing with no current hand
        with self.assertRaises(ValueError):
            player.stand()

    def test_hit(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 50) # Hand: 12 points
        
        player.hit(self.two_spades) # Add 2
        self.assertEqual(player._Player__hand.points, 14) # 12 + 2 = 14
        self.assertEqual(len(player._Player__hand.cards), 3)

        # Test hitting with no current hand
        player.reset()
        with self.assertRaises(ValueError):
            player.hit(self.ace_clubs)
        
        # Test hitting with non-Card object
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        with self.assertRaises(TypeError):
            player.hit("not a card")

    def test_double(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.two_spades], 100) # Hand: 7 points, Bet: 100
        self.assertEqual(player.get_bet(), 100)
        # Bank: 1000 - 100 = 900
        self.assertEqual(player.get_bank_amount(), 900)

        player.double(self.nine_clubs) # Add 9. Hand: 7+9=16 points. Bet: 100+100=200
        self.assertEqual(player._Player__main_bet, 100)
        self.assertEqual(player.get_hand().points, 16)
        self.assertEqual(player.get_hand().bet, 200)
        self.assertTrue(player.get_hand().doubled)
        self.assertEqual(player.get_bank_amount(), 800) # Bank: 900 - 100 (doubled bet) = 800
        self.assertEqual(len(player._Player__all_hands), 1) # Doubling ends the hand
        self.assertIsNone(player._Player__hand) # Current hand should be moved

        # Test doubling with insufficient funds
        player.reset()
        player = Player(id=1, bank_money=50)
        player.init_hand([self.five_hearts, self.two_spades], 50) # Bank 0
        self.assertEqual(player.get_bank_amount(), 0)
        with self.assertRaises(ValueError):
            player.double(self.nine_clubs)

        # Test doubling with no current hand
        player.reset()
        with self.assertRaises(ValueError):
            player.double(self.ace_clubs)
        
        # Test doubling with non-Card object
        player.reset()
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        with self.assertRaises(TypeError):
            player.double("not a card")

    def test_split(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.king_spades, self.king_hearts], 100) # Pair of Kings, Bet: 100. Bank: 900
        self.assertEqual(player.get_bank_amount(), 900)
        self.assertEqual(len(player._Player__hand.cards), 2)

        player.split()
        self.assertEqual(len(player._Player__hand.cards), 1) # Original hand now has 1 card
        self.assertEqual(player._Player__hand.cards[0], self.king_spades)
        self.assertEqual(len(player._Player__splited_hands), 1) # One split hand created
        self.assertEqual(player._Player__splited_hands[0].cards[0], self.king_hearts)
        self.assertEqual(player._Player__splited_hands[0].bet, 100)
        self.assertEqual(player.get_bank_amount(), 800) # Bank: 900 - 100 (new bet) = 800

        # Test splitting with no pair
        player.reset()
        player.init_hand([self.king_spades, self.queen_diamonds], 100)
        with self.assertRaises(ValueError):
            player.split()

        # Test splitting with insufficient funds
        player.reset()
        player = Player(id=1, bank_money=100)
        player.init_hand([self.king_spades, self.king_hearts], 100) # Bank 0 after initial bet
        with self.assertRaises(ValueError):
            player.split()

        # Test splitting with no current hand
        player.reset()
        with self.assertRaises(ValueError):
            player.split()

    def test_insurance(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 100) # Main bet 100. Bank 900
        self.assertEqual(player.get_insurance_amount(), 0)

        player.insurance() # Insurance is 100 // 2 = 50
        self.assertEqual(player.get_insurance_amount(), 50)
        self.assertEqual(player.get_bank_amount(), 850) # Bank: 900 - 50 = 850

        # Test taking insurance again
        with self.assertRaises(ValueError):
            player.insurance()

        # Test insurance with insufficient funds
        player.reset()
        player = Player(id=1, bank_money=100)
        player.init_hand(
            [self.five_hearts, self.seven_diamonds], 100)  # Bank 0
        with self.assertRaises(ValueError):
            player.insurance()

        # Test insurance with no current hand
        player.reset()
        with self.assertRaises(ValueError):
            player.insurance()

    def test_done_with_hand(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        
        player.done_with_hand()
        self.assertEqual(len(player._Player__all_hands), 1)
        self.assertIsNone(player._Player__hand)

        # Test with split hands
        player.reset()
        player.init_hand([self.king_spades, self.king_hearts], 100)
        player.split() # Original hand (King), Split hand (King)
        
        player.done_with_hand() # Original hand moved to all_hands
        self.assertEqual(len(player._Player__all_hands), 1)
        self.assertEqual(player._Player__all_hands[0].cards[0], self.king_spades)
        self.assertIsNotNone(player._Player__hand) # Current hand should now be the split hand
        self.assertEqual(player._Player__hand.cards[0], self.king_hearts)

        player.done_with_hand() # Split hand moved to all_hands
        self.assertEqual(len(player._Player__all_hands), 2)
        self.assertIsNone(player._Player__hand) # No more hands

        # Test done with hand when no hand is initialized
        player.reset()
        with self.assertRaises(ValueError):
            player.done_with_hand()

    def test_is_all_done(self):
        player = Player(id=1, bank_money=1000)
        self.assertFalse(player.is_all_done())  # Initially done as no hands

        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        self.assertFalse(player.is_all_done()) # Has a current hand

        player.stand()
        self.assertTrue(player.is_all_done()) # Current hand moved, no splits

        player.reset()
        player.init_hand([self.king_spades, self.king_hearts], 100)
        player.split()
        self.assertFalse(player.is_all_done()) # Has current hand and a split hand

        player.done_with_hand() # First hand done
        self.assertFalse(player.is_all_done()) # Still has the split hand as current

        player.done_with_hand() # Second hand done
        self.assertTrue(player.is_all_done()) # All hands processed

    def test_get_hand(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        hand = player.get_hand()
        self.assertIsInstance(hand, PlayerHand)
        self.assertEqual(hand.points, 12)

        player.reset()
        with self.assertRaises(ValueError):
            player.get_hand() # No hand initialized

    def test_get_all_hands(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        player.stand()

        all_hands = player.get_all_hands()
        self.assertEqual(len(all_hands), 1)
        self.assertEqual(all_hands[0].points, 12)

        # Test with split hands
        player.reset()
        player.init_hand([self.king_spades, self.king_hearts], 100)
        player.split()
        player.hit(self.five_hearts) # Hit first hand (King, 5) = 15
        player.done_with_hand()
        player.hit(self.two_spades) # Hit second hand (King, 2) = 12
        player.done_with_hand()

        all_hands_split = player.get_all_hands()
        self.assertEqual(len(all_hands_split), 2)
        self.assertEqual(all_hands_split[0].points, 15)
        self.assertEqual(all_hands_split[1].points, 12)

        # Test getting all hands before all hands are done
        player.reset()
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        with self.assertRaises(ValueError):
            player.get_all_hands()

    def test_get_insurance_rate(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.ace_clubs, self.king_spades], 100)
        self.assertEqual(player.get_insurance_rate(), 0.0) # No insurance taken yet

        player.insurance() # Insurance 50, main bet 100
        self.assertEqual(player.get_insurance_rate(), 0.5)

        player.reset()
        player = Player(id=1, bank_money=1000)
        # Test before init_hand (main_bet is 0)
        self.assertEqual(player.get_insurance_rate(), 0.0)

    def test_pay_out(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.five_hearts, self.seven_diamonds], 100) # Bank 900
        player.stand() # Hand is done

        # Win (1:1 payout on main bet)
        self.assertEqual(player.get_all_bets(), 100)  # Main bet
        self.assertEqual(player.get_bank_amount(), 900)  # Bank before payout
        self.assertEqual(player.get_bank_and_bets(), 1000)  # Bank + main bet
        money_earned = player.pay_out([1.0])
        self.assertEqual(money_earned, 100) # 100 * 1.0
        self.assertEqual(player.get_bank_amount(), 1100)  # 1000 + 100

        # Loss (0 payout)
        player.reset()
        player.init_hand(
            [self.king_spades, self.queen_diamonds], 100)  # Bank 1000
        player.stand()
        money_earned = player.pay_out([0.0])
        self.assertEqual(money_earned, 0)
        self.assertEqual(player.get_bank_amount(), 1100)

        # Push (0.5 payout - original code assumed 0.5 for push, usually 1.0 for bet back)
        # Assuming 0.5 for push as per original code's `rewards` multiplier
        player.reset()
        player.init_hand([self.ten_clubs, self.nine_clubs], 100)  # Bank 1000
        player.stand()
        money_earned = player.pay_out([0.5]) # If push, bet returned, so 1.0 multiplier is standard
        self.assertEqual(money_earned, 50) # 100 * 0.5
        self.assertEqual(player.get_bank_amount(), 1150)  # 1100 + 50

        # Blackjack (1.5 payout on main bet)
        player.reset()
        player.init_hand([self.ace_clubs, self.king_spades], 100) # Bank 900
        player.stand()
        money_earned = player.pay_out([1.5]) # 100 * 1.5 = 150
        self.assertEqual(money_earned, 150)
        self.assertEqual(player.get_bank_amount(), 1300)  # 1150 + 150

        # Test with multiple hands (e.g., after split)
        player.reset()
        player.init_hand([self.king_spades, self.king_hearts], 100) # Bank 900
        player.split() # Bank 800. Hand 1 (K), Hand 2 (K)
        player.hit(self.five_hearts) # Hand 1: K, 5 (15)
        player.done_with_hand()
        player.hit(self.seven_diamonds) # Hand 2: K, 7 (17)
        player.done_with_hand()

        # Assume Hand 1 wins (1.0), Hand 2 pushes (0.5)
        # Original code used `__main_bet` for each reward.
        # This implies rewards are for the *initial* bet, not per split hand bet.
        # If rewards are for each hand's individual bet, the `pay_out` method needs adjustment.
        # Sticking to the original `__main_bet * reward` logic for now.
        money_earned = player.pay_out([1.0, 0.5]) # (100 * 1.0) + (100 * 0.5) = 100 + 50 = 150
        self.assertEqual(money_earned, 150)
        self.assertEqual(player.get_bank_amount(), 1300 + 150)

        # Test mismatch in rewards and hands
        player.reset()
        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        player.stand()
        with self.assertRaises(ValueError):
            player.pay_out([1.0, 0.5]) # One hand, two rewards

    def test_reset(self):
        player = Player(id=1, bank_money=1000)
        player.init_hand([self.ace_clubs, self.king_spades], 100)
        player.insurance()
        player.stand()
        
        player.reset()
        self.assertIsNone(player._Player__hand)
        self.assertEqual(player._Player__splited_hands, [])
        self.assertEqual(player._Player__all_hands, [])
        self.assertEqual(player._Player__insuranced, 0)
        self.assertEqual(player._Player__main_bet, 0)
        self.assertEqual(player.get_bank_amount(), 1000) # Bank returns to initial state after reset

    def test_str(self):
        player = Player(id=1, bank_money=1000)
        self.assertEqual(str(player), "Player 1, has 1000 chips left,\ncurrent hand: No current hand,\nno main bet, no insurance")

        player.init_hand([self.five_hearts, self.seven_diamonds], 50)
        self.assertEqual(str(player), "Player 1, has 950 chips left,\ncurrent hand: With 5 of Hearts, 7 of Diamonds get points: 12,\nmain bet 50, no insurance")

        player.insurance()
        self.assertEqual(str(player), "Player 1, has 925 chips left,\ncurrent hand: With 5 of Hearts, 7 of Diamonds get points: 12,\nmain bet 50, 25 insurance")

        player.stand()
        self.assertEqual(str(player), "Player 1, has 925 chips left,\ncurrent hand: No current hand,\nmain bet 50, 25 insurance")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)