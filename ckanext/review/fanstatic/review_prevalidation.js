this.ckan.module('review_prevalidation', function (jQuery, _) {


  return {

    /* Sets up the event listeners for the object. Called internally by
     * module.createInstance().
     *
     * Returns nothing.
     */
    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      $(this.el).closest('form').on('submit', this._onSubmit);
    },
    _onSubmit: function(event){
      //validation 
      var ret = this.isValid(this.el);   
      return ret;
    },
    isValid: function(el){
      var valiationErrors = [];
      var asterisk = '* '

      //clear validation error
      $(el).closest('form').find('.error-block').remove();

      //name and title fields
      $(el).closest('form').find('#field-dataset_review_interval').each(function(){
        var label = $(this).closest('.control-group').find('label.control-label').text();
        if (label.length > asterisk.length && label.substring(0, asterisk.length) == asterisk){
          label = label.substring(asterisk.length);
        }

        var fieldValue = $.trim($(this).val());
        $(this).val(fieldValue);

        //is integer?
        if(!isInteger(fieldValue) || parseInt(fieldValue) < 1 || parseInt(fieldValue) > 999) {
          var error = 'Must be in range from 1 to 999';
          valiationErrors.push({'label': label, 'error': error});
          $(this).parent().append('<span class="error-block">' + error + '</span>');
        }

      });

      //summary
      this.summarizeErrors(el, valiationErrors);

      return !valiationErrors.length;
    },
    summarizeErrors: function(el, errors){
      if (errors.length)
      {
        //clear error
        $(el).closest('form').find('div.error-explanation').remove()       

        var explanation = ['<div class="error-explanation alert alert-error ">',
        '<p>The form contains invalid entries:</p>',
        '<ul>'].join('\n');
        for (var i=0; i<errors.length; i++)
        {
          explanation = explanation + '<li data-field-label="' + errors[i]['label'] + '">' + errors[i]['label'] + ': ' + errors[i]['error'] + '</li>';
        }
        explanation = explanation + '</ul></div>';

        //add error summary
        $(el).closest('form').children().first().before(explanation);
        if (errors.length){
          $('html, body').animate({scrollTop: 0}, 'slow');
        }
      }
    }
  };
});

