(function(window, document) {

  // enable string formatting: '{0}{1}'.format(var1, var2)
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/\{(\d+)\}/g, function(m, n) {
      return args[n];
    });
  };

})(window, document);
