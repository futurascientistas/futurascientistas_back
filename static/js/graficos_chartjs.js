class ChartManager {
  static charts = {};

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
