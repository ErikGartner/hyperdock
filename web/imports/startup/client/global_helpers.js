Template.registerHelper('json2string', (j) => {
  return JSON.stringify(j, null, '  ');
});

Template.registerHelper('niceTime', (t) => {
  if (t != -1) {
    return moment(t).format('MMMM Do HH:mm:ss');
  } else {
    return '';
  }
});
