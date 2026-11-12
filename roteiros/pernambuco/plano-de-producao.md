# Pernambuco: Terra de História, Coragem e Revolução — plano de produção

Adaptação do [roteiro original](roteiro-original.md) para a skill **estilo-documentario**: tudo desenhado em código sobre um único "mundo", com câmera contínua, um destaque por vez sincronizado com a palavra, fotos só com licença livre e efeitos sonoros reais.

> **Status:** rascunho para aprovação. Os tempos exatos de cada palavra-gatilho só existem depois de gerar a narração. Até lá a coluna "gatilho" indica a **palavra**, não o segundo.

## Resumo

| Item | Decisão |
|---|---|
| Duração real | **~6 min de fala** (817 palavras) + respiros ≈ **6,5–7 min**. O "15 min" do ChatGPT não bate com o texto. |
| Formato | 16:9, 1920×1080, 30 fps. Depois, cortes 9:16 por cena (cada cena funciona sozinha como Reels). |
| Narrador | Voz grave pt-BR. Sugestão: "Nassif" (ElevenLabs), a mesma do teste. |
| Mundo | Uma grande **mesa de arquivo pernambucano**. Cada cena é uma região da mesa; a câmera viaja entre elas sem cortes. |
| Imagens reais | Só domínio público ou CC (Wikimedia Commons), com crédito em `creditos.csv`. O resto é desenhado em código. |
| Produção | Cena por cena: cada uma vira um projeto HyperFrames e uma prévia aprovada antes da próxima. No fim, as 8 são unidas num único plano-sequência. |

## O mundo (mapa da mesa)

```
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  C2 COLÔNIA            C3 HOLANDESES             C4 1817 / 1824               │
 │  mapa antigo,          pintura Guararapes,       documentos, bandeira 1817,   │
 │  engenho desenhado,    mapa de tropas,           retrato Frei Caneca,         │
 │  cana, açúcar          retrato de Nassau         carimbos, jornal             │
 │                                                                              │
 │            C1 / C8  CENTRO: GRANDE MAPA DE PERNAMBUCO + TÍTULO               │
 │            (abertura e final; a câmera volta aqui e recua até ver tudo)      │
 │                                                                              │
 │  C7 DESAFIOS           C6 TERRITÓRIO             C5 CULTURA                   │
 │  painel de anotações,  faixa litoral→sertão,     sombrinha de frevo, alfaia,  │
 │  gráficos à mão,       Noronha, Catimbau,        cordel em xilogravura,       │
 │  pessoas (silhuetas)   rio São Francisco         sanfona, boneco de barro     │
 └──────────────────────────────────────────────────────────────────────────────┘
```

**Arte geral:** papel envelhecido, luz quente de luminária, grão de filme. Cada região tem um tom: C2 sépia, C3 pólvora/cinza, C4 vermelho e azul da bandeira, C5 cores vivas do frevo (amarelo, vermelho, verde, azul), C6 do azul ao dourado, C7 neutro, C8 todas.

**Legenda das colunas:**
- **Gatilho:** palavra que dispara o destaque.
- **Destaque:** o único elemento aceso naquele momento.
- **Texto:** o que aparece escrito na tela (no máximo 6 palavras).
- **Câmera:** aproxima, recua, desliza, viaja ou mergulha.
- **Som:** efeito pontual. A trilha está na seção própria.

---

## CENA 1 — Antes de existir o Brasil (~40 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 1.1 | Antes de o Brasil se tornar uma nação, esta terra já tinha história. | "terra" | Mapa de PE surge do escuro, sem divisões políticas | — | Aproxima devagar, da escuridão ao mapa | Vento + ondas, grave longo |
| 1.2 | Antes das grandes cidades, antes dos engenhos e das revoluções, povos indígenas viviam entre o litoral, as matas e o sertão. | "litoral" → "matas" → "sertão" | Três faixas do mapa acendem em sequência (azul, verde, ocre) | — | Desliza de leste para oeste pelo mapa | Ondas → folhas → vento seco |
| 1.3 | Séculos depois, este território seria palco de disputas entre impérios, batalhas históricas e movimentos que desafiariam o poder. | "impérios" | Duas bandeirinhas (Portugal e Holanda) espetadas no mapa | — | Recua um pouco | Papel + alfinete ×2 |
| 1.4 | Aqui, a liberdade se tornou bandeira. A resistência atravessou gerações. E a cultura transformou a história em identidade. | "bandeira" | Bandeira de 1817 desenhada em código desce sobre o mapa | — | Aproxima na bandeira | Tecido tremulando |
| 1.5 | Esta é a história de Pernambuco. | "Pernambuco" | **Título datilografado** | PERNAMBUCO | Para quase (drift lento) | Máquina de escrever + impacto grave; trilha cresce |
| 1.6 | Uma terra que não apenas participou da formação do Brasil, mas ajudou a mudar seus caminhos. | "caminhos" | Linha pontilhada sai de PE e corre pelo contorno do Brasil | Terra de História, Coragem e Revolução | Recua até mostrar a mesa toda (vista geral) | Caneta riscando |

**Imagens:** nenhuma foto. Mapa, bandeira e título em código.

## CENA 2 — A terra antes da colonização (~42 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 2.1 | Muito antes da chegada dos portugueses, diversos povos indígenas habitavam o território que hoje conhecemos como Pernambuco. | "indígenas" | Mapa etnográfico com nomes de povos (Caetés, Potiguaras, Tabajaras, Xukuru, Fulni-ô; **conferir com fonte**) | Povos originários | Viaja do centro para a região C2 | Folhas, pássaros ao longe |
| 2.2 | Eles possuíam línguas, tradições, conhecimentos e formas próprias de organização. | "línguas" | Quatro ícones desenhados acendem um a um (fala, grafismo, planta medicinal, aldeia), um por palavra | — | Desliza pelos ícones | Pena traçando ×4 |
| 2.3 | A partir do século XVI, a colonização portuguesa transformaria profundamente esse território. | "século XVI" | Caravela desenhada cruza o litoral do mapa antigo | Século XVI | Recua e desliza com a caravela | Madeira rangendo + mar |
| 2.4 | A capitania de Pernambuco se tornaria um dos principais centros de produção de açúcar da América portuguesa. | "açúcar" | **Pintura de engenho de Frans Post** cai na mesa | Capitania de Pernambuco | Aproxima na pintura | Foto/papel caindo |
| 2.5 | Mas a riqueza dos engenhos tinha um preço humano devastador: a escravização de africanos e seus descendentes, a violência colonial e a expropriação de terras indígenas. | "preço humano" | A pintura apaga; correntes **não**. Um livro-registro antigo abre e a linha "escravizados" é sublinhada em vermelho | — | Aproxima devagar, tom sério | Música some; só ambiente. Página virando |
| 2.6 | O açúcar trouxe riqueza para poucos. E deixou marcas profundas na sociedade brasileira. | "marcas" | Torrão de açúcar desenhado se desfaz em pó sobre o mapa | — | Recua | Silêncio → grave baixo |

**Imagens:** Frans Post, *Engenho* (século XVII, **domínio público**, Commons). O mapa antigo é a base da região: Georg Marcgraf, *Brasilia qua parte paret Belgis* (1647, **domínio público**).
**Cuidado:** não usar imagens de sofrimento como espetáculo. A violência é contada por documento e texto, não por cena.

## CENA 3 — Quando Pernambuco foi disputado por impérios (~42 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 3.1 | Em 1630, uma poderosa ofensiva holandesa tomou Olinda e Recife. | "1630" → "Olinda" | Data datilografada; depois setas da frota holandesa avançam no mapa até Olinda e Recife | 1630 | Viaja de C2 para C3 seguindo as setas | Máquina de escrever → canhão distante |
| 3.2 | O controle do açúcar e das rotas comerciais transformou Pernambuco em um território estratégico. | "rotas" | Linhas de rota atravessam o Atlântico até a Europa | — | Recua (mapa oceânico) | Caneta riscando longo |
| 3.3 | Durante a administração de Maurício de Nassau, Recife passou por importantes transformações urbanas, enquanto a economia continuava profundamente ligada à escravidão. | "Nassau" | **Retrato de Johan Maurits** (Jan de Baen) cai na mesa | Maurício de Nassau | Aproxima no retrato | Papel caindo |
| 3.3b | (mesma frase) | "urbanas" | Planta da Cidade Maurícia (mapa de época) acende ao lado; o retrato apaga | — | Desliza para a planta | — |
| 3.4 | Mas o domínio holandês encontraria resistência. | "resistência" | Mapa escurece; um ponto vermelho pulsa nos Guararapes | — | Aproxima | Tambor militar ×1 |
| 3.5 | Em 1648 e 1649, as Batalhas dos Guararapes marcaram momentos decisivos de uma longa luta. | "Guararapes" | **Pintura de Victor Meirelles, *Batalha dos Guararapes*** cai na mesa. A câmera percorre a pintura | 1648 · 1649 | Mergulha na pintura e desliza por ela | Tambores + mosquetes ao longe |
| 3.6 | Em 1654, os holandeses deixaram Pernambuco. | "1654" | Bandeirinha holandesa é arrancada do mapa | 1654 | Recua | Alfinete saindo + **carimbo** (a música morre) |
| 3.7 | Aquelas batalhas entrariam para a memória nacional como símbolos de resistência e de articulação entre diferentes grupos da sociedade colonial. | "memória" | A pintura volta a acender em plano geral | — | Recua lento | Trilha volta suave |

**Imagens (domínio público, conferir a página):** Jan de Baen, retrato de Johan Maurits (c. 1668); Victor Meirelles, *Batalha dos Guararapes* (1875–79); planta de Mauritsstad (século XVII).
**Regra do roteiro original mantida:** nada de reconstituição fingindo ser imagem real. Pinturas são apresentadas como pinturas.

## CENA 4 — A revolução que desafiou a monarquia (~48 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 4.1 | Em 1817, Pernambuco escreveu um dos capítulos mais ousados da história política do Brasil. | "1817" | Data datilografada em folha timbrada | 1817 | Viaja de C3 para C4 | Máquina de escrever |
| 4.2 | Insatisfeitos com os impostos, o domínio da monarquia portuguesa e a falta de autonomia, revolucionários desafiaram a ordem estabelecida. | "impostos" → "monarquia" → "autonomia" | Três palavras circuladas em vermelho num documento, uma por vez | — | Desliza pelo documento | Caneta circulando ×3 |
| 4.3 | No dia 6 de março, nasceu um governo republicano em Pernambuco. | "6 de março" | **Carimbo "GOVERNO REPUBLICANO"** | 6 de março de 1817 | Aproxima com tremor no impacto | **Carimbo** (a música morre e fica só o sino) |
| 4.4 | Era uma experiência revolucionária, anos antes da Independência do Brasil. | "Independência" | Linha do tempo curta: 1817 ●——● 1822, com o intervalo destacado | — | Recua | Sino distante |
| 4.5 | O movimento foi derrotado, mas suas ideias continuaram vivas. | "ideias" | A bandeira de 1817 (desenhada) volta a acender e tremula | — | Aproxima na bandeira | Tecido; a trilha volta |
| 4.6 | Em 1824, Pernambuco voltaria a desafiar o poder central, agora na Confederação do Equador. | "Confederação" | Mapa do Nordeste: províncias da Confederação acendem | 1824 · Confederação do Equador | Desliza no mapa | Máquina de escrever |
| 4.7 | Entre seus personagens estava Frei Caneca, que se tornaria um símbolo da luta contra o autoritarismo imperial. | "Frei Caneca" | **Retrato de Frei Caneca** cai na mesa, grande (≥ 60% da altura) | Frei Caneca | Aproxima no retrato | Papel caindo |
| 4.8 | A repressão foi severa. Mas a história registrou uma característica que atravessaria gerações: o desejo de autonomia. | "autonomia" | O retrato apaga; a palavra "autonomia" do 4.2 reacende no documento | o desejo de autonomia | Recua até a região toda | Passos → silêncio → trilha retoma |

**Imagens:** retrato de Frei Caneca (século XIX, **domínio público**; conferir autor e acervo na página). A bandeira de 1817 é desenhada em código (arco-íris, estrela, sol e cruz sobre azul e branco).
**Fontes do roteiro original:** Arquivo Nacional e UFF (citações do ChatGPT; conferir antes de publicar).

## CENA 5 — A cultura que conquistou o mundo (~43 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 5.1 | Pernambuco não é feito apenas de batalhas e revoluções. | "apenas" | Os objetos de guerra de C3 e C4 apagam ao fundo | — | Viaja de C4 para C5; a mesa clareia | A trilha orquestral sai e entra uma percussão leve |
| 5.2 | É também uma terra onde a história ganhou ritmo, dança e poesia. | "ritmo" | Batida visual: os objetos de C5 pulsam no compasso | — | Desliza | Primeira batida de alfaia |
| 5.3 | Nas ruas do Recife e de Olinda, nasceu o frevo. Uma mistura de música, movimento e energia que se tornaria patrimônio cultural da humanidade. | "frevo" | **Sombrinha de frevo desenhada** abre girando | FREVO | Aproxima na sombrinha | Metais de frevo (vinheta curta) |
| 5.3b | (mesma frase) | "humanidade" | Selo "Patrimônio da Humanidade · UNESCO · 2012" carimbado | UNESCO · 2012 | Recua um pouco | Carimbo |
| 5.4 | Nos tambores do maracatu, a herança africana atravessa gerações. | "maracatu" | **Alfaia desenhada** vibrando + foto de cortejo de maracatu (CC) | Maracatu | Desliza para a alfaia | Alfaias (loop curto) |
| 5.5 | No Agreste, o forró, o artesanato e as festas juninas mantêm vivas tradições que fazem parte da identidade nordestina. | "forró" | Sanfona desenhada abre e fecha; bandeirinhas juninas atravessam o quadro | — | Desliza | Sanfona (2 compassos) |
| 5.6 | Da literatura de cordel às esculturas de barro, Pernambuco transformou a criatividade popular em patrimônio. | "cordel" → "barro" | Folheto de cordel com capa em **estilo xilogravura desenhado por nós** e depois boneco de barro **genérico** desenhado | — | Desliza entre os dois | Papel + argila |
| 5.7 | Aqui, cultura não é apenas espetáculo. É memória, resistência e pertencimento. | "pertencimento" | Todos os objetos de C5 acendem juntos por um instante e voltam a um só: a sombrinha | — | Recua até a região toda | A batida para e fica um acorde |

**Imagens:** fotos de frevo e maracatu com licença CC BY ou CC BY-SA no Commons (crédito obrigatório: autor e licença na tela final).
**Direitos autorais:** **não** usar xilogravuras de artistas vivos ou recentes (ex.: J. Borges) nem fotos de obras de Mestre Vitalino (ainda protegidas). Desenhamos peças genéricas inspiradas no estilo.

## CENA 6 — Do litoral ao Sertão (~46 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 6.1 | Pernambuco é um território de contrastes extraordinários. | "contrastes" | Faixa horizontal de PE dividida em mesorregiões (Litoral → Zona da Mata → Agreste → Sertão → São Francisco) | — | Viaja de C5 para C6; enquadra a faixa inteira | Vento + mar misturados |
| 6.2 | No litoral, o Oceano Atlântico encontra praias, arrecifes e manguezais. | "arrecifes" | Ponta leste da faixa em azul; ondas desenhadas batendo nos arrecifes | — | Aproxima no litoral | Ondas |
| 6.3 | No arquipélago de Fernando de Noronha, a natureza revela uma das paisagens mais impressionantes do Brasil. | "Noronha" | **Foto do Morro Dois Irmãos (CC)** cai na mesa, fora da faixa, ligada por linha pontilhada (~545 km de Recife, mar adentro) | Fernando de Noronha | Desliza para a foto | Papel caindo + gaivotas |
| 6.4 | Mas Pernambuco vai muito além do mar. | "além" | A foto apaga; a câmera começa a ir para o oeste | — | Viaja para o oeste pela faixa | O mar some |
| 6.5 | No Agreste, as paisagens mudam, as feiras movimentam a economia e a cultura popular encontra novas formas de expressão. | "feiras" | Barraca de feira desenhada (lona, caixotes) no Agreste | Agreste | Aproxima | Burburinho de feira (baixo) |
| 6.6 | No Sertão, a Caatinga guarda uma biodiversidade singular. | "Caatinga" | **Foto do Vale do Catimbau (CC)**; a faixa vira ocre/dourado | Caatinga | Desliza; luz mais quente | Vento seco + cigarras |
| 6.7 | E às margens do Rio São Francisco, cidades como Petrolina mostram como a agricultura irrigada transformou parte da economia regional. | "São Francisco" → "irrigada" | O rio se desenha (traço azul); depois círculos verdes de irrigação aparecem às margens | Petrolina | Desliza ao longo do rio | Água correndo |
| 6.8 | Pernambuco é feito de muitos cenários. E em cada um deles existe uma história que merece ser contada. | "cenários" | A faixa inteira acende de ponta a ponta | — | Recua até ver a faixa toda | A trilha volta |

**Imagens:** Morro Dois Irmãos (Noronha) e Vale do Catimbau com licença CC no Commons (escolher na hora, com crédito).

## CENA 7 — O Pernambuco dos desafios (~40 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 7.1 | A história de Pernambuco também é a história de desafios que permanecem. | "desafios" | Prancheta de anotações na região C7 | — | Viaja de C6 para C7; ritmo mais lento | A trilha abaixa; piano solo |
| 7.2 | Um estado de grande riqueza cultural, econômica e humana, mas que ainda enfrenta desigualdades sociais, dificuldades de infraestrutura e diferenças marcantes entre suas regiões. | "desigualdades" | Duas barras desenhadas à mão de alturas diferentes (litoral × sertão), **sem números inventados**: só com dado real e fonte (ex.: IBGE) | — | Aproxima | Lápis desenhando |
| 7.3 | Nas cidades, a população busca melhores serviços públicos, oportunidades e qualidade de vida. | "cidades" | Silhuetas de prédios do Recife em traço | — | Desliza | Cidade ao longe (baixo) |
| 7.4 | No interior, a convivência com o semiárido exige conhecimento, tecnologia e políticas de desenvolvimento. | "semiárido" | Cisterna de placas desenhada (símbolo da convivência com o semiárido) | — | Desliza | Água caindo em cisterna |
| 7.5 | Ao mesmo tempo, universidades, empreendedores, trabalhadores e comunidades constroem novos caminhos. | "novos caminhos" | Quatro ícones ligados por linhas que formam um caminho | — | Recua um pouco | Pena traçando |
| 7.6 | O Pernambuco do futuro não será definido apenas pelo seu passado. | "futuro" | A linha do tempo de C4 aparece ao fundo e se estende para a direita, pontilhada | — | Desliza para a direita | A trilha começa a subir |
| 7.7 | Será construído pelas escolhas realizadas no presente. | "presente" | Um marcador "HOJE" é carimbado na linha | HOJE | Aproxima | Carimbo leve |

**Imagens:** nenhuma foto (evita expor pessoas reais). Tudo desenhado. **Pendente:** se 7.2 mostrar números, eles precisam de fonte oficial citada na tela.

## CENA 8 — O que significa ser pernambucano? (~57 s)

| # | Narração | Gatilho | Destaque (único) | Texto | Câmera | Som |
|---|---|---|---|---|---|---|
| 8.1 | O que faz de Pernambuco um lugar tão singular? | "singular" | Volta ao grande mapa central | — | Viaja de C7 até o centro | Respiro; só piano |
| 8.2 | Seriam suas revoluções? Sua cultura? Suas paisagens? | "revoluções" → "cultura" → "paisagens" | Três flashes de câmera: a bandeira de 1817, a sombrinha e a foto do Catimbau, um por palavra | — | Três viagens rápidas e suaves, com a spline sem cortes | Batida suave em cada palavra |
| 8.3 | Talvez seja algo que não possa ser explicado apenas por datas ou acontecimentos. | "datas" | As datas da mesa (1630, 1654, 1817, 1824, 2012) acendem e apagam | — | Recua | Máquina de escrever, distante |
| 8.4 | Pernambuco está na força de quem trabalha. Na criatividade de quem transforma dificuldades em oportunidades. Na coragem de quem questiona. E na memória de quem preserva suas raízes. | "força" / "criatividade" / "coragem" / "memória" | Quatro objetos da mesa acendem, um por palavra (feira, cordel, Frei Caneca, mapa antigo) | — | Viagem contínua entre os quatro | Trilha crescendo |
| 8.5 | Está no frevo que ocupa as ruas, no silêncio do Sertão, nos rios que atravessam o território e nas histórias transmitidas de geração em geração. | "frevo" / "silêncio" / "rios" | Sombrinha → Catimbau → rio, um por palavra; em "silêncio" **a música para por 1 s** | — | Viagem | Metais curtos → silêncio → água |
| 8.6 | Mais do que um estado brasileiro, Pernambuco é um encontro de povos, lutas, sonhos e tradições. | "encontro" | Linhas ligam todas as regiões da mesa ao mapa central | — | Recua bastante | Trilha cheia |
| 8.7 | Uma terra que carrega marcas do passado, enfrenta desafios no presente e continua escrevendo sua própria história. | "escrevendo" | Pena escreve uma linha nova na faixa do tempo | — | Aproxima na pena | Pena escrevendo |
| 8.8 | Porque para entender Pernambuco não basta olhar para o mapa. | "mapa" | Mapa central em plano geral | — | **Recua até ver a mesa inteira** | — |
| 8.9 | É preciso conhecer o seu povo. | "povo" | Bandeira de Pernambuco (atual, em código) cobre o centro; título final | PERNAMBUCO · Uma história que vive em seu povo. | Para devagar | Trilha resolve e termina; grave final |

Depois do 8.9: tela de créditos com todas as imagens (autor e licença), a voz, a trilha e os efeitos.

---

## Trilha sonora (arco)

| Trecho | Música | Momento-chave |
|---|---|---|
| C1 | Orquestral grave, suspense, cresce | Sobe no título "PERNAMBUCO" (1.5) |
| C2 | Cordas baixas, sério | **Some** em "preço humano" (2.5) e volta só em C3 |
| C3 | Percussão militar contida | **Morre no carimbo** de 1654 (3.6); volta suave em 3.7 |
| C4 | Tensão (cordas e sino) | **Morre no carimbo** de 6 de março (4.3); volta em "ideias" (4.5) |
| C5 | Troca para ritmo regional: alfaias, metais de frevo, sanfona | Batidas casadas com os objetos |
| C6 | Ambiente aberto (violão e cordas) | Clareia do mar para o sertão |
| C7 | Piano solo, contido | Começa a subir em "futuro" (7.6) |
| C8 | Crescendo final com tema da C1 + percussão regional | **Silêncio de 1 s** em "silêncio do Sertão" (8.5); resolve em "povo" (8.9) |

Gerar no ElevenLabs Music: 4 faixas (C1–C4 orquestral, C5 regional, C6–C7 ambiente, C8 final), cada uma com o tamanho da sua parte, todas **instrumentais**.

## Biblioteca de efeitos sonoros

| Efeito | Onde | Como obter |
|---|---|---|
| Máquina de escrever | datas e título | já temos (teste) |
| Papel/foto caindo | fotos que entram | já temos (teste) |
| Carimbo | 1654, 6 de março, UNESCO, HOJE | sintetizado no teste; gerar um melhor no ElevenLabs |
| Vento, ondas, folhas, pássaros | C1, C2, C6 | ElevenLabs SFX |
| Madeira rangendo + mar (caravela) | 2.3 | ElevenLabs SFX |
| Canhão distante, tambor militar, mosquetes ao longe | C3 | ElevenLabs SFX (distantes, sem violência explícita) |
| Caneta/pena riscando e circulando | C4, C7, C8 | ElevenLabs SFX |
| Sino de igreja distante | C4 | ElevenLabs SFX |
| Tecido/bandeira tremulando | 1.4, 4.5 | ElevenLabs SFX |
| Alfaia (maracatu), metais curtos de frevo, sanfona | C5, C8 | ElevenLabs Music/SFX (vinhetas de 2–4 s) |
| Feira, cidade ao longe | 6.5, 7.3 | ElevenLabs SFX (bem baixo) |
| Cigarras + vento seco | 6.6 | ElevenLabs SFX |
| Água correndo, água em cisterna | 6.7, 7.4, 8.5 | ElevenLabs SFX |

## Imagens: lista de busca

Todas no Wikimedia Commons. **Confirmar a licença na página de cada arquivo** e anotar em `creditos.csv`.

| Imagem | Cena | Licença esperada | Alternativa se não houver |
|---|---|---|---|
| Georg Marcgraf, *Brasilia qua parte paret Belgis* (1647) | C2/C3 (base) | Domínio público | Mapa desenhado em código |
| Frans Post, pintura de engenho (século XVII) | 2.4 | Domínio público | Engenho desenhado em traço |
| Jan de Baen, retrato de Johan Maurits | 3.3 | Domínio público | Silhueta + nome |
| Planta de Mauritsstad/Recife (século XVII) | 3.3b | Domínio público | Planta desenhada |
| Victor Meirelles, *Batalha dos Guararapes* | 3.5 | Domínio público | Mapa de tropas desenhado |
| Retrato de Frei Caneca (século XIX) | 4.7 | Domínio público | Silhueta + nome |
| Foto de frevo (passistas) | 5.3 | CC BY / CC BY-SA | Só a sombrinha desenhada |
| Foto de cortejo de maracatu | 5.4 | CC BY / CC BY-SA | Só a alfaia desenhada |
| Morro Dois Irmãos, Fernando de Noronha | 6.3 | CC BY / CC BY-SA | Ilha desenhada |
| Vale do Catimbau | 6.6 | CC BY / CC BY-SA | Paisagem desenhada |

Desenhado em código (sem foto): mapas de PE e do Nordeste, bandeira de 1817, bandeira atual de PE, caravela, ícones, sombrinha, alfaia, sanfona, cordel, boneco de barro, feira, cisterna, prédios, linhas do tempo.

## Perguntas para aprovar antes de construir

1. **Duração:** a narração dá ~6,5 min. Mantemos assim ou você quer acrescentar texto para chegar mais perto de 10–15 min?
2. **Narrador:** usamos o "Nassif" do teste?
3. **Cena 2.5 (escravidão):** concorda com tratar o tema por documento (livro-registro) em vez de imagem de pessoas?
4. **Cena 7.2:** mostramos números reais com fonte (IBGE) ou só a comparação visual, sem números?
5. **Ordem de produção:** começamos pela **Cena 4 (1817)** como piloto, que é a mais forte, e seguimos para as outras depois da aprovação?

## Custo e tempo estimados

| Item | Estimativa |
|---|---|
| Voz (ElevenLabs, ~6,5 min) | ~4.500 créditos (≈ US$ 0,45) |
| 4 trilhas (~6,5 min de música no total) | ~12.000 créditos (≈ US$ 1,20) |
| ~25 efeitos sonoros | ~1.250 créditos |
| Render | ~35–45 min de máquina para o vídeo inteiro (mais as prévias por cena) |
