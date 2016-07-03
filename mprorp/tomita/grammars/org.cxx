#encoding "utf-8"
// Суды
Trial -> Word<kwtype='trial'>;
// ОАО
OOO -> Word<kwtype='OOO'> Word<h-reg2>+ | Word<kwtype='OOO'> Word<quoted> | Word<kwtype='OOO'> Word<lat>;
// Международные организации
International -> Word<kwtype='inter'>;
// Российские организации
RusOrg -> Word<kwtype='rusorg'>;
// Аббревиатура
Org1 -> AnyWord<wfl="[А-Я][А-Я][А-Я]+"> | AnyWord<wfl="[А-Я][а-я]+([А-Я][а-я]+)+">;
// Фонды
Fond -> 'фонд' Word<gram='gen'>+ | 'фонд' Word<gram='gen'>+ SimConjAnd Word<gram='gen'>+ | 'фонд' Prep Dop_Fond1;
Dop_Fond1 -> Noun<gram=~'nom'> | Adj<gram=~'nom'>;
Dop_Fond2 -> SimConjAnd Dop_Fond1;
Fonds -> Fond | Fond Prep* Dop_Fond1+ | Fond Prep* Dop_Fond1 Dop_Fond2+;
// Министерства
RF -> Word<kwtype='RF'>;
Min ->  Word<kwtype='ministry'> RF | Word<kwtype='ministry'>;

Org -> Trial | OOO | International | Org1 | Fonds | RusOrg | Min;
Organisation -> Org interp(OrgFact_TOMITA.Org_TOMITA::not_norm);