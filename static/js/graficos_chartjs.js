class ChartManager {
  static charts = {};
  static pluginsRegistered = false;

  static registerPlugins() {
    if (!ChartManager.pluginsRegistered) {
      // Registrar o plugin de funil globalmente
      Chart.register(ChartFunnel);
      ChartManager.pluginsRegistered = true;
    }
  }

  static destroyIfExists(idCanvas) {
    if (ChartManager.charts[idCanvas]) {
      ChartManager.charts[idCanvas].destroy();
      delete ChartManager.charts[idCanvas];
    }
  }

  static register(idCanvas, chartInstance) {
    ChartManager.charts[idCanvas] = chartInstance;
  }

  static getChart(idCanvas) {
    return ChartManager.charts[idCanvas] || null;
  }
}

// Certifique-se de registrar os plugins quando o arquivo for carregado
ChartManager.registerPlugins();


class BaseChart {
  static defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: "#858796",
          font: {
            size: 12
          }
        }
      }
    }
  };

  constructor({ idCanvas, type, labels = [], datasets = [], options = {}, plugins = [] }) {
    this.idCanvas = idCanvas;
    this.type = type;
    this.labels = labels;
    this.datasets = datasets;
    this.options = { ...BaseChart.defaultOptions, ...options };
    this.plugins = plugins;
    this.chartInstance = null;
    
    // Registrar plugins específicos deste chart
    this.registerPlugins();
  }

  registerPlugins() {
    this.plugins.forEach(plugin => {
      if (!Chart.registry.getPlugin(plugin.id)) {
        Chart.register(plugin);
      }
    });
  }

  buildConfig() {
    return {
      type: this.type,
      data: {
        labels: this.labels,
        datasets: this.datasets
      },
      options: this.options,
      plugins: this.plugins
    };
  }

  render() {
    const ctx = document.getElementById(this.idCanvas)?.getContext("2d");
    if (!ctx) {
      console.warn(`Canvas ${this.idCanvas} não encontrado.`);
      return null;
    }

    ChartManager.destroyIfExists(this.idCanvas);
    this.chartInstance = new Chart(ctx, this.buildConfig());
    ChartManager.register(this.idCanvas, this.chartInstance);
    return this.chartInstance;
  }

  updateData({ labels, datasets }) {
    if (!this.chartInstance) return;

    if (labels) this.chartInstance.data.labels = labels;
    if (datasets) this.chartInstance.data.datasets = datasets;

    this.chartInstance.update();
  }
}


class BarChart extends BaseChart {
  constructor({ idCanvas, labels, valores, labelDataSet = "", datasets = [], backgroundColor = [], borderWidth = 1, options = {}, plugins = [] }) {
    const defaultOptions = {
      scales: {
        y: { 
          beginAtZero: true 
        }
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,  
            pointStyle: 'circle',
            font: {
              size: 12
            }
          }
        }
      }
    };

    // const datasets = [
    //   {
    //     label: labelDataSet,
    //     data: valores,
    //     backgroundColor,
    //     borderWidth
    //   }
    // ];

    super({
      idCanvas,
      type: "bar",
      labels,
      datasets,
      options: { ...defaultOptions, ...options },
      plugins
    });
  }
}


class DoughnutChart extends BaseChart {
  constructor({ idCanvas, labels, valores, backgroundColor = [], hoverOffset = 10, options = {}, plugins = [] }) {
    const datasets = [
      {
        data: valores,
        backgroundColor,
        hoverOffset
      }
    ];

    const defaultOptions = {
      cutout: "70%",
      plugins: {
        legend: {
          position: "bottom"
        }
      }
    };

    super({
      idCanvas,
      type: "doughnut",
      labels,
      datasets,
      options: { ...defaultOptions, ...options },
      plugins
    });
  }
}


class LineChart extends BaseChart {
  constructor({ idCanvas, labels, valores, labelDataSet = "", borderColor = "#36A2EB", backgroundColor = "rgba(54,162,235,0.2)", options = {}, plugins = [] }) {
    const datasets = [
      {
        label: labelDataSet,
        data: valores,
        borderColor,
        backgroundColor,
        fill: true,
        tension: 0.3
      }
    ];

    const defaultOptions = {
      elements: {
        point: {
          radius: 4,
          backgroundColor: borderColor
        }
      }
    };

    super({
      idCanvas,
      type: "line",
      labels,
      datasets,
      options: { ...defaultOptions, ...options },
      plugins
    });
  }
}


// Adicione esta classe ao seu arquivo ChartManager

class FunnelChart extends BaseChart {
  constructor({ 
    idCanvas, 
    labels, 
    valores, 
    backgroundColor = [], 
    borderColor = "#fff", 
    borderWidth = 2,
    hoverBackgroundColor = [],
    options = {}, 
    plugins = [] 
  }) {
    // Registrar o plugin de funil
    if (!Chart.registry.getPlugin('funnel')) {
      Chart.register(ChartFunnel);
    }

    const datasets = [
      {
        data: valores,
        backgroundColor,
        borderColor,
        borderWidth,
        hoverBackgroundColor: hoverBackgroundColor.length ? hoverBackgroundColor : backgroundColor.map(color => {
          // Aumenta a opacidade para o hover
          if (color.includes('rgba')) {
            return color.replace(/[\d.]+\)$/g, '1)');
          }
          return color;
        })
      }
    ];

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.raw}`;
            }
          }
        }
      },
      // Configurações específicas do funil
      funnel: {
        minSize: '0%',
        dynamicSlope: true,
        dynamicHeight: true,
        fill: true
      }
    };

    super({
      idCanvas,
      type: "funnel", // Tipo específico para o plugin de funil
      labels,
      datasets,
      options: { ...defaultOptions, ...options },
      plugins: [ChartFunnel, ...plugins] // Inclui o plugin de funil
    });
  }
}