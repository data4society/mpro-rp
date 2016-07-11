#encoding "utf-8"
// Название в кавычках
Q -> Word+;
// Суды
Trial -> Word<kwtype='trial'>;
// Тюрьмы
Jail1 -> Word<kwtype='jail', h-reg1> | 'колония' Word<kwtype='jail', h-reg1>;
SIZO -> 'сизо' AnyWord<wfl="[0-9]+"> | 'сизо' '№' AnyWord<wfl="[0-9]+">;
Jail -> Jail1 | SIZO;
// ОАО
OOO -> Word<kwtype='OOO'> Word<h-reg2>+ | Word<kwtype='OOO'> Q<quoted> | Word<kwtype='OOO'> Word<lat>;
// Международные организации
International -> Word<kwtype='inter'>;
// Российские организации
RusOrg -> Word<kwtype='rusorg'>;
// Аббревиатура
Org1 -> AnyWord<wfl="[А-Я][А-Я][А-Я]+", ~dict> | AnyWord<wfl="[А-Я][а-я]+([А-Я][а-я]+)+", ~dict>;
// Фонды
Fond -> Word<kwtype='fond'> Word<gram='gen'>+ | Word<kwtype='fond'> Word<gram='gen'>+ SimConjAnd Word<gram='gen'>+ | Word<kwtype='fond'> Prep Dop_Fond1;
Dop_Fond1 -> Noun<gram=~'nom'> | Adj<gram=~'nom'>;
Dop_Fond2 -> SimConjAnd Dop_Fond1;
Fonds -> Fond | Fond Prep* Dop_Fond1+ | Fond Prep* Dop_Fond1 Dop_Fond2+;
// Министерства
RF -> Word<kwtype='RF'>;
Min ->  Word<kwtype='ministry'> RF | Word<kwtype='ministry'>;
// Иностранные организации
Org2 -> Word<kwtype='comp'> AnyWord<lat, h-reg1>+;
// Агентство
Agent -> Word<kwtype='ag'> Word<h-reg1>+ | Word<kwtype='ag'> Q<quoted>;

Org -> Trial | OOO | International | Fonds | RusOrg | Min | Org2 | Jail | Org1<kwtype=~'KoAP'> | Agent;
Organisation -> Org interp(OrgFact_TOMITA.Org_TOMITA::not_norm);