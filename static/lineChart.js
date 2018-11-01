const DrawLineChart = function DrawLineChart(parent_selector, data) {

  // Define margins, dimensions, and some line colors
  const margin = {top: 40, right: 120, bottom: 30, left: 40};
  const width = 1000 - margin.left - margin.right;
  const height = 600 - margin.top - margin.bottom;
  const colors = ['red', 'green', 'limegreen', 'blue', 'skyblue', 'gray', 'magenta'];
    
  // Define the scales and tell D3 how to draw the line
  const x = d3.scaleLinear().domain([0, 15]).range([0, width]);     
  const y = d3.scaleLinear().domain([0, 110]).range([height, 0]);
  const line = d3.line().x(d => x(d.week)).y(d => y(d.score));

  /////////////////////////////////////////////////////////
  //////////// Create the container SVG and g /////////////
  /////////////////////////////////////////////////////////
  const parent = d3.select(parent_selector);


  // Create areas for the chart and user input
  const chart = parent.append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform','translate('+ margin.left+','+margin.top+')');

  const userInput = parent.append('div')
    .style('width', width + margin.left + margin.right)
    .style('height', '10em')
    .style('display', 'flex')
    .style('flex-flow', 'column wrap');  
    
  // Add the axes and a title
  const xAxis = d3.axisBottom(x).tickFormat(d3.format('1'));
  //const xAxis = d3.axisBottom(x).tickFormat(d3.format('.4'));
  const yAxis = d3.axisLeft(y).tickFormat(d3.format('1'));
  //const yAxis = d3.axisLeft(y).tickFormat(d3.format('.2s'));
  chart.append('g').call(yAxis); 
  chart.append('g').attr('transform', 'translate(0,' + height + ')').call(xAxis);
  chart.append('text').html('Scores over weeks').attr('x', 200);
    
  // Load the data
  let learners = data;
  
  drawUserInput();
  drawChart();  


  //d3.json('state-scores.json', d => {
  //  learners = d;
  //  drawUserInput();
  //  drawChart();  
  //});
    
  function drawUserInput() {
    userInput.selectAll('checkboxes')
      .data(learners).enter()
      .append('label')
      .style('width', '14em')
      .html(d => d.name)
      .append('input')
      .attr('type', 'checkbox')
      .property('checked', d => {
        if (d.show) {
          const color = colors.shift();
          d.color = color;
          colors.push(color);
        }
        return d.show;
      })
      .on('change', d => {
        d.show = !d.show;
        if (!d.color) {
          const color = colors.shift();
          d.color = color;
          colors.push(color);
        }
        drawChart();
      });
  }
    
  function drawChart() {  
    const visibleLearners = learners.filter(s => s.show);
    const lines = chart.selectAll('.score-line').data(visibleLearners, d => d.name);
    lines.exit().remove();
    lines.enter().append('path')
      .attr('class', 'score-line')
      .attr('fill', 'none')
      .attr('stroke', d => d.color)
      .attr('stroke-width', 2)
      .datum(d => d.history)
      .attr('d', line);
    drawLegend();
  }
    
  function drawLegend() {
    const visibleLearners = learners.filter(s => s.show);
    const labelHeight = 14;
    
    // Create some nodes
    const labels = visibleLearners.map(s => {
      return {
        fx: 0,
        targetY: y(s.currentScore)
      };
    });
    
    // Define a custom force
    const forceClamp = (min, max) => {
      let nodes;
      const force = () => {
        nodes.forEach(n => {
          if (n.y > max) n.y = max;
          if (n.y < min) n.y = min;
        });
      };
      force.initialize = (_) => nodes = _;
      return force;
    }
    
    // Set up the force simulation
    const force = d3.forceSimulation()
      .nodes(labels)
      .force('collide', d3.forceCollide(labelHeight / 2))
      .force('y', d3.forceY(d => d.targetY).strength(1))    
      .force('clamp', forceClamp(0, height))
      .stop();
    
    // Execute the simulation
    for (let i = 0; i < 300; i++) force.tick();
    
    // Assign values to the appropriate marker
    labels.sort((a, b) => a.y - b.y);
    visibleLearners.sort((a, b) => b.currentScore - a.currentScore);
    visibleLearners.forEach((state, i) => state.y = labels[i].y);
    
    // Add labels
    const legendItems = chart.selectAll('.legend-item').data(visibleLearners, d => d.name);
    legendItems.exit().remove();
    legendItems.attr('y', d => d.y);
    legendItems.enter().append('text')
      .attr('class', 'legend-item')
      .html(d => d.name)
      .attr('fill', d => d.color)
      .attr('font-size', labelHeight)
      .attr('alignment-baseline', 'middle')
      .attr('x', width)
      .attr('dx', '.5em')
      .attr('y', d => d.y);
  }
}
