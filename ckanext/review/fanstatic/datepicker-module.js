//loads jquery-ui's datepicker for the input field
$(function() {
	$.each($(".vdoj-datepicker input:text"), function(){
	    $(this).datepicker({ dateFormat: "dd-mm-yy" });
	    if ($(this).attr('readonly')=='readonly'){
			$(this).datepicker("option", "minDate", -1);
			$(this).datepicker("option", "maxDate", -2);
	    }
	});
});