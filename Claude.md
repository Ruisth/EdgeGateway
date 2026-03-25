# Dissertação de Mestrado — C2DTA

## Sobre o projeto
Dissertação de mestrado no ISCTE sobre Consumer-Controlled Digital 
Twin Architecture (C2DTA). O tema integra Digital Twins, Self-Sovereign 
Identity (SSI), Blockchain e o Personal Data Ecosystem.

## Documentação de referência
- O artigo base está em `docs/EdgeGateway_Paper.pdf` — lê-o antes 
  de escrever qualquer secção
- Os materiais da cadeira estão em `docs/` (guidelines, SLR, PRISMA, 
  Design Science Research)

## Tecnologias do C2DTA
Eclipse Ditto, Hyperledger Fabric/Indy, Hyperledger Aries, IPFS, 
DIDComm, MQTT, Web of Things

## Regras de escrita
- LaTeX, em inglês académico
- Usar biblatex para referências (ficheiro references/bibliography.bib)
- Cada capítulo num ficheiro separado em chapters/
- Compilar com: pdflatex main && biber main && pdflatex main
- Estilo: voz ativa, presente do indicativo, frases concisas

## Estrutura da dissertação
1. Introduction (chapters/01-introduction.tex)
2. State of the Art (chapters/02-state-of-art.tex)
3. C2DTA Architecture (futuro)
4. Results and Discussion (futuro)
5. Conclusions (futuro)