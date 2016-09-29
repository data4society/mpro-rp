#encoding "utf-8"
// Дополнительные терминалы
quot -> Word {count = 3}| UnknownPOS {count = 3};
lat -> AnyWord<lat, h-reg1>+ interp(OrgFact_TOMITA.Org_TOMITA::not_norm);
Q -> quot<quoted> interp(OrgFact_TOMITA.Org_TOMITA::not_norm);
Words -> Word<~lat, ~l-quoted, ~r-quoted> {count = 3};

// Суды
Trial -> Word<kwtype='trial'>;

// Тюрьмы
Jail1 -> Word<kwtype='jail', h-reg1> | 'колония' Word<kwtype='jail', h-reg1>;
SIZO -> 'сизо' AnyWord<wfl="[0-9]+"> | 'сизо' '№' AnyWord<wfl="[0-9]+">;
Jail -> Jail1 | SIZO;

// ОАО
OOO -> Word<kwtype='OOO'> Q | Word<kwtype='OOO'> lat+;

// Международные организации
International -> Word<kwtype='inter'>;

// Российские организации
RusOrg -> Word<kwtype='rusorg'>;

// Аббревиатура Rus
Org1 -> AnyWord<wfl="[А-Я][А-Я][А-Я]+", ~dict> | AnyWord<wfl="[А-Я][а-я]+([А-Я][а-я]+)+", ~dict>;

// Аббревиатура Eng
Org3 -> AnyWord<wfl="[A-Z][A-Z][A-Z]+", ~dict> | AnyWord<wfl="[A-Z][a-z]+([A-Z][a-z]+)+", ~dict>;

// Фонды
Fond -> Word<kwtype='fond'> Word<gram='gen'>+ | Word<kwtype='fond'> Word<gram='gen'>+ SimConjAnd Word<gram='gen'>+ | Word<kwtype='fond'> Prep Dop_Fond1;
Dop_Fond1 -> Noun<gram=~'nom'> | Adj<gram=~'nom'>;
Dop_Fond2 -> SimConjAnd Dop_Fond1;
Fonds -> Fond | Fond Prep* Dop_Fond1+ | Fond Prep* Dop_Fond1 Dop_Fond2+;

// Министерства
RF -> Word<kwtype='RF'>;
Min ->  Word<kwtype='ministry'> RF | Word<kwtype='ministry'>;

// Агентство|Холдинг
Org2_NoWords -> Word<kwtype='ag'> Q | Word<kwtype='ag'> lat;
Org2_Words -> Word<kwtype='ag'> Q | Word<kwtype='ag'> Words lat;
Org2 -> Org2_NoWords | Org2_Words;

Org -> Trial | International | Fonds | RusOrg | Min | Jail | Org1<kwtype=~'KoAP'> | Org3 | Org_lat;
Organisation1 -> Org interp(OrgFact_TOMITA.Org_TOMITA::not_norm);
Organisation -> Organisation1 | Org2 | OOO;