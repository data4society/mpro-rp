#encoding "utf-8"

Trial -> Word<kwtype='trial'>;

OOO -> Word<kwtype='OOO'> Word<h-reg2>+ | Word<kwtype='OOO'> Word<quoted> | Word<kwtype='OOO'> Word<lat>;

International -> Word<kwtype='inter'>;

Org1 -> AnyWord<wfl="[А-Я][А-Я][А-Я]+"> | AnyWord<wfl="[А-Я][а-я]+([А-Я][а-я]+)+">;

Fond -> 'фонд' Word<gram='gen'>+ | 'фонд' Word<gram='gen'>+ SimConjAnd Word<gram='gen'>+;
Dop1 -> Noun<gram=~'nom'> | Adj<gram=~'nom'>;
Dop2 -> SimConjAnd Dop1;
Fonds -> Fond | Fond Prep* Dop1+ | Fond Prep* Dop1 Dop2+;

Org -> Trial | OOO | International | Org1 | Fonds;
Organisation -> Org interp(OrgFact_TOMITA.Org_TOMITA::not_norm);