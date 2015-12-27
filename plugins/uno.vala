using JiyuuBot;

enum CardColor {
    W, B, R, Y, G;

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
    WD4, D2, R, S,
    _0, _1, _2, _3, _4, _5, _6, _7, _8, _9,
    W, NULL;

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
}

class UnoGame : Object {
    public string game_master {construct; get;}
    // keep around so we can message the right chan
    public Prpl.Message init_message {construct; get;}
    public UnoCard top_card;
    public UnoCard[] cards;

    private Gee.HashMap<string, int> color_rec;
    public CardColor recommended_color;

    public void enumerate_cards(string text) {
        cards = {};
        color_rec = new Gee.HashMap<string, int>();
        var color_count = new Gee.HashMap<string, int>();
        UnoCard[] _cards = {};
        var tags = text.split("</FONT>");
        foreach (var pot_card in tags) {
            if ("[" in pot_card && "]" in pot_card) {
                var color = pot_card.split("\"")[1];
                var number = pot_card.split("[")[1].split("]")[0];
                if (color == "cyan")
                    color = "B";
                else
                    color = color.up()[0].to_string();
                _cards += new UnoCard(CardColor.get(color), CardNumber.get(number));
            }
        }
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
        if (col != null)
            recommended_color = col;
        cards = _cards;
    }

    public bool play_card(UnoCard card) {
        if (card.color == top_card.color || card.number == top_card.number) {
            init_message.send(".p %s %s".printf(card.color.to_string(), card.number.to_string()));
            return true;
        } else if (card.color == CardColor.W) {
            init_message.send(".p %s %s".printf(card.number.to_string(),
                recommended_color.to_string()));
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
        if (hm == null)
            hm = color_rec;
        if (card.number == CardNumber.WD4)
            return 500;
        if (card.number == CardNumber.W)
            return (int) CardNumber.W;
        var number = (int) card.number;
        if (number > CardNumber._0)
            number = CardNumber._0;
        var result = (hm[card.color.to_string()] * 10) / number;
        if (result < 0)
            return 1;
        return result;
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
        if (msg.text.has_prefix("IRC-UNO started by")) {
            games.set(msg.sender, new UnoGame(msg.sender, msg));
            msg.send(".ujoin");
        } else if (games.has_key(msg.sender)) {
            if (msg.text == "Game stopped." || msg.text.has_prefix("We have a winner!")) {
                games.unset(msg.sender);
            } else if (msg.us.down() in msg.text && "top card" in msg.text.down()) {
                var top_card = msg.text.split("Top Card: ")[1];
                var color = top_card[1].to_string();
                var number = top_card.split("[")[1].replace("]", "");
                games[msg.sender].top_card =
                    new UnoCard(CardColor.get(color), CardNumber.get(number));
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
        foreach (var card in game.cards) {
            var score = game.score_card(card);
            if (game.card_playable(card) && game.score_card(card) > game.score_card(to_play))
                to_play = card;
        }
        if (to_play != null)
            game.play_card(to_play);
        else
            game.init_message.send(".d");
    }
}

public Type[] register_plugin() {
    return {typeof(UnoPlayer)};
}
