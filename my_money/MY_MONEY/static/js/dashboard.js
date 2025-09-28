// Arquivo: static/js/dashboard.js

// Variável para armazenar a instância do gráfico de pizza
let graficoPizzaInstance = null;
// Variável para armazenar a instância do gráfico de barras (adicionada por consistência, caso precise manipulá-lo depois)
let graficoMensalInstance = null;


document.addEventListener("DOMContentLoaded", () => {
  // Carregar email do usuário (manter esta lógica se ainda for usada)
  const email = localStorage.getItem("email");
  if (document.getElementById("userEmail")) {
      document.getElementById("userEmail").textContent = email || "usuário não identificado";
  }


  // Função para atualizar o resumo financeiro por período e total acumulado
  function atualizarResumo(periodo = 'mes') {
    fetch(`/resumo_periodo?periodo=${periodo}`)
      .then(response => response.json())
      .then(data => {
        if (data) {
          // Dados do período selecionado
          const entradasPeriodo = parseFloat(data.entradas || 0).toFixed(2).replace('.', ',');
          const saidasPeriodo = parseFloat(data.saidas || 0).toFixed(2).replace('.', ',');
          const saldoPeriodo = parseFloat(data.saldo || 0).toFixed(2).replace('.', ',');

          // Dados do resumo total acumulado
          const totalAcumuladoEntradas = parseFloat(data.total_acumulado_entradas || 0).toFixed(2).replace('.', ',');
          const totalAcumuladoSaidas = parseFloat(data.total_acumulado_saidas || 0).toFixed(2).replace('.', ',');
          const totalAcumuladoSaldo = parseFloat(data.total_acumulado_saldo || 0).toFixed(2).replace('.', ',');


          const liEntradas = document.getElementById("liEntradas");
          const liSaidas = document.getElementById("liSaidas");
          const liSaldo = document.getElementById("liSaldo");
          const resumoEntradasSpan = document.getElementById("resumoEntradas");
          const resumoSaidasSpan = document.getElementById("resumoSaidas");
          const resumoSaldoSpan = document.getElementById("resumoSaldo");
          const tituloPeriodoSpan = document.getElementById("tituloPeriodo");

          // Elementos do resumo total acumulado
          const resumoTotalEntradasSpan = document.getElementById("resumoTotalEntradas");
          const resumoTotalSaidasSpan = document.getElementById("resumoTotalSaidas");
          const resumoTotalSaldoSpan = document.getElementById("resumoTotalSaldo");


          // Atualiza o título do período no card de resumo geral
          let titulo = '';
          if (periodo === 'semana') {
              const hoje = new Date();
              const diaSemana = hoje.getDay();
              const diff = hoje.getDate() - diaSemana;
              const inicioSemana = new Date(hoje.setDate(diff));
              const fimSemana = new Date(hoje.setDate(diff + 6));
              const options = { day: '2-digit', month: '2-digit' };
              titulo = `Semana (${inicioSemana.toLocaleDateString('pt-BR', options)} - ${fimSemana.toLocaleDateString('pt-BR', options)})`;
          } else if (periodo === 'mes') {
              const mesNome = new Date().toLocaleDateString('pt-BR', { month: 'long' });
              const ano = new Date().getFullYear();
              titulo = `${mesNome.charAt(0).toUpperCase() + mesNome.slice(1)} ${ano}`;
          } else if (periodo === 'ano') {
              titulo = `Ano ${new Date().getFullYear()}`;
          }
           if (tituloPeriodoSpan) { // Verifica se o elemento existe antes de atualizar
                tituloPeriodoSpan.textContent = titulo;
           }


          // Atualiza os valores do resumo do período selecionado (verifica se os elementos existem)
           if (liEntradas) liEntradas.style.display = 'block';
           if (liSaidas) liSaidas.style.display = 'block';
           if (liSaldo) liSaldo.style.display = 'block';
           if (resumoEntradasSpan) resumoEntradasSpan.textContent = `R$ ${entradasPeriodo}`;
           if (resumoSaidasSpan) resumoSaidasSpan.textContent = `R$ ${saidasPeriodo}`;
           if (resumoSaldoSpan) resumoSaldoSpan.textContent = `R$ ${saldoPeriodo}`;


          // Atualiza os valores do resumo total acumulado (verifica se os elementos existem)
           if (resumoTotalEntradasSpan) resumoTotalEntradasSpan.textContent = `R$ ${totalAcumuladoEntradas}`;
           if (resumoTotalSaidasSpan) resumoTotalSaidasSpan.textContent = `R$ ${totalAcumuladoSaidas}`;
           if (resumoTotalSaldoSpan) resumoTotalSaldoSpan.textContent = `R$ ${totalAcumuladoSaldo}`;

        }
      })
      .catch(error => console.error("Erro ao buscar resumo:", error));
  }

  // Adiciona listeners aos botões de filtro de período para redirecionar
  document.querySelectorAll('.filtro-periodo').forEach(btn => {
    btn.addEventListener('click', function () {
      // Remove a classe 'active' de todos os botões de filtro e adiciona ao clicado
       document.querySelectorAll('.filtro-periodo').forEach(b => b.classList.remove('active')); // Garante que todos perdem a classe
       this.classList.add('active');

      const periodo = this.dataset.periodo;
      // Redireciona para a página do dashboard com o parâmetro de período
      window.location.href = `/dashboard?periodo=${periodo}`;
       // Alternativamente, para atualizar via AJAX sem recarregar a página:
       // atualizarResumo(periodo);
       // atualizarGraficoMensal(periodo);
       // atualizarGraficoPizza(periodo(periodo);
       // atualizarTabelaLancamentos(); // Chamar se a tabela estivesse no dashboard
    });
  });


  // Função para atualizar o gráfico de pizza (Distribuição Financeira)
  function atualizarGraficoPizza(periodo = 'mes') {
    fetch(`/distribuicao_financeira?periodo=${periodo}`)
      .then(response => response.json())
      .then(data => {
        // *** Adicione logs para inspecionar os dados ***
        console.log(`Dados recebidos para o gráfico de pizza (${periodo}):`, data);

        // Verifica se há dados para o gráfico de pizza. Se não, destrói o gráfico e sai da função.
        if (!data || data.length === 0) {
             console.log(`Nenhum dado para o gráfico de pizza (${periodo}). Destruindo gráfico.`);
             if (graficoPizzaInstance) {
                graficoPizzaInstance.destroy();
                graficoPizzaInstance = null; // Define como null após destruir
             }
             // Limpar a área do canvas se não houver dados
             const ctx = document.getElementById('graficoPizza')?.getContext('2d'); // Usa optional chaining
             if (ctx) {
                 ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
             }
             return; // Sai da função se não houver dados
        }


        const labels = data.map(item => item.categoria);
        const valores = data.map(item => item.valor);

        console.log(`Labels gerados para o gráfico de pizza (${periodo}):`, labels);
        console.log(`Valores gerados para o gráfico de pizza (${periodo}):`, valores);
        console.log(`Número de fatias esperadas (${periodo}):`, labels.length);


        const canvas = document.getElementById('graficoPizza');
        if (!canvas) {
             console.error("Elemento canvas para gráfico de pizza não encontrado!");
             return;
        }
        const ctx = canvas.getContext('2d');


        // Verifica se já existe uma instância do gráfico e a destrói
        if (graficoPizzaInstance) {
          graficoPizzaInstance.destroy();
        }

        // *** Adicione um try...catch em torno da criação do gráfico ***
        try {
          graficoPizzaInstance = new Chart(ctx, {
            type: 'pie',
            data: {
              labels: labels,
              datasets: [{
                data: valores,
                backgroundColor: gerarCoresAleatorias(labels.length)
              }]
            },
            options: {
              responsive: true,
              plugins: {
                legend: { position: 'top' },
                tooltip: {
                  callbacks: {
                    label: function (context) {
                      let label = context.label || '';
                      if (label) label += ': ';
                      if (context.parsed !== null) {
                        label += 'R$ ' + parseFloat(context.parsed).toFixed(2).replace('.', ','); // Formatar valor no tooltip
                      }
                      return label;
                    }
                  }
                }
              }
            }
          });
          console.log(`Gráfico de pizza para ${periodo} criado com sucesso.`);
        } catch (error) {
          console.error(`Erro ao criar o gráfico de pizza para ${periodo}:`, error);
          // Limpar o canvas se houver um erro na criação
          if (ctx) {
              ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
          }
        }
      })
      .catch(error => console.error("Erro na requisição dos dados da pizza:", error)); // Ajuste a mensagem para ser mais clara
   }


  // Função para atualizar o gráfico de barras (Entradas e Saídas Mensais)
  function atualizarGraficoMensal(periodo = 'mes') {
     fetch(`/entradas_saidas_mensal?periodo=${periodo}`)
       .then(response => response.json())
       .then(data => {
         console.log(`Dados recebidos para o gráfico de barras (${periodo}):`, data); // Log para depuração

         // Verifica se há dados. Se não, destrói o gráfico e sai.
         if (!data || data.length === 0) {
            console.log(`Nenhum dado para o gráfico de barras (${periodo}). Destruindo gráfico.`);
            if (graficoMensalInstance) {
               graficoMensalInstance.destroy();
               graficoMensalInstance = null; // Define como null após destruir
            }
             const ctxMensal = document.getElementById('graficoMensal')?.getContext('2d'); // Usa optional chaining
             if (ctxMensal) {
                 ctxMensal.clearRect(0, 0, ctxMensal.canvas.width, ctxMensal.canvas.height);
             }
            return; // Sai da função
         }


         const labels = data.map(item => item.mes);
         const entradas = data.map(item => item.entradas);
         const saidas = data.map(item => item.saidas);

         const canvasMensal = document.getElementById('graficoMensal');
         if (!canvasMensal) {
             console.error("Elemento canvas para gráfico de barras não encontrado!");
             return;
         }
         const ctxMensal = canvasMensal.getContext('2d');


         // Destrói a instância anterior do gráfico de barras, se existir
         if (graficoMensalInstance) {
             graficoMensalInstance.destroy();
         }

         try {
              graficoMensalInstance = new Chart(ctxMensal, {
                 type: 'bar',
                 data: {
                     labels: labels,
                     datasets: [
                         {
                             label: 'Entradas',
                             data: entradas,
                             backgroundColor: '#007bff'
                         },
                         {
                             label: 'Saídas',
                             data: saidas,
                             backgroundColor: '#dc3545'
                         }
                     ]
                 },
                 options: {
                     responsive: true,
                     plugins: {
                         legend: { position: 'top' },
                         tooltip: {
                             callbacks: {
                                 label: function (context) {
                                     let label = context.dataset.label || '';
                                     if (label) label += ': ';
                                     if (context.parsed.y !== null) {
                                         label += 'R$ ' + parseFloat(context.parsed.y).toFixed(2).replace('.', ','); // Formatar valor no tooltip
                                     }
                                     return label;
                                 }
                             }
                         }
                     },
                     scales: {
                         y: {
                             beginAtZero: true,
                             ticks: {
                                 // Personalize os ticks se necessário, remover stepSize 2 se os valores forem altos
                                 // stepSize: 2
                             }
                         }
                     }
                 }
              });
              console.log(`Gráfico de barras para ${periodo} criado com sucesso.`);
         } catch(error) {
             console.error(`Erro ao criar o gráfico de barras para ${periodo}:`, error);
             const ctxMensal = document.getElementById('graficoMensal')?.getContext('2d');
             if (ctxMensal) {
                 ctxMensal.clearRect(0, 0, ctxMensal.canvas.width, ctxMensal.canvas.height);
             }
         }
       })
       .catch(error => console.error("Erro na requisição dos dados mensais:", error));
   }


    // ** REMOVIDA LÓGICA DA TABELA: PAGINAÇÃO, ORDENAÇÃO, FILTROS E ATUALIZAÇÃO **
    // Essa lógica agora deve estar no arquivo static/js/extrato.js e ser executada
    // apenas na página de extrato.


  // Obtenha o período inicial da URL ou use 'mes' como padrão
  const urlParams = new URLSearchParams(window.location.search);
  const periodoInicial = urlParams.get('periodo') || 'mes';

   // Atualiza o estado visual dos botões de período na carga inicial
   document.querySelectorAll('.filtro-periodo').forEach(btn => {
        if (btn.dataset.periodo === periodoInicial) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
   });


  // Chamadas iniciais para carregar dados e gráficos na carga da página
  atualizarResumo(periodoInicial);
  atualizarGraficoMensal(periodoInicial);
  atualizarGraficoPizza(periodoInicial);
  // Chamada para atualizar a tabela removida daqui (pertence ao extrato)
  // atualizarTabelaLancamentos(); // Esta função foi removida


  // Lógica para exibir o toast de sucesso ao salvar lançamento (se houver o parâmetro 'sucesso=1' na URL)
  const params = new URLSearchParams(window.location.search);
  if (params.get("sucesso") === "1") {
    const toastEl = document.getElementById('toastSucesso');
    if (toastEl) {
      // Mostra o toast
      new bootstrap.Toast(toastEl).show();
      // Remove o parâmetro 'sucesso' da URL para que o toast não apareça novamente ao recarregar
      params.delete("sucesso");
      const novaURL = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
      window.history.replaceState({}, document.title, novaURL);

      // Opcional: Recarregar dados do dashboard após salvar com sucesso (já acontece no redirecionamento, mas pode ser útil para atualizações via AJAX sem recarregar a página)
      // atualizarResumo(periodoInicial); // periodoInicial pode não ser o ideal após salvar
      // atualizarGraficoMensal(periodoInicial);
      // atualizarGraficoPizza(periodoInicial);
      // atualizarTabelaLancamentos(); // Chamar se a tabela estivesse no dashboard
    }
  }
});


// Função auxiliar para gerar cores aleatórias para o gráfico de pizza
function gerarCoresAleatorias(qtd) {
  const cores = [];
  for (let i = 0; i < qtd; i++) {
      // Gera cores no espaço HSL para garantir boa distinção
      const hue = Math.floor(Math.random() * 360); // Matiz (0-359)
      const saturation = 70 + Math.floor(Math.random() * 30); // Saturação (70-100)
      const lightness = 50 + Math.floor(Math.random() * 20); // Luminosidade (50-70)
      cores.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
  }
  return cores;
   // Versão anterior mais simples, mantida como comentário
   /*
   return Array.from({ length: qtd }, () =>
     `hsl(${Math.floor(Math.random() * 360)}, 70%, 60%)`
   );
   */
}