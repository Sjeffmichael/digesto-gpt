function generation_metrics_chart(faithfulnessMetrics, answerRelevancy, contextUtilization) {
    const options = {
        // set the labels option to true to show the labels on the X and Y axis
        xaxis: {
          show: true,
          type: 'datetime',
          labels: {
            show: true,
            style: {
              fontFamily: "Inter, sans-serif",
              cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
            }
          },
          axisBorder: {
            show: false,
          },
          axisTicks: {
            show: false,
          },
        },
        yaxis: {
          show: true,
          labels: {
            show: true,
            style: {
              fontFamily: "Inter, sans-serif",
              cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
            },
          }
        },
        series: [
          {
            name: gettext("Faithfulness"),
            data: faithfulnessMetrics,
            color: "#1A56DB",
          },
          {
            name: gettext("Answer Relevancy"),
            data: answerRelevancy,
            color: "#7E3BF2",
          },
          {
            name: gettext("Context Utilization"),
            data: contextUtilization,
            color: "#16BDCA",
          },
        ],
        chart: {
          sparkline: {
            enabled: false
          },
          height: "100%",
          width: "100%",
          type: "area",
          fontFamily: "Inter, sans-serif",
          dropShadow: {
            enabled: false,
          },
          toolbar: {
            show: false,
          },
        },
        tooltip: {
          enabled: true,
          x: {
            show: false,
          },
        },
        fill: {
          type: "gradient",
          gradient: {
            opacityFrom: 0.55,
            opacityTo: 0,
            shade: "#1C64F2",
            gradientToColors: ["#1C64F2"],
          },
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          width: 6,
        },
        legend: {
          show: true
        },
        grid: {
          show: false,
        },
        }
        if (document.getElementById("tooltip-chart") && typeof ApexCharts !== 'undefined') {
            const chart = new ApexCharts(document.getElementById("tooltip-chart"), options);
            chart.render();
        }
}
