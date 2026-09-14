document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('market-search');
  const searchResults = document.getElementById('market-search-results');
  const chartWrappers = document.querySelectorAll('.market-chart');

  if (!searchInput && !chartWrappers.length) {
    return;
  }

  const rangeButtons = ['1D', '5D', '1M', '3M', '6M', '1Y', '5Y', 'MAX'];

  function setChartLoading(element, message = 'Chargement...') {
    const status = element.querySelector('.chart-status');
    if (status) {
      status.textContent = message;
      status.classList.add('is-warning');
    }
  }

  function setChartError(element, message = 'Données indisponibles') {
    const status = element.querySelector('.chart-status');
    if (status) {
      status.textContent = message;
      status.classList.remove('is-warning');
      status.classList.add('is-error');
    }
  }

  function renderChart(element, candles) {
    const canvas = element.querySelector('.chart-canvas');
    const status = element.querySelector('.chart-status');

    if (!canvas || !candles || !candles.length) {
      if (status) {
        status.textContent = 'Aucune donnée disponible';
      }
      return;
    }

    if (window.lightweightCharts && typeof window.lightweightCharts.createChart === 'function') {
      const chart = window.lightweightCharts.createChart(canvas, {
        layout: {
          background: { color: '#0f1726' },
          textColor: '#edf4ff'
        },
        grid: {
          vertLines: { color: 'rgba(148, 163, 184, 0.10)' },
          horzLines: { color: 'rgba(148, 163, 184, 0.10)' }
        },
        crosshair: {
          mode: window.lightweightCharts.CrosshairMode.Normal,
          vertLine: { color: '#7dd3fc', width: 1 },
          horzLine: { color: '#7dd3fc', width: 1 }
        },
        rightPriceScale: { borderColor: 'rgba(148, 163, 184, 0.25)' },
        timeScale: { borderColor: 'rgba(148, 163, 184, 0.25)' },
        width: canvas.clientWidth,
        height: 230,
      });

      const candleSeries = chart.addCandlestickSeries({
        upColor: '#16c784',
        downColor: '#ea3943',
        borderVisible: false,
        wickUpColor: '#16c784',
        wickDownColor: '#ea3943'
      });

      const transformed = candles
        .filter((item) => item && typeof item.time !== 'undefined' && item.close !== null)
        .map((item) => ({
          time: Math.floor(item.time / 1000),
          open: Number(item.open),
          high: Number(item.high),
          low: Number(item.low),
          close: Number(item.close),
          volume: Number(item.volume || 0)
        }));

      if (transformed.length) {
        candleSeries.setData(transformed);
        chart.timeScale().fitContent();
      }

      if (status) {
        status.textContent = 'Marché connecté';
        status.classList.remove('is-warning', 'is-error');
      }

      const resizeObserver = new ResizeObserver(() => {
        chart.applyOptions({ width: canvas.clientWidth });
      });
      resizeObserver.observe(canvas);

      element._chart = chart;
      element._resizeObserver = resizeObserver;
    }
  }

  async function fetchJson(url) {
    const response = await fetch(url, { headers: { 'Accept': 'application/json' } });
    const content = await response.json();

    if (!response.ok) {
      throw new Error(content.error || 'Request failed');
    }

    return content;
  }

  async function loadChart(element) {
    const symbol = element.dataset.symbol;
    const range = element.dataset.range || '1M';
    const name = element.dataset.name || symbol;
    const symbolLabel = element.querySelector('.symbol-label');

    if (symbolLabel) {
      symbolLabel.textContent = name;
    }

    setChartLoading(element, 'Chargement...');

    try {
      const data = await fetchJson(`/api/markets/history/${encodeURIComponent(symbol)}?range=${encodeURIComponent(range)}`);
      renderChart(element, data.candles || []);
    } catch (error) {
      setChartError(element, error.message || 'Données indisponibles');
    }
  }

  function attachRangeButtons() {
    chartWrappers.forEach((element) => {
      const buttons = element.querySelectorAll('.chart-range button');
      buttons.forEach((button) => {
        button.addEventListener('click', function () {
          const nextRange = this.dataset.range;
          element.dataset.range = nextRange;
          loadChart(element);
        });
      });
    });
  }

  if (chartWrappers.length) {
    chartWrappers.forEach((chart) => {
      if (!chart.dataset.symbol) {
        return;
      }
      loadChart(chart);
    });
    attachRangeButtons();
  }

  if (searchInput && searchResults) {
    const handleSearch = async function () {
      const query = searchInput.value.trim();

      if (!query || query.length < 2) {
        searchResults.innerHTML = '';
        return;
      }

      try {
        const data = await fetchJson(`/api/markets/search?q=${encodeURIComponent(query)}`);
        const items = data.items || [];

        if (!items.length) {
          searchResults.innerHTML = '<div class="search-empty">Aucun symbole trouvé.</div>';
          return;
        }

        searchResults.innerHTML = items.map((item) => `
          <button class="search-result" type="button" data-symbol="${item.symbol}" data-name="${item.name}">
            <strong>${item.symbol}</strong>
            <span>${item.name}</span>
          </button>
        `).join('');

        searchResults.querySelectorAll('.search-result').forEach((button) => {
          button.addEventListener('click', function () {
            const symbol = this.dataset.symbol;
            const name = this.dataset.name || symbol;
            const newCard = document.createElement('div');
            newCard.className = 'market-chart';
            newCard.dataset.symbol = symbol;
            newCard.dataset.name = name;
            newCard.dataset.range = '1M';
            newCard.innerHTML = `
              <div class="chart-head">
                <div>
                  <div class="chart-symbol">${symbol}</div>
                  <div class="symbol-label">${name}</div>
                </div>
                <span class="chart-status">Chargement...</span>
              </div>
              <div class="chart-range">
                ${rangeButtons.map((range) => `<button type="button" data-range="${range}" class="${range === '1M' ? 'is-active' : ''}">${range}</button>`).join('')}
              </div>
              <div class="chart-canvas"></div>
            `;

            const target = document.getElementById('chart-list');
            if (target) {
              target.appendChild(newCard);
              loadChart(newCard);
              attachRangeButtons();
            }

            searchResults.innerHTML = '';
            searchInput.value = '';
          });
        });
      } catch (error) {
        searchResults.innerHTML = '<div class="search-empty">Recherche indisponible.</div>';
      }
    };

    searchInput.addEventListener('input', handleSearch);
  }
});
