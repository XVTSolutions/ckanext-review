//loads jquery-ui's datepicker for the input field
$(function() {
	$.each($(".vdoj-datepicker input:text"), function(){
	    $(this).datepicker({ dateFormat: "dd-mm-yy" });
	    if ($(this).attr('readonly')=='readonly'){
			if (!$.trim($(this).val()).length){
				$(this).datepicker("setDate", new Date());//fail safe
			}
			$(this).datepicker("option", "beforeShow", function(element, instance) { return false; });
	    }
	});
});