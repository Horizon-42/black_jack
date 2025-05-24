import unittest
from models.card import Card, Suit, Rank
from models.dealer import Dealer
from models.deck import Deck


class MockDeck(Deck):
    def __init__(self, cards_to_deal=None):
        if cards_to_deal is None:
            cards_to_deal = []
        self.cards = cards_to_deal

    def deal_card(self):
        if self.cards:
            return self.cards.pop(0)
        raise ValueError("No more cards to deal")
class TestDealer(unittest.TestCase):

    def setUp(self):
        self.ace_clubs = Card(Suit.Clubs, Rank.ACE)
        self.ace_hearts = Card(Suit.Hearts, Rank.ACE)
        self.ace_spades = Card(Suit.Spades, Rank.ACE)
        self.king_spades = Card(Suit.Spades, Rank.KING)
        self.queen_diamonds = Card(Suit.Diamonds, Rank.QUEEN)
        self.ten_clubs = Card(Suit.Clubs, Rank.TEN)
        self.five_hearts = Card(Suit.Hearts, Rank.FIVE)
        self.two_spades = Card(Suit.Spades, Rank.TWO)
        self.seven_diamonds = Card(Suit.Diamonds, Rank.SEVEN)
        self.nine_clubs = Card(Suit.Clubs, Rank.NINE)
        self.three_clubs = Card(Suit.Clubs, Rank.THREE)
        self.four_diamonds = Card(Suit.Diamonds, Rank.FOUR)
        self.six_hearts = Card(Suit.Hearts, Rank.SIX)

    def test_init_hand(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.five_hearts])
        
        # Check hidden card and face-up card
        self.assertEqual(dealer.get_hiden_card(), self.king_spades)
        self.assertEqual(dealer.get_hand_length(), 1)
        self.assertEqual(dealer.get_face_card(), self.five_hearts)
        self.assertEqual(dealer.get_face_point(), 5)
        self.assertFalse(dealer.is_blackjack()) # Not a blackjack yet as hidden card isn't revealed
        self.assertFalse(dealer.is_bust())

        # Test invalid initializations
        with self.assertRaises(ValueError):
            dealer.init_hand([self.king_spades]) # Not two cards
        with self.assertRaises(ValueError):
            dealer.init_hand([self.king_spades, self.five_hearts, self.ten_clubs]) # More than two cards
        with self.assertRaises(ValueError):
            dealer.init_hand(["not a card", self.five_hearts]) # Not Card objects

    def test_hits_stand_on_hard_17_or_more(self):
        # Dealer has 17 (hard) - should stand
        dealer = Dealer()
        dealer.init_hand([self.ten_clubs, self.seven_diamonds]) # Hidden 10, Face-up 7
        # Card to deal if hits
        mock_deck = MockDeck(cards_to_deal=[self.two_spades])
        
        dealer.hits(mock_deck)
        self.assertEqual(dealer.reveal_hand(), 17) # 10 + 7 = 17
        self.assertEqual(dealer.get_hand_length(), 2) # No extra cards dealt
        self.assertIsNone(dealer._Dealer__hiden_card) # Hidden card revealed

        # Dealer has 18 - should stand
        dealer.reset()
        dealer.init_hand([self.ten_clubs, self.ace_hearts]) # Hidden 10, Face-up A. After hits, 10+A=21.
        mock_deck = MockDeck(cards_to_deal=[self.two_spades])
        dealer.hits(mock_deck)
        self.assertEqual(dealer.reveal_hand(), 21)
        self.assertEqual(dealer.get_hand_length(), 2)
        self.assertIsNone(dealer._Dealer__hiden_card)

    def test_hits_stand_on_soft_17_default(self):
        # Dealer has soft 17 - should stand by default (hit_soft17=False)
        dealer = Dealer()
        dealer.init_hand([self.ace_clubs, self.six_hearts]) # Hidden A, Face-up 6. After hits, A+6=17 (soft).
        # Card to deal if hits
        mock_deck = MockDeck(cards_to_deal=[self.two_spades])
        
        dealer.hits(mock_deck)
        self.assertEqual(dealer.reveal_hand(), 17)
        self.assertEqual(dealer.get_hand_length(), 2)
        self.assertIsNone(dealer._Dealer__hiden_card)

    def test_hits_hit_on_soft_17_when_true(self):
        # Dealer has soft 17 - should hit when hit_soft17=True
        dealer = Dealer()
        dealer.init_hand([self.ace_clubs, self.six_hearts]) # Hidden A, Face-up 6. After hits, A+6=17 (soft).
        # Deals 2, then 3 if needed
        mock_deck = MockDeck(cards_to_deal=[self.two_spades, self.three_clubs])
        
        dealer.hits(mock_deck, hit_soft17=True)
        # Initial: A(11), 6 = 17 (soft)
        # Hits: A(11), 6, 2 = 19 (soft)
        self.assertEqual(dealer.reveal_hand(), 19)
        self.assertEqual(dealer.get_hand_length(), 3) # Should have hit one more card
        self.assertIsNone(dealer._Dealer__hiden_card)

        # Test hitting multiple times until stand
        dealer.reset()
        dealer.init_hand([self.ace_clubs, self.two_spades]) # Hidden A, Face-up 2. After hits, A+2=13.
        mock_deck = MockDeck(cards_to_deal=[
                             self.four_diamonds, self.three_clubs, self.five_hearts])  # Deals 4, then 3, then 5
        # A,2 (13) -> hits 4 (17 soft) -> hits 3 (20 hard) -> stands
        dealer.hits(mock_deck, hit_soft17=True)
        self.assertEqual(dealer.reveal_hand(), 20)
        self.assertEqual(dealer.get_hand_length(), 4) # A,2,4,3
        self.assertIsNone(dealer._Dealer__hiden_card)

    def test_hits_bigger17_bust_scenario(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.ten_clubs]) # Hidden K, Face-up 10. After hits, K+10=20.
        self.assertEqual(dealer.get_face_point(), 10)  # Before hitting
        mock_deck = MockDeck(cards_to_deal=[self.five_hearts])  # Deals 5
        
        dealer.hits(mock_deck)
        # because K(10) + 10(10) >17, should not hit again
        self.assertEqual(dealer.reveal_hand(), 20)
        self.assertFalse(dealer.is_bust())
        self.assertEqual(dealer.get_hand_length(), 2)
        self.assertIsNone(dealer._Dealer__hiden_card)

    def test_hits_bust_scenario(self):
        dealer = Dealer()
        # Hidden K, Face-up 2. After hits, K+2=12.
        dealer.init_hand([self.king_spades, self.two_spades])
        self.assertEqual(dealer.get_face_point(), 2)  # Before hitting
        mock_deck = MockDeck(
            # Deals 5, then 6
            cards_to_deal=[self.four_diamonds, self.six_hearts])
        dealer.hits(mock_deck)  # K(10) + 2(2) + 4(4) + 6(6) = 22
        self.assertTrue(dealer.is_bust())
        # K(10) + 2(2) + 4(4) + 6(6) = 22
        self.assertEqual(dealer.reveal_hand(), 22)
        self.assertEqual(dealer.get_hand_length(), 4)  # K, 2, 4, 6
        # Hidden card should be revealed
        self.assertIsNone(dealer._Dealer__hiden_card)

    def test_is_black_jack_initial_reveal(self):
        # True case
        dealer = Dealer()
        dealer.init_hand([self.ace_clubs, self.king_spades]) # Hidden A, Face-up K
        dealer.hits(Deck()) # Reveals hidden card, now 21
        self.assertTrue(dealer.is_black_jack())

        # False case (not 21)
        dealer.reset()
        dealer.init_hand([self.ten_clubs, self.five_hearts]) # Hidden 10, Face-up 5
        dealer.hits(Deck())
        self.assertFalse(dealer.is_black_jack())

        # False case (hidden card still present - before hits is called)
        dealer.reset()
        dealer.init_hand([self.ace_clubs, self.king_spades])
        self.assertFalse(dealer.is_black_jack()) # Hidden card still exists

    def test_reveal_hand(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.five_hearts]) # Hidden K, Face-up 5
        self.assertEqual(dealer.get_face_point(), 5) # Before reveal

        revealed_points = dealer.reveal_hand()
        self.assertEqual(revealed_points, 15) # K(10) + 5 = 15
        self.assertIsNone(dealer._Dealer__hiden_card) # Hidden card should be gone

        # Calling reveal_hand again should return the same points and not add card again
        revealed_points_again = dealer.reveal_hand()
        self.assertEqual(revealed_points_again, 15)
        self.assertEqual(dealer.get_hand_length(), 2) # Should still be 2 cards

    def test_get_face_point(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.five_hearts]) # Hidden K, Face-up 5
        self.assertEqual(dealer.get_face_point(), 5)

        dealer.reset()
        dealer.init_hand([self.ace_clubs, self.ten_clubs]) # Hidden A, Face-up 10
        self.assertEqual(dealer.get_face_point(), 10)

        # Test before init_hand is called
        dealer_uninitialized = Dealer()
        with self.assertRaises(ValueError):
            dealer_uninitialized.get_face_point()

    def test_is_bust(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.queen_diamonds]) # Hidden K, Face-up Q
        mock_deck = MockDeck(cards_to_deal=[self.five_hearts])  # Deals 5
        dealer.hits(mock_deck)  # won't hit again as K(10) + Q(10) = 20
        self.assertFalse(dealer.is_bust())

        dealer.reset()
        dealer.init_hand([self.five_hearts, self.seven_diamonds]) # Hidden 5, Face-up 7
        # 5 + 7 + 9 = 21
        dealer.hits(MockDeck(cards_to_deal=[self.nine_clubs]))
        self.assertFalse(dealer.is_bust())

        dealer.reset()
        dealer.init_hand([self.king_spades, self.two_spades])
        # K(10) + 2(2) + 4(4) + 6(6) = 22
        dealer.hits(
            MockDeck(cards_to_deal=[self.four_diamonds, self.six_hearts]))
        self.assertTrue(dealer.is_bust())  # Should be bust now

        # Test before init_hand is called
        dealer_uninitialized = Dealer()
        with self.assertRaises(ValueError):
            dealer_uninitialized.is_bust()

    def test_is_blackjack_general(self):
        # This tests the second `is_blackjack` method in Dealer, which calls Hand's `is_blackjack`.
        # True case (after initial setup and reveal)
        dealer = Dealer()
        dealer.init_hand([self.ace_clubs, self.king_spades]) # Hidden A, Face-up K
        dealer.hits(Deck()) # Reveals hidden card
        self.assertTrue(dealer.is_blackjack())

        # False case (not 21)
        dealer.reset()
        dealer.init_hand([self.ten_clubs, self.five_hearts]) # Hidden 10, Face-up 5
        dealer.hits(Deck())
        self.assertFalse(dealer.is_blackjack())

        # False case (more than 2 cards, even if 21)
        dealer.reset()
        dealer.init_hand([self.five_hearts, self.seven_diamonds]) # Hidden 5, Face-up 7
        mock_deck = MockDeck(cards_to_deal=[self.nine_clubs])  # Deals 9
        dealer.hits(mock_deck) # 5 + 7 + 9 = 21 (but 3 cards)
        self.assertFalse(dealer.is_blackjack())

        # Test before init_hand is called
        dealer_uninitialized = Dealer()
        self.assertFalse(dealer_uninitialized.is_blackjack())

    def test_reset(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.five_hearts])
        dealer.reset()
        self.assertIsNone(dealer._Dealer__hand)
        self.assertIsNone(dealer._Dealer__hiden_card)

    def test_coner_case(self):
        delear = Dealer()
        delear.init_hand([self.ace_spades, self.three_clubs])
        mock_deck = MockDeck(
            cards_to_deal=[self.queen_diamonds, self.queen_diamonds])
        delear.hits(mock_deck, hit_soft17=True)
        # A(1) + 3 + Q(10) + Q(10) = 24
        self.assertEqual(delear.reveal_hand(), 24)

        delear.reset()
        delear.init_hand([self.ace_spades, self.three_clubs])
        mock_deck = MockDeck(
            cards_to_deal=[self.nine_clubs, self.queen_diamonds])
        delear.hits(mock_deck, hit_soft17=False)
        # A(11) + 3 + 9 = 23
        self.assertEqual(delear.reveal_hand(), 23)

    def test_str(self):
        dealer = Dealer()
        dealer.init_hand([self.king_spades, self.five_hearts]) # Hidden K, Face-up 5
        self.assertEqual(str(dealer), "Dealer's hand: ♠K?, ♥5, get points: 5")

        dealer.hits(MockDeck(cards_to_deal=[
                    # Reveals hidden card
                    self.five_hearts, self.king_spades, self.ace_clubs, self.five_hearts]))
        self.assertEqual(
            str(dealer), "Dealer's hand: ♠K, ♥5, ♥5, get points: 20")

        dealer.reset()
        # Test string representation when hand is not initialized
        # Updated based on string logic
        self.assertEqual(str(dealer), "Dealer's hand is not initialized.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)