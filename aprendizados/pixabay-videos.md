# Pixabay: vídeos (pixabay.com/pt/videos)

Estudado pela busca na web; o site está bloqueado na rede desta sessão. **Confira a licença e a documentação oficiais antes de usar.**

## O que é
Banco gratuito de mídia: vídeos (filmagens e animações), fotos, ilustrações, vetores, **músicas e efeitos sonoros**. Os vídeos são buscados por palavra-chave, categoria, orientação e resolução (HD, Full HD e 4K, conforme o arquivo).

## Licença (Pixabay Content License)
- Uso **comercial e não comercial** gratuito, podendo modificar e copiar.
- **Atribuição opcional**, mas recomendada, especialmente em uso editorial.
- **Não pode:** revender ou redistribuir o arquivo sem modificação, montar um banco de mídia concorrente ou insinuar que pessoas ou marcas mostradas endossam algo.
- **Atenção:** pessoas, marcas e lugares nos vídeos podem ter direitos de imagem ou de marca, e o Pixabay **não garante** autorização de imagem. Em campanha comercial com pessoa identificável, cuidado.

## API (para automatizar a busca)
- Endpoint de vídeos: `https://pixabay.com/api/videos/?key=SUA_CHAVE&q=termo` (parâmetros úteis: `video_type` film|animation, `category`, `min_width`, `per_page`, `lang=pt`).
- A chave é gratuita e aparece na página da documentação depois do login.
- **Limite:** cerca de 100 requisições por 60 s (cabeçalhos `X-RateLimit-*`; acima disso, HTTP 429). Os resultados devem ser guardados em cache (orientação de 24 h) e os arquivos baixados, sem hotlink.
- Cada vídeo vem em vários tamanhos (large/medium/small/tiny) com o link de download.
- Músicas e efeitos sonoros ficam no site, mas não parecem estar na API.

## Como se relaciona com a skill estilo-documentario
- A skill **não usa** vídeos de banco: os quadros são desenhados em código. Isso continua igual.
- Possível uso futuro, se você quiser: **músicas, efeitos sonoros e texturas** (grão de filme, poeira, papel) do Pixabay como alternativa gratuita ao pack pago, registrando a origem em `creditos.csv`.

## Fontes
- Termos: https://pixabay.com/service/terms/
- Resumo da licença: https://pixabay.com/service/license/
- FAQ: https://pixabay.com/service/faq/
- API: https://pixabay.com/api/docs/
