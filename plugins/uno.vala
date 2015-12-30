using JiyuuBot;

enum CardColor {
    NULL, W, B, R, Y, G;

    public string to_string() {
        var enumc = (EnumClass) typeof(CardColor).class_ref();
        unowned EnumValue? color_string = enumc.get_value(this);
        assert (color_string != null);
        return color_string.value_nick;
    }

    public static CardColor @get(owned string name) {
        if (!name.has_prefix("CARD_COLOR_"))
            name = "CARD_COLOR_" + name;
        var enumc = (EnumClass) typeof(CardColor).class_ref();
        unowned EnumValue? color = enumc.get_value_by_name(name.up());
        assert (color != null);
        return (CardColor) color.value;
    }
}

enum CardNumber {
    NULL, W,
    _0, _1, _2, _3, _4, _5, _6, _7, _8, _9,
    S, R, D2, WD4;

    public string to_string() {
        var enumc = (EnumClass) typeof(CardNumber).class_ref();
        unowned EnumValue? number_string = enumc.get_value(this);
        assert (number_string != null);
        return number_string.value_nick.replace("-", "");
    }

    public static CardNumber @get(owned string name) {
        var enumc = (EnumClass) typeof(CardNumber).class_ref();
        if (name == "*")
            name = "NULL";
        string[] non_nums = {"WD4", "D2", "R", "S", "W", "NULL"};
        if (!(name in non_nums))
            name = "_" + name;
        if (!name.has_prefix("CARD_NUMBER_"))
            name = "CARD_NUMBER_" + name;
        var number = enumc.get_value_by_name(name.up());
        assert (number != null);
        return (CardNumber) number.value;
    }
}

class UnoCard : Object {
    public CardColor color {construct; get;}
    public CardNumber number {construct; get;}

    public UnoCard(CardColor color, CardNumber number) {
        Object(color: color, number: number);
    }

    public UnoCard.from_text(string text) {
        assert ("[" in text && "]" in text);
        var color = text.split("\"")[1];
        var number = text.split("[")[1].split("]")[0];
        if (number == "WD4" || number == "W")
            color = "W";
        else if (color == "cyan" || color == "light blue")
            color = "B";
        else
            color = color.up()[0].to_string();
        Object(color: CardColor.get(color), number: CardNumber.get(number));
    }

    public static UnoCard[] all_from_text(owned string text) {
        text = text.replace("<B>", "").replace("</B>", "");
        UnoCard[] cards = {};
        foreach (var pot_card in text.split("</FONT>"))
            if (pot_card != "")
                cards += new UnoCard.from_text(pot_card);
        return cards;
    }
}

class UnoGame : Object {
    public string game_master {construct; get;}
    // keep around so we can message the right chan
    public Prpl.Message init_message {construct; get;}
    public UnoCard top_card;
    public UnoCard[] cards;

    private Gee.HashMap<string, int> color_rec;
    public CardColor? recommended_color;

    public void enumerate_cards(string text) {
        cards = {};
        color_rec = new Gee.HashMap<string, int>();
        recommended_color = null;
        var color_count = new Gee.HashMap<string, int>();
        var _cards = UnoCard.all_from_text(text);
        foreach (var card in _cards) {
            if (card.color == CardColor.W)
                continue;
            if (!color_count.has_key(card.color.to_string()))
                color_count.set(card.color.to_string(), 0);
            color_count[card.color.to_string()] = color_count[card.color.to_string()] + 1;
        }
        foreach (var card in _cards) {
            if (card.color == CardColor.W)
                continue;
            if (!color_rec.has_key(card.color.to_string()))
                color_rec.set(card.color.to_string(), 0);
            color_rec[card.color.to_string()] = color_rec[card.color.to_string()]
                + score_card(card, color_count);
        }
        int num = 0;
        CardColor? col = null;
        color_rec.foreach((e) => {
            if (e.value > num) {
                num = e.value;
                col = CardColor.get(e.key);
            }
            return true;
        });
        recommended_color = col;
        cards = _cards;
    }

    public bool play_card(UnoCard card) {
        if (card.color == top_card.color || card.number == top_card.number) {
            init_message.send(@".p $(card.color) $(card.number)");
            return true;
        } else if (card.color == CardColor.W) {
            if (recommended_color == null)
                recommended_color = top_card.color;
            init_message.send(@".p $(card.number) $(recommended_color)");
            return true;
        }
        return false;
    }

    public bool card_playable(UnoCard card) {
        return card.color == CardColor.W || card.color == top_card.color ||
            card.number == top_card.number;
    }

    public int score_card(UnoCard? card, Gee.HashMap<string, int>? hm = null) {
        if (card == null)
            return 0;
        assert (card.number != CardNumber.NULL);
        if (hm == null)
            hm = color_rec;
        if (card.color == CardColor.W) {
            if (top_card.color == recommended_color || card.number == CardNumber.W)
                return 1;
            return int.MAX; // this means we're a WD4 that isn't going to be wasted
        }
        var number = (int) card.number;
        if (CardNumber._0 <= number <= CardNumber._9)
            number = CardNumber._0;
        return hm[card.color.to_string()] * number;
    }

    public UnoGame(string gm, Prpl.Message msg) {
        Object(game_master: gm, init_message: msg);
    }
}

class UnoPlayer : Plugins.BasePlugin {
    private Gee.HashMap<string, UnoGame> games;

    public override void activate() {
        games = new Gee.HashMap<string, UnoGame>();
    }

    public override bool should_exec(Prpl.Message msg) {
        if (msg.at_us) {
            if (msg.text.down().strip() == ".uno")
                msg.send(".uno");
            else if (msg.text.down().has_prefix(".deal"))
                foreach (var game in games.values) {
                    if (Prpl.Message.same_context(msg, game.init_message)) {
                        game.init_message.send(".deal");
                        break;
                    }
                }
        } else if (msg.text.has_prefix("IRC-UNO started by") && !games.has_key(msg.sender)) {
            var game_in_progress = false;
            foreach (var game in games.values) {
                if (Prpl.Message.same_context(msg, game.init_message)) {
                    game_in_progress = true;
                    break;
                }
            }
            if (!game_in_progress) {
                games.set(msg.sender, new UnoGame(msg.sender, msg));
                if (!(msg.context.display_name.down() in msg.text.down()))
                    msg.send(".ujoin");
            }
        } else if (games.has_key(msg.sender)) {
            if (Prpl.Message.same_context(msg, games[msg.sender].init_message)) {
                if (@"new owner is $(games[msg.sender].init_message.context.display_name.down())" in msg.text.down()) {
                    games[msg.sender].init_message.send(".unostop");
                } else if (msg.text == "Game stopped." || msg.text.has_prefix("We have a winner!")) {
                    games.unset(msg.sender);
                } else if (msg.context.display_name.down() in msg.text.down() && "Top Card: " in msg.text) {
                    games[msg.sender].top_card =
                        new UnoCard.from_text(msg.raw_text.split("Top Card: ")[1]);
                }
            } else if (msg.text.has_prefix("(notice) Drawn card:")) {
                var game = games[msg.sender];
                var wc = game.recommended_color;
                game.enumerate_cards(msg.raw_text);
                game.recommended_color = wc;
                if (!game.play_card(game.cards[0]))
                    game.init_message.send(".pa");
            } else if (msg.text.has_prefix("(notice) Your cards:")) {
                return true;
            }
        }
        return false;
    }

    public override void exec(Prpl.Message msg) {
        var game = games[msg.sender];
        game.enumerate_cards(msg.raw_text);
        UnoCard? to_play = null;
        foreach (var card in game.cards)
            if (game.card_playable(card) && game.score_card(card) > game.score_card(to_play))
                to_play = card;
        if (to_play != null)
            game.play_card(to_play);
        else
            game.init_message.send(".d");
    }
}

public Type[] register_plugin() {
    return {typeof(UnoPlayer)};
}
