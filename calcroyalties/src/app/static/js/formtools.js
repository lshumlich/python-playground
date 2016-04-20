var emailRegexp = /^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$/i;

function updateErrors(t){
errors = $(".errors");
errors.text(t)
};

function checkEntered( o ) {
if ( o.val() == "" ) {
  o.addClass( "ui-state-error" );
  o.focus();
  o.on('input', function() { o.removeClass( "ui-state-error" ) });
  updateErrors( o.attr('ID') + " needs to be entered" );
  return false;
} else {
  o.removeClass( "ui-state-error" );
  return true;
}
};

function checkLength( o, min, max ) {
if ( o.val().length > max || o.val().length < min ) {
  o.addClass( "ui-state-error" );
  o.focus();
  o.on('input', function() { o.removeClass( "ui-state-error" ) });
  updateErrors( "Length of " + o.attr('ID').toLowerCase() + " must be between " + min + " and " + max + "." );
  return false;
} else {
  o.removeClass( "ui-state-error" );
  return true;
}
};

function checkRegexp( o, regexp) {
if ( !( regexp.test( o.val() ) ) ) {
  o.addClass( "ui-state-error" );
  o.focus();
  o.on('input', function() { o.removeClass( "ui-state-error" ) });
  updateErrors( o.attr('ID') + " has incorrect format" );
  return false;
} else {
  o.removeClass( "ui-state-error" );
  return true;
}
};