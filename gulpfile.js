var gulp = require('gulp');
var browserSync = require('browser-sync');
var exec = require('child_process').exec;
var reload = browserSync.reload;
var shell = require('gulp-shell');


var dir = "~/dev/rep";
var host = "127:0.0.1";
var port = "7000";
var watch_list = [
  "rep/templates/**",
  "rep/static/**"
];

// gulp.task('watch', function () {
//     gulp.watch(watch_list).on('change', reload);
// });

gulp.task('runserver', function() {
    // var proc = exec('python runserver.py');
    shell.task('python runserver.py');
});

gulp.task('browser-sync', ['runserver'], function () {
  browserSync({
    notify: false,
    files: '~/dev/rep/templates/**, ~/dev/rep/static/**'
  });
});

gulp.task('default', ['browser-sync']);
