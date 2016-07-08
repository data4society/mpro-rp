#encoding "utf-8"
//Criminal Code
RF -> Word<kwtype='RF'>;
UK -> Word<kwtype='uk'> Word<h-reg1> | Word<kwtype='uk'> RF;

Connect -> SimConjAnd | Comma | ';';

St -> 'статья' | 'ст';
Art1 -> St AnyWord<wfl="[0-9]+.?[0-9]*"> Connect* | St '№' AnyWord<wfl="[0-9]+.?[0-9]*"> Connect*;
Art2 -> AnyWord<wfl="ст.?[0-9]+"> Connect*;
Art -> Art1 | Art2;

Ch -> 'часть' | 'ч';
Part1 -> Ch AnyWord<wfl="[0-9]+"> Connect* | Ch '№' AnyWord<wfl="[0-9]+"> Connect*;
Part2 -> AnyWord<wfl="ч.?[0-9]+"> Connect*;
Part -> Part1 | Part2;

Pun -> 'пункт' | 'п';
P1 -> AnyWord<wfl="([а-я]|[А-Я])"> Connect*;
P2 -> AnyWord<wfl="[0-9]+"> Connect;
Point -> Pun P2+ | Pun '№' P2+ | Pun P1+ |Pun '№' P1+;

Act1 -> Point+;
Act2 -> Part+;
Act3 -> Art+;
Act4 -> UK;

// KoAP
KoAP -> Word<kwtype='KoAP'> | Word<kwtype='KoAP'> RF;
KoAP_N -> 'n' AnyWord<wfl="[0-9]+.?[А-Я]+">;

Norm_Act -> Act1 | Act2 | Act3 | Act4 | KoAP | KoAP_N;
Norm_Act_int -> Norm_Act interp(NormFact_TOMITA.Norm_TOMITA::not_norm);
