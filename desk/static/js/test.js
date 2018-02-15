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
