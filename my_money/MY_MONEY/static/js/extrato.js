document.addEventListener("DOMContentLoaded", () => {
    const tabelaLancamentos = document.getElementById('tabelaLancamentos');
    const linhasTabela = tabelaLancamentos.getElementsByTagName('tr');
    const registrosPorPagina = 10;
    let paginaAtual = 1;
   
  
    function exibirPagina(numPagina) {
    paginaAtual = numPagina;
    const inicio = (numPagina - 1) * registrosPorPagina;
    const fim = inicio + registrosPorPagina;
    for (let i = 1; i < linhasTabela.length; i++) {
    linhasTabela[i].style.display = 'none';
    if (i >= inicio && i < fim) {
    linhasTabela[i].style.display = '';
    }
    }
    }
   
  
    function criarPaginacao() {
    const numPaginas = Math.ceil((linhasTabela.length - 1) / registrosPorPagina);
    const paginacao = document.getElementById('paginacao');
    paginacao.innerHTML = '';
   
  
    for (let i = 1; i <= numPaginas; i++) {
    const link = document.createElement('a');
    link.href = '#';
    link.textContent = i;
    if (i === paginaAtual) {
    link.classList.add('active');
    }
    link.addEventListener('click', (e) => {
    e.preventDefault();
    exibirPagina(i);
    const links = paginacao.querySelectorAll('a');
    links.forEach(a => a.classList.remove('active'));
    link.classList.add('active');
    });
    paginacao.appendChild(link);
    }
    }
   
  
    exibirPagina(1);
    criarPaginacao();
   
  
    const cabecalhoData = document.querySelector('#tabelaLancamentos th:nth-child(6)');
    let ordemData = 'asc';
   
  
    cabecalhoData.addEventListener('click', () => {
    ordenarTabelaPorData(ordemData);
    ordemData = ordemData === 'asc' ? 'desc' : 'asc';
    });
   
  
    function ordenarTabelaPorData(ordem) {
    const tbody = tabelaLancamentos.querySelector('tbody');
    const linhas = Array.from(tbody.querySelectorAll('tr'));
   
  
    linhas.sort((a, b) => {
    const dataA = new Date(a.cells[5].textContent);
    const dataB = new Date(b.cells[5].textContent);
    return ordem === 'asc' ? dataA - dataB : dataB - dataA;
    });
   
  
    tbody.innerHTML = '';
    linhas.forEach(linha => tbody.appendChild(linha));
    exibirPagina(paginaAtual);
    criarPaginacao();
    }
   
  
    const filtroTipo = document.getElementById('filtroTipo');
    const filtroCategoria = document.getElementById('filtroCategoria');
    const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
   
  
    function aplicarFiltros() {
    const tipoSelecionado = filtroTipo.value;
    const categoriaSelecionada = filtroCategoria.value;
   
  
    atualizarTabelaLancamentos(tipoSelecionado, categoriaSelecionada);
    }
   
  
    btnAplicarFiltros.addEventListener('click', aplicarFiltros);
   
      // Excluir Lançamento
    tabelaLancamentos.addEventListener('click', (event) => {
        if (event.target.classList.contains('excluir-btn')) {
        const lancamentoId = event.target.dataset.id;
        if (confirm('Tem certeza que deseja excluir este lançamento?')) {
            fetch('/excluir_lancamento', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `lancamento_id=${lancamentoId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                alert(data.message);
                atualizarTabelaLancamentos();
                } else {
                alert('Erro ao excluir lançamento: ' + data.message);
                }
            })
            .catch(error => console.error('Erro ao excluir:', error));
        }
        }
    });

    function atualizarTabelaLancamentos(tipo = 'todos', categoria = 'todas') {
    let url = "/entradas_saidas";
    if (tipo !== 'todos' || categoria !== 'todas') {
    url += "?";
    if (tipo !== 'todos') {
    url += `tipo_filtro=${tipo}&`;
    }
    if (categoria !== 'todas') {
    url += `categoria_filtro=${categoria}&`;
    }
    url = url.slice(0, -1);
    }
   
  
    fetch(url)
    .then(res => res.json())
    .then(lancamentos => {
    const tbody = document.querySelector("#tabelaLancamentos tbody");
    tbody.innerHTML = '';
    lancamentos.forEach(item => {
    const row = document.createElement("tr");
    row.innerHTML = `
    <td>${item.id}</td>
    <td>${item.categoria}</td>
    <td>${item.produto_servico}</td>
    <td>${item.tipo_conta}</td>
    <td>R$ ${parseFloat(item.valor).toFixed(2)}</td>
    <td>${item.data}</td>
    <td>${item.tipo === "entrada" ? "Entrada" : "Saída"}</td>
    <td><button class="btn btn-danger btn-sm excluir-btn" data-id="${item.id}">Excluir</button></td>
    `;
    tbody.appendChild(row);
    });
    exibirPagina(paginaAtual);
    criarPaginacao();
    });
    }
   
  
    atualizarTabelaLancamentos();
   });