$('.datepicker-p').datepicker({
    weekStart: 1,
    daysOfWeekHighlighted: "6,0",
    autoclose: true,
    todayHighlight: true,
    format: "dd-mm-yyyy",
    language: "fr"
});
$('.datepicker').datepicker({
    weekStart: 1,
    daysOfWeekHighlighted: "6,0",
    autoclose: true,
    todayHighlight: true,
    format: "dd/mm/yyyy",
    language: "fr"
});

/*
$('.datepicker').datepicker({
    weekStart: 1,
    daysOfWeekHighlighted: "6,0",
    autoclose: true,
    todayHighlight: true,
    format: "dd/mm/yyyy",
    language: "fr"
});*/

/*
function startRefresh_el(id) {

    var container = document.getElementById(id);
    var content = container.innerHTML;
    container.innerHTML= content;
    console.log("Refreshed " + container);
}
function startRefresh(url, id) {
    $(id).load(url).fadeIn("slow");
}*/