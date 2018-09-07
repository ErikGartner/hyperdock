import { Meteor } from 'meteor/meteor';

import Chart from 'chart.js';
import palette from 'google-palette';
import lodash from 'lodash';

import '../../stylesheets/resultgraph.less';
import './resultgraph.html';

Template.resultgraph.onRendered(function () {

  let graphId = 'graph-' + this.data._id + '-' + this.data.graphIdx;
  let ctx = document.getElementById(graphId).getContext('2d');

  // Create graph
  let chart = new Chart(ctx, {
      type: 'scatter',

      data: {
          datasets: []
      },

      options: {
        elements: {
          line: {
            tension: 0, // disables bezier curves
            fill: false,
          }
        },
        responsive: true,
        title: {
          display: true,
          text: "Title"
        },
        tooltips: {
          mode: 'index',
          intersect: false,
        },
        hover: {
          mode: 'nearest',
          intersect: true
        },
        scales: {
          xAxes: [{
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Month'
            }
          }],
          yAxes: [{
            display: true,
            scaleLabel: {
              display: true,
              labelString: 'Value'
            }
          }]
        }
      }
  });

  this.autorun(() => {

    // Update graph with data
    let data = undefined;
    try {
      data = this.data.graph;
    }
    catch(err) {
      return;
    }

    // Set title etc
    chart.config.options.title.text = data.name;
    chart.config.options.scales.xAxes[0].scaleLabel.labelString = data.x_axis;
    chart.config.options.scales.yAxes[0].scaleLabel.labelString = data.y_axis;

    // Colors
    let colors = palette('mpn65', data.series.length);

    // Transform data to chart.js scatter format.
    datasets = lodash.map(data.series, function(serie, idx) {
      data = lodash.zipWith(serie.x, serie.y, function(x, y) {
        return {x: x, y: y};
      });
      dataset = {label: serie.label, borderColor: '#' + colors[idx], data: data,
                 showLine: true};
      return dataset;
    });
    chart.data.datasets = datasets;
    chart.update();

  });


});
