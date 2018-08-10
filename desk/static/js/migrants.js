// Chart.js scripts
// -- Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

function chartlineData(menage_per_date_entrtien, id) {
    //var datasets = Object.values(datasets);
    var ctx = document.getElementById(id);
    var data = menage_per_date_entrtien["data"]
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: menage_per_date_entrtien["labels"],
            datasets: [{
                label: menage_per_date_entrtien["label"],
                lineTension: 0.3,
                backgroundColor: "rgba(2,117,216,0.2)",
                borderColor: "rgba(2,117,216,1)",
                pointRadius: 5,
                pointBackgroundColor: "rgba(2,117,216,1)",
                pointBorderColor: "rgba(255,255,255,0.8)",
                pointHoverRadius: 5,
                pointHoverBackgroundColor: "rgba(2,117,216,1)",
                pointHitRadius: 20,
                pointBorderWidth: 2,
                data: data,
                borderWidth: 1,
            }],
        },
        options: {
            title: {
              display: true,
              text: menage_per_date_entrtien["title"],
            },
        legend: {
          display: true
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });
}
function chartbarData(menage_per_prov, id) {
    // body...
    var ctx = document.getElementById(id);
    var data = menage_per_prov["data"]
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: menage_per_prov["labels"],
            datasets: [{
                  label: menage_per_prov["label"],
                  backgroundColor: getRandomColorData(data.length),
                  borderColor: getRandomColorData(data.length),
                  data: data,
                }],
            options : {
                title: {
                  display: true,
                  text: menage_per_prov["title"],
                },
            }
        },
    });
}

function chartpieData(menage_per_prov) {
    var ctx = document.getElementById("pieChart");
    var data = menage_per_prov["data"];
    var myPieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: menage_per_prov["labels"],
        datasets: [{
                label: menage_per_prov["label"],
                data: data,
                backgroundColor: getRandomColorData(data.length),
        }],
        options : {
                title: {
                  display: true,
                  text: menage_per_prov["title"],
                },
            }
      },
    });
}

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
function getRandomColorData(count) {
        var data =[];
        for (var i = 0; i < count; i++) {
            data.push(getRandomColor());
        }
        return data;
}

function chartUpadteAfterRender(data, id) {

    var data1 = data['series'];
    var chart = Highcharts.chart(id, {
    title: {
        text: data[text]
    },

    subtitle: {
        text: 'Plain'
    },

    xAxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    },

    series: [{
        type: 'column',
        colorByPoint: true,
        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        showInLegend: false
    }]});


    $('#plain').click(function () {
        chart.update({
            chart: {
                inverted: false,
                polar: true
            },
            subtitle: {
                text: 'Plain'
            }
        });
    });

    $('#inverted').click(function () {
        chart.update({
            chart: {
                inverted: true,
                polar: false
            },
            subtitle: {
                text: 'Inverted'
            }
        });
    });

    $('#polar').click(function () {
        chart.update({
            chart: {
                inverted: false,
                polar: false
            },
            subtitle: {
                text: 'Polar'
            }
        });
    });
    }

function chartLine(data, id) {

    var data1 = data['series'];
    Highcharts.chart(id, {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Stacked column chart'
        },
        xAxis: {
            categories: ['Apples', 'Oranges', 'Pears', 'Grapes', 'Bananas']
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Total fruit consumption'
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        legend: {
            align: 'right',
            x: -30,
            verticalAlign: 'top',
            y: 25,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                }
            }
        },
        series: [{
            name: 'John',
            data: [5, 3, 4, 7, 2]
        }, {
            name: 'Jane',
            data: [2, 2, 3, 2, 1]
        }, {
            name: 'Joe',
            data: [3, 4, 4, 2, 5]
        }]
    });
}
function chartLine(data, id) {

    var data1 = data['series'];

    console.log(data1)
    Highcharts.chart(id, {
        chart: {type: data['type']},
        title: data["title"],
        xAxis: {
            categories: data["categories"]
        },
        yAxis: {
            allowDecimals: false,
            min: 0,
            title: {
                text: data['text']
            }
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.x + '</b><br/>' +
                    this.series.name + ': ' + this.y + '<br/>' +
                    'Total: ' + this.point.stackTotal;
            }
        },
    plotOptions: {
        line: {
            dataLabels: {
                enabled: true
            },
            enableMouseTracking: false
        }
    },
        series: data['series']
    });
}

$('.datepicker-p').datepicker({
    weekStart: 1,
    daysOfWeekHighlighted: "6,0",
    autoclose: true,
    todayHighlight: true,
    format: "dd-mm-yyyy",
    language: "fr"
});
$('.datepicker-p').datepicker("setDate", new Date());

$('.datepicker').datepicker({
    weekStart: 1,
    daysOfWeekHighlighted: "6,0",
    autoclose: true,
    todayHighlight: true,
    format: "dd/mm/yyyy",
    language: "fr"
});
/*$('.datepicker').datepicker("setDate", new Date());
*/