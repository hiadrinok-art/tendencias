# PERNAMBUCO: Terra de História, Coragem e Revolução
## Roteiro completo (v2) + tabela de produção

Documento de trabalho do documentário, no estilo da skill **estilo-documentario**: cada quadro desenhado em código, uma câmera contínua sobre um único mundo, um destaque por vez sincronizado com a palavra falada, fotos só com licença livre e sons reais.

| Item | Decisão |
|---|---|
| Duração | **~7,5 min**: 83 frases, 983 palavras de narração, mais os respiros |
| Voz | "Nassif" (ElevenLabs), pt-BR, a mesma do piloto aprovado |
| Ritmo | O do piloto da Cena 5, aprovado |
| Formato | 16:9, 1920×1080, 30 fps. Depois, cortes 9:16 por cena |
| Estilo visual | **Misto.** Mesa de arquivo (madeira, papel envelhecido, luz quente) da Abertura à Cena 5. **Cordel** (papel creme, tinta preta, tipos de madeira, vermelho de impressão) da Cena 6 ao Final |
| Já produzido | **Cena 5** (piloto, nas duas peles). Projeto em `cena5/` |

---

## 1. Como os dois estilos convivem num plano-sequência

```
 ┌───────────────────────────── MESA DE ARQUIVO (madeira escura) ─────────────────────────────┐
 │  C1 POVOS        C2 AÇÚCAR         C3 PALMARES        C4 HOLANDESES        C5 1817/1824    │
 │  mapa, Catimbau  Olinda, engenho   Serra da Barriga   Recife, sinagoga,    (piloto pronto) │
 │                                                       Guararapes                           │
 │                         ABERTURA: folha "6 de março de 1817" + título                      │
 │                                                                                            │
 │        ┌──────────────── GRANDE FOLHETO DE CORDEL aberto sobre a mesa ────────────────┐     │
 │        │  C6 CULTURA        C7 DO MAR AO SERTÃO          C8 PRÓXIMO CAPÍTULO           │     │
 │        │  frevo, maracatu,  faixa de PE: litoral →      Recife Antigo / Porto Digital │     │
 │        │  forró, manguebeat sertão → São Francisco                                    │     │
 │        │                       FINAL: bandeira + título                                │     │
 │        └───────────────────────────────────────────────────────────────────────────────┘     │
 └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **A virada (6.1, "Mas Pernambuco não se explica só por guerras"):** a câmera sai da região da Cena 5, recua e encontra um folheto de cordel fechado sobre a mesa. A capa se abre e a câmera **mergulha no papel**. Dali em diante o mundo é cordel.
- **O fecho (F.8):** a câmera recua do folheto e revela de novo a mesa inteira, com tudo o que foi visto. Os dois estilos aparecem juntos no último quadro.
- **Técnica:** o `cordel.css` da skill passa a valer só dentro de `.zona-cordel`, em vez da página toda. Os ids e o motor não mudam.

**Legenda das colunas:**
- **Gatilho:** palavra que dispara o destaque (o segundo exato vem da transcrição).
- **Destaque:** o único elemento aceso naquele momento.
- **Texto:** o que aparece escrito na tela, no máximo 6 palavras.
- **Câmera:** aproxima, recua, desliza, viaja ou mergulha.
- **Som:** efeito pontual. A trilha está na seção 4.

---

## 2. Roteiro e produção, cena por cena

### ABERTURA: 6 de março de 1817 · mesa · ~25 s

> 6 de março de 1817. No Recife, um grupo de revolucionários toma o poder. O Brasil ainda pertencia à Coroa portuguesa. A independência só viria cinco anos depois. Mas, naquele dia, um pedaço do Brasil se declarou república. Para entender como isso foi possível, é preciso voltar muito antes.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| A.1 | 6 de março de 1817. | "6" | Data datilografada numa folha, no escuro | 6 de março de 1817 | Aproxima do preto até a folha | Máquina de escrever; grave longo |
| A.2 | No Recife, um grupo de revolucionários toma o poder. | "Recife" | Ponto vermelho pulsa no litoral de um mapa | — | Desliza para o mapa | Batida grave |
| A.3 | O Brasil ainda pertencia à Coroa portuguesa. | "Coroa" | Coroa desenhada em traço sobre o mapa do Brasil | — | Recua | Pena traçando |
| A.4 | A independência só viria cinco anos depois. | "cinco" | Linha do tempo 1817 ●——● 1822 | 1817 → 1822 | Desliza pela linha | — |
| A.5 | Mas, naquele dia, um pedaço do Brasil se declarou república. | "república" | Carimbo "REPÚBLICA" sobre Pernambuco | — | Aproxima, com tremor | **Carimbo** (a música corta) |
| A.6 | Para entender como isso foi possível, é preciso voltar muito antes. | "antes" | Folhas da mesa "voam" para trás e surge o título | **PERNAMBUCO** · Terra de História, Coragem e Revolução | Recua até ver a mesa toda | Papéis + entra o tema da trilha |

### CENA 1: A terra antes do nome · mesa · ~30 s

> Muito antes de existir Brasil, esta terra já tinha gente, nomes e histórias. Caetés, Potiguaras, Tabajaras e muitos outros povos viviam aqui. Do litoral ao sertão, cada um com sua língua, seus rituais e seu jeito de ler a natureza. No interior, as rochas do Vale do Catimbau ainda guardam pinturas feitas há milhares de anos. É a memória mais antiga de Pernambuco. E ela não foi escrita em papel.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 1.1 | Muito antes de existir Brasil, esta terra já tinha gente, nomes e histórias. | "gente" | Mapa de PE sem divisões, só relevo e rios | — | Viaja para C1 | Vento, folhas |
| 1.2 | Caetés, Potiguaras, Tabajaras e muitos outros povos viviam aqui. | "Caetés" → "Potiguaras" → "Tabajaras" | Três nomes escritos à mão no mapa, um por palavra | — | Desliza entre os nomes | Pena ×3 |
| 1.3 | Do litoral ao sertão, cada um com sua língua, seus rituais e seu jeito de ler a natureza. | "litoral" → "sertão" | Faixa do mapa acende do azul ao ocre | — | Desliza de leste a oeste | Ondas → vento seco |
| 1.4 | No interior, as rochas do Vale do Catimbau ainda guardam pinturas feitas há milhares de anos. | "Catimbau" | **Foto das pinturas rupestres do Catimbau (CC)** cai na mesa | Vale do Catimbau | Aproxima na foto | Papel caindo |
| 1.5 | É a memória mais antiga de Pernambuco. | "memória" | Figuras rupestres redesenhadas em traço ocre ao lado da foto | — | Aproxima mais | Pena lenta |
| 1.6 | E ela não foi escrita em papel. | "papel" | A foto apaga e só as figuras ficam acesas | — | Recua | Silêncio breve |

### CENA 2: O açúcar · mesa · ~45 s

> Em 1535, Duarte Coelho desembarca para tomar posse da capitania de Pernambuco. No alto de uma colina, de frente para o mar, ele funda Olinda. E aposta numa planta trazida de longe: a cana-de-açúcar. Em poucas décadas, os engenhos fazem de Pernambuco a região mais rica da América portuguesa. Mas essa riqueza tinha um custo que o açúcar escondia. Centenas de milhares de africanos foram trazidos à força e escravizados nos engenhos. Povos indígenas perderam suas terras, e muitos, suas vidas. O açúcar adoçou a Europa. E deixou em Pernambuco feridas que o tempo não apagou.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 2.1 | Em 1535, Duarte Coelho desembarca para tomar posse da capitania de Pernambuco. | "1535" | Data + caravela desenhada chegando à costa (sem retrato: não há retrato autêntico) | 1535 | Viaja para C2 com a caravela | Máquina; madeira e mar |
| 2.2 | No alto de uma colina, de frente para o mar, ele funda Olinda. | "Olinda" | **Pintura de Frans Post com vista de Olinda (domínio público)** | Olinda | Aproxima na pintura | Papel caindo; sino |
| 2.3 | E aposta numa planta trazida de longe: a cana-de-açúcar. | "cana" | Ramo de cana desenhado em traço cresce sobre o mapa | — | Desliza | Folhas secas |
| 2.4 | Em poucas décadas, os engenhos fazem de Pernambuco a região mais rica da América portuguesa. | "engenhos" | **Frans Post, pintura de engenho (domínio público)** | — | Aproxima | Moenda ao longe |
| 2.5 | Mas essa riqueza tinha um custo que o açúcar escondia. | "custo" | Torrão de açúcar desenhado; a música cai | — | Aproxima lento | A trilha some |
| 2.6 | Centenas de milhares de africanos foram trazidos à força e escravizados nos engenhos. | "escravizados" | Livro-registro antigo: a palavra é sublinhada em vermelho. **Sem imagens de sofrimento** | — | Aproxima no livro | Página virando |
| 2.7 | Povos indígenas perderam suas terras, e muitos, suas vidas. | "terras" | Os nomes da Cena 1 no mapa se apagam um a um | — | Desliza no mapa | Silêncio |
| 2.8 | O açúcar adoçou a Europa. | "Europa" | Rota pontilhada do Recife até Lisboa e Amsterdã | — | Recua (mapa do Atlântico) | Caneta riscando |
| 2.9 | E deixou em Pernambuco feridas que o tempo não apagou. | "feridas" | O torrão se desfaz em pó sobre o mapa | — | Recua | Grave baixo; a trilha volta |

### CENA 3: Palmares · mesa · ~30 s

> Mas onde houve escravidão, houve resistência. Na Serra da Barriga, então território pernambucano, pessoas que fugiram dos engenhos ergueram Palmares. Por quase um século, o quilombo resistiu às expedições que tentavam destruí-lo. Seu líder mais conhecido, Zumbi, foi morto em 20 de novembro de 1695. Hoje, essa data é o Dia da Consciência Negra.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 3.1 | Mas onde houve escravidão, houve resistência. | "resistência" | Uma linha vermelha sai dos engenhos em direção ao interior | — | Viaja para C3 seguindo a linha | Tambor grave ×1 |
| 3.2 | Na Serra da Barriga, então território pernambucano, pessoas que fugiram dos engenhos ergueram Palmares. | "Palmares" | **Foto da Serra da Barriga (CC)**; mapa com a fronteira antiga de PE (Alagoas ainda dentro) | Palmares · Serra da Barriga | Aproxima | Papel caindo; mata |
| 3.3 | Por quase um século, o quilombo resistiu às expedições que tentavam destruí-lo. | "resistiu" | Setas de expedições batem e recuam diante de uma paliçada desenhada | — | Desliza | Tambores ao longe |
| 3.4 | Seu líder mais conhecido, Zumbi, foi morto em 20 de novembro de 1695. | "Zumbi" → "1695" | Nome "ZUMBI" datilografado; depois a data. **Sem retrato inventado** (não existe imagem autêntica) | Zumbi · 20/11/1695 | Aproxima | Máquina; a trilha some |
| 3.5 | Hoje, essa data é o Dia da Consciência Negra. | "Consciência" | A data recebe o carimbo "20 DE NOVEMBRO", e a frase se completa | Dia da Consciência Negra | Recua devagar | Carimbo; a trilha volta digna |

### CENA 4: Pernambuco disputado por impérios · mesa · ~75 s

> Em 1630, a riqueza de Pernambuco atrai uma frota estrangeira. A Companhia das Índias Ocidentais, dos Países Baixos, toma Olinda e Recife. Olinda é incendiada. O Recife se torna o centro do Brasil holandês. Em 1637, chega o conde Maurício de Nassau. Ele traz pintores, cientistas e engenheiros. Ergue pontes, palácios e uma nova cidade ao lado do Recife. Na mesma época, judeus vindos da Holanda fundam ali a Kahal Zur Israel, a primeira sinagoga das Américas. Mas, por trás da vitrine, os engenhos continuavam movidos pelo trabalho escravizado. Em 1645, começa a Insurreição Pernambucana. Senhores de engenho, soldados, indígenas e negros lutam do mesmo lado. Nomes como Henrique Dias e Filipe Camarão entram para a história. Nos Montes Guararapes, em 1648 e 1649, as tropas locais vencem duas batalhas decisivas. Em 1654, os holandeses se rendem. O Exército Brasileiro considera a primeira batalha dos Guararapes o seu marco de origem.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 4.1 | Em 1630, a riqueza de Pernambuco atrai uma frota estrangeira. | "1630" | Data; frota holandesa desenhada no horizonte do mapa | 1630 | Viaja para C4 | Máquina; mar e canhão distante |
| 4.2 | A Companhia das Índias Ocidentais, dos Países Baixos, toma Olinda e Recife. | "toma" | Setas da frota atingem Olinda e Recife; bandeirinha holandesa espetada | — | Desliza com as setas | Alfinete |
| 4.3 | Olinda é incendiada. | "incendiada" | A pintura de Olinda (2.2) reaparece e escurece pelas bordas, como papel queimado | — | Aproxima | Fogo crepitando, curto |
| 4.4 | O Recife se torna o centro do Brasil holandês. | "centro" | Recife circulado no **mapa de Marcgraf (1647, domínio público)** | — | Recua para o mapa | Pena circulando |
| 4.5 | Em 1637, chega o conde Maurício de Nassau. | "Nassau" | **Retrato de Johan Maurits por Jan de Baen (domínio público)** cai grande | Maurício de Nassau | Aproxima no retrato | Papel caindo |
| 4.6 | Ele traz pintores, cientistas e engenheiros. | "pintores" | Três ícones em traço (pincel, luneta, compasso), um por palavra | — | Desliza | Pena ×3 |
| 4.7 | Ergue pontes, palácios e uma nova cidade ao lado do Recife. | "pontes" | Ponte desenhada liga Recife à Cidade Maurícia no mapa | — | Desliza ao longo da ponte | Madeira e pedra |
| 4.8 | Na mesma época, judeus vindos da Holanda fundam ali a Kahal Zur Israel, a primeira sinagoga das Américas. | "sinagoga" | **Foto da fachada da sinagoga Kahal Zur Israel, Recife (CC)** | Kahal Zur Israel · 1636 | Aproxima | Papel caindo |
| 4.9 | Mas, por trás da vitrine, os engenhos continuavam movidos pelo trabalho escravizado. | "escravizado" | O livro-registro da Cena 2 reacende | — | Recua | A trilha baixa |
| 4.10 | Em 1645, começa a Insurreição Pernambucana. | "Insurreição" | Data + carimbo "INSURREIÇÃO" | 1645 | Viaja | Carimbo; tambor militar |
| 4.11 | Senhores de engenho, soldados, indígenas e negros lutam do mesmo lado. | "mesmo lado" | Quatro silhuetas em traço se alinham | — | Desliza | Passos marchando |
| 4.12 | Nomes como Henrique Dias e Filipe Camarão entram para a história. | "Henrique Dias" → "Camarão" | Nomes datilografados, um por vez | Henrique Dias · Filipe Camarão | Desliza | Máquina ×2 |
| 4.13 | Nos Montes Guararapes, em 1648 e 1649, as tropas locais vencem duas batalhas decisivas. | "Guararapes" | **Victor Meirelles, *Batalha dos Guararapes* (domínio público)**; a câmera percorre a pintura | 1648 · 1649 | Mergulha e desliza pela pintura | Tambores; mosquetes ao longe |
| 4.14 | Em 1654, os holandeses se rendem. | "1654" | A bandeirinha holandesa é arrancada do mapa | 1654 | Recua | Alfinete saindo; **carimbo** (a música morre) |
| 4.15 | O Exército Brasileiro considera a primeira batalha dos Guararapes o seu marco de origem. | "origem" | A pintura reacende em plano geral | — | Recua lento | A trilha volta suave |

### CENA 5: A república antes do Brasil · mesa · ~85 s · ✅ piloto produzido

> Mais de um século e meio depois, voltamos ao dia em que tudo começou. 6 de março de 1817. Revoltados com impostos, privilégios e a falta de autonomia, comerciantes, padres e militares tomam o Recife. Nasce um governo provisório republicano. Ele cria uma bandeira: azul e branca, com arco-íris, sol e cruz. A república durou cerca de setenta e cinco dias. Seus líderes foram presos, e vários, executados. Pouco depois, a Coroa desmembrou de Pernambuco a comarca das Alagoas. Sete anos mais tarde, Pernambuco se levanta de novo. Em 1824, contra um imperador que havia fechado a Assembleia Constituinte, nasce a Confederação do Equador. A voz mais forte do movimento é a de um frade: Frei Caneca. Condenado à forca, ele não encontrou carrasco que aceitasse enforcá-lo. Em 13 de janeiro de 1825, Frei Caneca foi fuzilado. Quase um século depois, em 1917, a bandeira de 1817 se tornou a bandeira oficial de Pernambuco.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 5.0 | Mais de um século e meio depois, voltamos ao dia em que tudo começou. | "voltamos" | **Nova:** a folha "6 de março de 1817" da Abertura reacende | — | Viaja de C4 de volta à folha da Abertura | Papel |
| 5.1–5.17 | (o restante da cena) | — | **Como no piloto** (`cena5/plano.json`): documento circulado, setas no Recife, carimbo "GOVERNO PROVISÓRIO", bandeira de 1817 com 3 estrelas, 75 dias, sentença, Alagoas se separando, 1824, "DISSOLVIDA", Confederação, *Typhis Pernambucano*, Parreiras, forca, 1825, bandeira de 1917 com 1 estrela | — | Como no piloto | Como no piloto |

**Ajuste para o filme completo:** regerar a narração inteira de uma vez, para a voz ficar contínua. Com isso, os tempos da Cena 5 mudam e o plano é recalculado a partir da nova transcrição.

### CENA 6: A cultura que ferve · **cordel** · ~75 s

> Mas Pernambuco não se explica só por guerras. Em 1907, um jornal do Recife imprime uma palavra nova: frevo. Vem de "frever", o jeito popular de dizer ferver. E é isso que acontece nas ladeiras de Olinda e nas ruas do Recife a cada carnaval. Em 2012, a UNESCO reconheceu o frevo como patrimônio cultural imaterial da humanidade. Nos tambores do maracatu, a herança africana desfila com reis, rainhas e alfaias. No Agreste, Caruaru transforma o São João em uma das maiores festas do país. Ali perto, no Alto do Moura, mestres do barro moldam o cotidiano do sertanejo. Do Sertão veio a voz que levou o forró ao Brasil inteiro: Luiz Gonzaga, nascido em Exu. E, nos anos noventa, o Recife misturou maracatu com guitarra e criou o manguebeat. Em Pernambuco, tradição não é peça de museu. É coisa viva, que se reinventa.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 6.1 | Mas Pernambuco não se explica só por guerras. | "guerras" | **A virada:** folheto de cordel fechado sobre a mesa; a capa abre | — | Recua de C5, encontra o folheto e **mergulha no papel** | Papel abrindo; a trilha troca para a regional |
| 6.2 | Em 1907, um jornal do Recife imprime uma palavra nova: frevo. | "frevo" | Bloco de impressão vermelho "FREVO" prensado no papel | 1907 · FREVO | Aproxima | Prensa/carimbo |
| 6.3 | Vem de "frever", o jeito popular de dizer ferver. | "ferver" | As letras de "FREVO" tremem como se fervessem | frever = ferver | Leve tremor | Metais de frevo (vinheta de 1 s) |
| 6.4 | E é isso que acontece nas ladeiras de Olinda e nas ruas do Recife a cada carnaval. | "carnaval" | **Sombrinha de frevo em xilogravura** abre girando; ladeira de casario em traço | — | Desliza pela ladeira | Metais + multidão ao longe |
| 6.5 | Em 2012, a UNESCO reconheceu o frevo como patrimônio cultural imaterial da humanidade. | "UNESCO" | Selo carimbado | UNESCO · 2012 | Aproxima no selo | Carimbo |
| 6.6 | Nos tambores do maracatu, a herança africana desfila com reis, rainhas e alfaias. | "maracatu" → "alfaias" | Cortejo em xilogravura (rei, rainha, estandarte); depois a alfaia vibra | Maracatu | Desliza com o cortejo | Alfaias (loop curto) |
| 6.7 | No Agreste, Caruaru transforma o São João em uma das maiores festas do país. | "São João" | Bandeirinhas atravessam o quadro; fogueira em xilogravura | Caruaru · São João | Desliza | Fogos ao longe; sanfona |
| 6.8 | Ali perto, no Alto do Moura, mestres do barro moldam o cotidiano do sertanejo. | "barro" | Boneco de barro **genérico** desenhado (não copia obras de Vitalino) | Alto do Moura | Aproxima | Argila |
| 6.9 | Do Sertão veio a voz que levou o forró ao Brasil inteiro: Luiz Gonzaga, nascido em Exu. | "Luiz Gonzaga" | Sanfona + chapéu de couro em xilogravura (**sem foto**: as fotos dele ainda têm direito autoral); nome em tipo de madeira | Luiz Gonzaga · Exu | Aproxima | Sanfona, 2 compassos |
| 6.10 | E, nos anos noventa, o Recife misturou maracatu com guitarra e criou o manguebeat. | "manguebeat" | Caranguejo em xilogravura com antena (símbolo do movimento); guitarra cruza a alfaia | MANGUEBEAT | Desliza | Riff curto de guitarra + alfaia |
| 6.11 | Em Pernambuco, tradição não é peça de museu. | "museu" | Moldura de museu vazia, desenhada | — | Recua | A trilha baixa |
| 6.12 | É coisa viva, que se reinventa. | "viva" | Todos os objetos da cena pulsam juntos e voltam a um só: a sombrinha | — | Recua até ver a cena toda | A batida volta forte |

**Direito autoral:** nada de xilogravuras de artistas reais (ex.: J. Borges), fotos de obras de Mestre Vitalino, fotos de Luiz Gonzaga ou de Chico Science. Tudo é desenhado de forma genérica, no estilo.

### CENA 7: Do mar ao sertão · **cordel** · ~60 s

> No mapa, Pernambuco é uma faixa estreita e comprida, que vai do mar até o coração do Nordeste. No litoral, o Recife nasce entre rios, pontes e arrecifes. O nome da cidade vem deles. A mais de quinhentos quilômetros da costa fica Fernando de Noronha, patrimônio natural da humanidade. Rumo ao interior, a Zona da Mata ainda guarda os canaviais. No Agreste, as feiras ditam o ritmo das cidades. No Sertão, a Caatinga, um bioma que só existe no Brasil, resiste ao sol e à seca. No extremo oeste, o Rio São Francisco muda a paisagem. Em Petrolina, a irrigação faz o semiárido produzir uvas, mangas e até vinho. Do azul ao dourado, são mais de setecentos quilômetros de contrastes.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 7.1 | No mapa, Pernambuco é uma faixa estreita e comprida, que vai do mar até o coração do Nordeste. | "faixa" | A faixa de PE é entalhada em xilogravura, de leste a oeste | — | Viaja; enquadra a faixa inteira | Goiva riscando madeira |
| 7.2 | No litoral, o Recife nasce entre rios, pontes e arrecifes. | "arrecifes" | Ondas em xilogravura batendo nos arrecifes; pontes sobre o Capibaribe | — | Aproxima no litoral | Ondas |
| 7.3 | O nome da cidade vem deles. | "nome" | "ARRECIFES" perde as primeiras letras e vira "RECIFE" | RECIFE | Aproxima | Prensa |
| 7.4 | A mais de quinhentos quilômetros da costa fica Fernando de Noronha, patrimônio natural da humanidade. | "Noronha" | **Foto do Morro Dois Irmãos (CC)** em alto contraste de gravura, ligada à costa por linha pontilhada | Fernando de Noronha | Desliza mar adentro | Gaivotas, mar |
| 7.5 | Rumo ao interior, a Zona da Mata ainda guarda os canaviais. | "canaviais" | Canavial em xilogravura (traços verticais) | Zona da Mata | Viaja para o oeste | Vento na cana |
| 7.6 | No Agreste, as feiras ditam o ritmo das cidades. | "feiras" | Barraca de feira em xilogravura | Agreste | Desliza | Burburinho de feira (baixo) |
| 7.7 | No Sertão, a Caatinga, um bioma que só existe no Brasil, resiste ao sol e à seca. | "Caatinga" | Mandacaru e sol grande em xilogravura; o papel esquenta para o ocre | Caatinga | Desliza; luz mais quente | Vento seco, cigarras |
| 7.8 | No extremo oeste, o Rio São Francisco muda a paisagem. | "São Francisco" | O rio é entalhado em azul na ponta oeste da faixa | — | Desliza ao longo do rio | Água correndo |
| 7.9 | Em Petrolina, a irrigação faz o semiárido produzir uvas, mangas e até vinho. | "uvas" → "vinho" | Cacho de uva, manga e garrafa em xilogravura, um por palavra | Petrolina | Aproxima | Pena ×3 |
| 7.10 | Do azul ao dourado, são mais de setecentos quilômetros de contrastes. | "setecentos" | A faixa inteira acende, do azul ao dourado | +700 km | Recua até ver a faixa toda | A trilha sobe |

**Imagens:** Morro Dois Irmãos (Noronha) com licença CC no Commons, com crédito. Todo o resto é desenhado.

### CENA 8: O próximo capítulo · **cordel** · ~35 s

> A Pernambuco de hoje também carrega desafios antigos. A desigualdade que nasceu nos engenhos ainda aparece nas cidades e no campo. No Sertão, a água continua sendo uma questão de sobrevivência. Ao mesmo tempo, no bairro onde funcionou a primeira sinagoga das Américas, hoje fica o Porto Digital, um dos maiores parques de tecnologia do país. Universidades, artistas, cientistas e agricultores escrevem, todos os dias, o próximo capítulo.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 8.1 | A Pernambuco de hoje também carrega desafios antigos. | "desafios" | Página nova do folheto, quase vazia | — | Viaja; ritmo mais lento | Piano solo; a trilha baixa |
| 8.2 | A desigualdade que nasceu nos engenhos ainda aparece nas cidades e no campo. | "desigualdade" | Duas casas em xilogravura, um sobrado e um casebre, **sem números** | — | Aproxima | Lápis |
| 8.3 | No Sertão, a água continua sendo uma questão de sobrevivência. | "água" | Cisterna de placas em xilogravura; uma gota cai | — | Desliza | Gota d'água |
| 8.4 | Ao mesmo tempo, no bairro onde funcionou a primeira sinagoga das Américas, hoje fica o Porto Digital, um dos maiores parques de tecnologia do país. | "sinagoga" → "Porto Digital" | A sinagoga (de 4.8, agora em traço) e, ao lado, prédios com circuitos gravados como desenho de cordel | Porto Digital | Desliza de um ao outro | Teclado ao longe |
| 8.5 | Universidades, artistas, cientistas e agricultores escrevem, todos os dias, o próximo capítulo. | "próximo capítulo" | Uma pena escreve uma linha nova no folheto | — | Aproxima na pena | Pena; a trilha começa a subir |

### FINAL: O que é ser pernambucano · **cordel**, fechando na **mesa** · ~40 s

> Então, o que faz de Pernambuco um lugar tão singular? Não são só as datas. É a coragem de quem disse "república" antes do Brasil. É a resistência de Palmares. É o frevo que ferve, o maracatu que ecoa e o forró que atravessa o sertão. É um povo que transformou dor em música e luta em memória. Para entender o Brasil, é preciso passar por Pernambuco. E para entender Pernambuco, é preciso conhecer o seu povo.

| # | Narração | Gatilho | Destaque | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| F.1 | Então, o que faz de Pernambuco um lugar tão singular? | "singular" | Capa do folheto com o título em tipo de madeira | — | Recua até a capa | Respiro; só piano |
| F.2 | Não são só as datas. | "datas" | As datas do filme (1535, 1630, 1654, 1695, 1817, 1824) passam e se apagam | — | Recua | Máquina distante |
| F.3 | É a coragem de quem disse "república" antes do Brasil. | "república" | Carimbo "REPÚBLICA" da Abertura reacende | — | Viagem rápida e suave até ele | Batida |
| F.4 | É a resistência de Palmares. | "Palmares" | A Serra da Barriga (C3) reacende | — | Viagem | Tambor |
| F.5 | É o frevo que ferve, o maracatu que ecoa e o forró que atravessa o sertão. | "frevo" / "maracatu" / "forró" | Sombrinha, alfaia e sanfona, uma por palavra | — | Três viagens curtas | Metais / alfaia / sanfona |
| F.6 | É um povo que transformou dor em música e luta em memória. | "música" → "memória" | O livro-registro (C2) e a sombrinha (C6) lado a lado | — | Recua | A trilha cheia |
| F.7 | Para entender o Brasil, é preciso passar por Pernambuco. | "Pernambuco" | Mapa do Brasil com PE aceso | — | Recua bastante | — |
| F.8 | E para entender Pernambuco, é preciso conhecer o seu povo. | "povo" | **A bandeira de PE** cobre o centro; a câmera recua e revela **a mesa inteira, com o folheto aberto sobre ela** | **PERNAMBUCO** · Uma história que vive em seu povo. | Recua até o plano mais aberto do filme e para devagar | A trilha resolve; grave final |

Depois do F.8: tela de créditos com todas as imagens (autor e licença), a voz, as trilhas e os efeitos.

---

## 3. Imagens

Todas no Wikimedia Commons. **Confirmar a licença na página de cada arquivo** e anotar em `creditos.csv`.

| Imagem | Cena | Licença | Status / alternativa |
|---|---|---|---|
| Antônio Parreiras, *Estudo para Frei Caneca* (c. 1918) | 5 | Domínio público | ✅ Baixada e usada no piloto |
| Pinturas rupestres do Vale do Catimbau | 1.4 | CC (conferir) | Figuras redesenhadas em traço |
| Frans Post, vista de Olinda (século XVII) | 2.2, 4.3 | Domínio público | Casario desenhado |
| Frans Post, pintura de engenho | 2.4 | Domínio público | Engenho em traço |
| Serra da Barriga (foto) | 3.2, F.4 | CC (conferir) | Serra desenhada |
| Georg Marcgraf, *Brasilia qua parte paret Belgis* (1647) | 4.4 | Domínio público | Mapa desenhado |
| Jan de Baen, retrato de Johan Maurits | 4.5 | Domínio público | Silhueta + nome |
| Sinagoga Kahal Zur Israel, fachada (foto) | 4.8 | CC (conferir) | Fachada em traço |
| Victor Meirelles, *Batalha dos Guararapes* (1875–79) | 4.13 | Domínio público | Mapa de tropas |
| Morro Dois Irmãos, Fernando de Noronha (foto) | 7.4 | CC (conferir) | Ilha em xilogravura |

**Não usar:**
- **Murillo La Greca** (ele morreu em 1985, e a obra está protegida).
- **Fotos de Luiz Gonzaga ou de Chico Science** (protegidas).
- **Obras de Vitalino e de J. Borges** (protegidas).
- **Retratos "de Zumbi" ou "de Duarte Coelho"** (não existe imagem autêntica, e uma imagem inventada passaria por real).

**Na prática:** o Wikimedia limita requisições deste servidor (erro 429). Baixe com intervalos e use desenhos provisórios enquanto isso.

## 4. Trilha (arco)

| Trecho | Música | Momento-chave |
|---|---|---|
| Abertura | Grave, suspense | **Corta no carimbo "REPÚBLICA"** (A.5); volta com o tema no título (A.6) |
| C1 | Cordas leves, misteriosas | — |
| C2 | Cordas baixas, sério | **Some em "custo"** (2.5) e volta em "feridas" (2.9) |
| C3 | Percussão contida | Some em 1695 (3.4); volta digna em "Consciência" (3.5) |
| C4 | Percussão militar | **Morre no carimbo** de 1654 (4.14); volta em 4.15 |
| C5 | Trilha do piloto (cordas tensas → resolução) | Morre em "republicano" e em "fuzilado"; resolve na bandeira de 1917 |
| C6 | **Troca para regional:** alfaias, metais de frevo, sanfona | Batidas casadas com os objetos; guitarra no manguebeat |
| C7 | Violão e cordas abertas | Clareia do mar ao sertão; sobe em "setecentos" |
| C8 | Piano solo | Começa a subir em "próximo capítulo" |
| Final | Tema da Abertura + percussão regional | Resolve em "povo" (F.8) |

**A gerar no ElevenLabs Music**, todas instrumentais e niveladas com `trilha_abaixo_da_voz: 14`:
- orquestral histórica (Abertura a C4, ~3 min)
- a trilha da C5 (já existe)
- regional (C6, ~75 s)
- ambiente (C7–C8, ~95 s)
- final (~40 s)

## 5. Efeitos sonoros

| Efeito | Onde | Status |
|---|---|---|
| Máquina de escrever, papel caindo | várias | ✅ temos |
| Carimbo, pena, sino distante, salva distante | várias | ✅ temos (piloto) |
| Vento, ondas, folhas, mata, gaivotas | A, C1, C3, C7 | gerar |
| Madeira rangendo + mar (caravela), canhão distante | 2.1, 4.1 | gerar |
| Moenda ao longe, fogo crepitando | 2.4, 4.3 | gerar |
| Tambor militar, passos marchando, mosquetes ao longe | C3, C4 | gerar |
| Página virando, prensa de impressão, goiva na madeira | C2, C6, C7 | gerar |
| Vinhetas: metais de frevo, alfaia, sanfona, riff de guitarra | C6, F.5 | gerar (2–4 s cada) |
| Feira, cigarras + vento seco, água correndo, gota | C7, C8 | gerar |
| Teclado ao longe | 8.4 | gerar |

## 6. Para conferir antes de publicar

As datas e os fatos da **Cena 5** já foram conferidos (Frei Caneca, os 75 dias, Alagoas, a bandeira de 1917 com as três estrelas originais). Os demais estão listados com observações no fim de [`roteiro-v2.md`](roteiro-v2.md). Os pontos mais sensíveis:
- os nomes dos povos indígenas (C1);
- a estimativa de africanos escravizados (C2; conferir no SlaveVoyages);
- "primeira sinagoga das Américas" (C4, C8);
- "maiores parques de tecnologia do país" (C8).

## 7. Ordem de produção sugerida

1. Gerar a **narração completa** de uma vez (~7 min) e transcrever com o tempo de cada palavra.
2. Gerar as trilhas e os efeitos que faltam.
3. Produzir **cena por cena**, salvando no GitHub a cada uma: Abertura → C1 → C2 → C3 → C4 → C5 (reaproveitando o piloto) → C6 (virada para o cordel) → C7 → C8 → Final.
4. Juntar tudo num único `plano.json` e num único mundo, e renderizar o plano-sequência final (~45 min de render).
5. Créditos, conferência final (sincronia, câmera, volume) e cortes 9:16.

**Estimativa:** de 8 a 10 h de trabalho em várias sessões, e cerca de 20.000 créditos no ElevenLabs (≈ US$ 2).
