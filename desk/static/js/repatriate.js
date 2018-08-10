
function h_chartLine(data, id) {
    var data = data['series'];
    console.log(data);
/*
    Highcharts.chart(id, {

        title: {
            text: 'Solar Employment Growth by Sector, 2010-2016'
        },

        subtitle: {
            text: 'Source: thesolarfoundation.com'
        },

        yAxis: {
            title: {
                text: 'Number of Employees'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },
        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                },
                pointStart: 2010
            }
        },
        series: data["series"]
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }
    });*/
}

function hchartLine(data, id) {

    Highcharts.chart(data['id'], {
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

function hchartbar(data, id) {

    Highcharts.chart(id, {
    chart: {
        type: 'column'
    },
    title: {
        text: data['label']
    },
    subtitle: {
        text: data['subtitle']
    },
    xAxis: {
        categories: data['categories'],
        crosshair: true
    },
    yAxis: {
        min: 0,
        title: {
            text: data['title']
        }
    },
    tooltip: {
        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
        footerFormat: '</table>',
        shared: true,
        useHTML: true
    },
    plotOptions: {
        column: {
            pointPadding: 0.2,
            borderWidth: 0
        }
    },

        series: data['series']
});
}
