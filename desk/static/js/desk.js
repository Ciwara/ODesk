
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
    }]
});


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
/*$('.datepicker').datepicker("setDate", new Date());*/
