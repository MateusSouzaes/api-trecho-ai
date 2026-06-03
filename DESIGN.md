# 🎨 Trecho.IA - Design System & UI/UX Guidelines

Este documento (`DESIGN.md`) define as regras estritas de interface de usuário (UI) e experiência do usuário (UX) para o frontend do Trecho.IA. 
**Instrução para a IA Geradora** Leia este documento inteiramente antes de gerar qualquer componente, tela ou código Tailwind. Siga estas diretrizes rigorosamente para manter a consistência Enterprise do SaaS.

---

## 1. 🌌 Filosofia de Design e Identidade Visual

O Trecho.IA é um SaaS B2B de Logística e FinOps (Gestão Financeira). A interface não pode parecer um e-commerce ou um app social. Ela deve transmitir **confiança, robustez, precisão matemática e alta eficiência**.
- **Scannable (Leitura Dinâmica):** O gestor da frota precisa bater o olho na tela e entender o lucro da viagem e os alertas críticos em menos de 3 segundos.
- **Data-Dense, mas Limpo:** Tabelas e formulários devem aproveitar bem o espaço da tela (densidade média/alta), mas com espaçamento (`padding` e `gap`) consistente para não sufocar o usuário.
- **The "Death of WhatsApp":** Toda comunicação e log de sistema deve parecer oficial e imutável.

### 1.1. Paleta de Cores (Tailwind Base)
Utilize estas cores exatas ao gerar as classes utilitárias:

* **Primary (Brand):** Azul Petróleo Profundo 
    * `bg-[#001A33]`, `text-[#001A33]`, `border-[#001A33]`
    * *Uso:* Sidebar, Topbar, Títulos principais (H1), botões de ação primária de alto risco.
* **Accent (Inovação/IA):** Teal / Verde-Agra Vibrante
    * `bg-[#00E6B8]`, `text-[#00E6B8]`, `border-[#00E6B8]`
    * *Uso:* Badges de "Processado por IA", botões de ação principal (Call to Action), links de destaque, KPIs positivos.
* **Backgrounds (Neutros):**
    * `bg-slate-50` ou `bg-gray-50` (Fundo principal da aplicação)
    * `bg-white` (Cards, Tabelas e Formulários)
* **Textos:**
    * `text-slate-900` (Texto principal)
    * `text-slate-500` (Texto secundário, labels, placeholders)

### 1.2. Cores Semânticas (Status Blindados)
Conforme regra de negócio de backend (C#), os status são estritos:
* 🟢 **Ativa / Sucesso:** `bg-emerald-100 text-emerald-800 ring-emerald-600/20`
* 🟡 **Pendente / Em Análise:** `bg-amber-100 text-amber-800 ring-amber-600/20`
* 🔴 **Bloqueado / Erro:** `bg-rose-100 text-rose-800 ring-rose-600/20`
* ⚫ **Suspenso / Inativo:** `bg-slate-100 text-slate-800 ring-slate-600/20`

---

## 2. 📐 Estrutura de Layout Base (App Shell)

Toda a aplicação desktop deve seguir o layout **Dashboard Shell**:

1.  **Sidebar (Menu Lateral):** * Fixa à esquerda (`w-64`, oculta em mobile).
    * Fundo Azul Petróleo (`bg-[#001A33]`).
    * Logo do Trecho.IA no topo.
    * Links de navegação com ícones (Lucratividade, Viagens, Frota, Pessoas, WhatsApp Central). Link ativo com `bg-white/10` e borda esquerda verde (`border-l-4 border-[#00E6B8]`).
2.  **Topbar (Barra Superior):**
    * Fundo branco, sombra sutil (`shadow-sm`).
    * Input de Busca Global rápido.
    * Perfil do usuário, IP-API tracker badge (segurança) e Sino de Notificações.
3.  **Main Content (Área de Conteúdo):**
    * Fundo `bg-slate-50`.
    * `padding` de `p-6` ou `p-8`.
    * Largura máxima de leitura (ex: `max-w-7xl mx-auto`).

---

## 3. 🧩 Padrões de Componentes

### 3.1. Cards de KPI (Key Performance Indicators)
* Devem conter: Título (Ex: Margem de Contribuição), Valor principal em destaque (Ex: R$ 45.200,00), e um subtexto de variação (Ex: +12% em relação ao mês passado em cor semântica verde).
* Estilo: `bg-white rounded-xl shadow-sm border border-slate-200 p-5`.

### 3.2. Tabelas de Dados (Data Tables)
* Cabeçalhos: Fundo levemente cinza (`bg-slate-50`), texto pequeno, uppercase, bold, e cor cinza (`text-xs font-semibold text-slate-500 uppercase tracking-wider`).
* Linhas: Hover state subtil (`hover:bg-slate-50`).
* Colunas de Ação: Alinhadas à direita, contendo ícones (editar, excluir, detalhes) em tons neutros que escurecem no hover.
* Sempre inclua Badges de Status (usando as cores semânticas da seção 1.2) na coluna apropriada.

### 3.3. Formulários e Inputs
* Inputs devem ter bordas nítidas: `border-slate-300 rounded-lg focus:ring-2 focus:ring-[#00E6B8] focus:border-[#00E6B8]`.
* Labels devem estar fora do input (acima), em `text-sm font-medium text-slate-700`.
* **Integrações Simuladas UI:** Inputs como CEP, CNPJ ou Placa FIPE devem ter um pequeno ícone de "Loading" ou "Verificado" à direita para indicar o consumo de APIs (BrasilAPI, Parallelum).

### 3.4. Mapas e Geolocalização
* Sempre que um mapa for renderizado (simulando Leaflet/Mapbox), ele deve possuir cantos arredondados (`rounded-xl`), sombra (`shadow-md`) e um overlay com controles rápidos (ex: "Centralizar na Frota").

### 3.5. Componente de Chat / WhatsApp
* Bolhas de mensagem do sistema/IA devem utilizar a cor de destaque da marca (`bg-[#00E6B8]/10 text-[#001A33] border border-[#00E6B8]/30`).
* Mensagens do motorista devem ser neutras (`bg-white border border-slate-200`).

---

## 4. ⚡ Interações e Comportamento (UX)

* **Feedback Imediato:** Qualquer clique em botões de "Salvar" ou "Calcular Rota" deve acionar um estado de *loading* (spinner no botão e `opacity-75` no resto).
* **Drawers (Painéis Laterais):** Em vez de enviar o usuário para outra página ao clicar nos detalhes de uma viagem ou num registro de caminhão, abra um "Drawer" lateral (`slide-over` a partir da direita). Isso mantém o contexto da tabela original.
* **Formatos Monetários e Decimais:**
    * Valores financeiros devem sempre usar máscara `R$ 0.000,00`.
    * Coordenadas GPS (Lat/Long) devem ser exibidas com alta precisão técnica quando visíveis (ex: `-10.87654321`).

## 5. Diretrizes para a Geração de Código
Ao gerar código `.ejs` ou componentes React/Tailwind baseados neste documento:
1.  NÃO use estilos inline (`style="..."`). Confie 100% no Tailwind.
2.  Use ícones da biblioteca *Lucide* ou *Heroicons* (se aplicável no gerador).
3.  Garanta acessibilidade (`aria-labels` in botões de ícone).
