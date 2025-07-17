
|s|a|s'|reward|p(s' given s,a)|p(s',r given s, a)|
|:---|:---|:---|:---|:---|:---|
|<21|stand|win|1|
|<21|stand|push|0|
|<21|stand|lose|-1|
|<21|hit|<21|-|
|<21|hit|win|1|
|<21|hit|push|0|
|<21|hit|lose|-1|
|<21|double|<21, doubled|-
|<21, doubled|stand|win|2
|<21, doubled|stand|push|0
|<21, doubled|stand|lose|-2
|<21, pair|split|<21|-
|<21, pair|split|<21, pair|-
|<21, pair|not split|<21|-
|<21, dealer ace|no insurance|<21|-
|<21, dealer ace|insurance|<21, insuranced|-
|<21, insuranced|-|Dealer has blackjack|1+x
|<21, insuranced|-|Dealer has no blackjack|-0.5+x
|blackjack|stand|win|1.5
|blackjack|stand|push|0

