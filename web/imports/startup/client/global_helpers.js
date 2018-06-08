Template.registerHelper('json2string', (j) => {
  return JSON.stringify(j, null, '  ');
});

Template.registerHelper('niceTime', (t) => {
  return moment(t).format('MMMM Do hh:mm:ss');
});
