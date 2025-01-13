function correctness_metric_chart(correcness_data) {

    const getChartOptions = () => {
        return {
          series: correcness_data,
          colors: ["#16BDCA", "#FDBA8C",],
          chart: {
            height: 320,
            width: "100%",
            type: "donut",
          },
          stroke: {
            colors: ["transparent"],
            lineCap: "",
          },
          plotOptions: {
            pie: {
              donut: {
                labels: {
                  show: true,
                  name: {
                    show: true,
                    fontFamily: "Inter, sans-serif",
                    offsetY: 20,
                  },
                  total: {
                    showAlways: true,
                    show: true,
                    label: gettext("Answers Generated"),
                    fontFamily: "Inter, sans-serif",
                    // formatter: function (w) {
                    //   const sum = w.globals.seriesTotals.reduce((a, b) => {
                    //     return a + b
                    //   }, 0)
                    //   return '$' + sum + 'k'
                    // },
                  },
                  value: {
                    show: true,
                    fontFamily: "Inter, sans-serif",
                    offsetY: -20,
                    // formatter: function (value) {
                    //   return value + "k"
                    // },
                  },
                },
                size: "80%",
              },
            },
          },
          grid: {
            padding: {
              top: -2,
            },
          },
          labels: [gettext("Correct"), gettext("Incorrect")],
          dataLabels: {
            enabled: false,
          },
          legend: {
            position: "bottom",
            fontFamily: "Inter, sans-serif",
          },
          yaxis: {
            labels: {
              // formatter: function (value) {
              //   return value + "k"
              // },
            },
          },
          xaxis: {
            labels: {
              // formatter: function (value) {
              //   return value  + "k"
              // },
            },
            axisTicks: {
              show: false,
            },
            axisBorder: {
              show: false,
            },
          },
        }
      }

      if (document.getElementById("correctness_donut-chart") && typeof ApexCharts !== 'undefined') {
        const chart = new ApexCharts(document.getElementById("correctness_donut-chart"), getChartOptions());
        chart.render();
      }

    }
