/////////////////////////////////////////////////////////
/////////////// The Radar Chart Function ////////////////
/// mthh - 2017 /////////////////////////////////////////
// Inspired by the code of alangrafu and Nadieh Bremer //
// (VisualCinnamon.com) and modified for d3 v4 //////////
/////////////////////////////////////////////////////////

import * as d3 from 'd3'

const max = Math.max;
const sin = Math.sin;
const cos = Math.cos;
const HALF_PI = Math.PI / 2;

const RadarChart = function RadarChart(parent_selector, data, options, parent_component, node_id) {
	//Wraps SVG text - Taken from http://bl.ocks.org/mbostock/7555321
	const wrap = (text, width) => {
		text.each(function () {
			var text = d3.select(this),
				words = text.text().split(/\s+/).reverse(),
				word,
				line = [],
				lineNumber = 0,
				lineHeight = 1.4, // ems
				y = text.attr("y"),
				x = text.attr("x"),
				dy = parseFloat(text.attr("dy")),
				tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");

			//eslint-disable-next-line
			while (word = words.pop()) {
				line.push(word);
				tspan.text(line.join(" "));
				if (tspan.node().getComputedTextLength() > width) {
					line.pop();
					tspan.text(line.join(" "));
					line = [word];
					tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
				}
			}
		});
	}//wrap

	const cfg = {
		w: 600,				//Width of the circle
		h: 600,		
		x:0,
		y:0,		//Height of the circle
		margin: { top: 20, right: 20, bottom: 20, left: 20 }, //The margins of the SVG
		levels: 3,				//How many levels or inner circles should there be drawn
		maxValue: 0, 			//What is the value that the biggest circle will represent
		labelFactor: 1.75, 	//How much farther than the radius of the outer circle should the labels be placed
		wrapWidth: 60, 		//The number of pixels after which a label needs to be given a new line
		opacityArea: 0.35, 	//The opacity of the area of the blob
		dotRadius: 1, 			//The size of the colored circles of each blog
		opacityCircles: 0.1, 	//The opacity of the circles of each blob
		strokeWidth: 1, 		//The width of the stroke around each blob
		roundStrokes: false,	//If true the area and stroke will follow a round path (cardinal-closed)
		color: d3.scaleOrdinal(d3.schemeCategory10),	//Color function,
		format: '.2f',
		unit: '',
		legend: false,
		fontsize: '6px'
	};

	//Put all of the options into a variable called cfg
	if ('undefined' !== typeof options) {
		for (var i in options) {
			if ('undefined' !== typeof options[i]) { cfg[i] = options[i]; }
		}//for i
	}//if

	//If the supplied maxValue is smaller than the actual one, replace by the max in the data
	// var maxValue = max(cfg.maxValue, d3.max(data, function(i){return d3.max(i.map(function(o){return o.value;}))}));
	let maxValue = 0;
	for (let j = 0; j < data.length; j++) {
		for (let i = 0; i < data[j].axes.length; i++) {
			data[j].axes[i]['id'] = data[j].name;
			if (data[j].axes[i]['value'] > maxValue) {
				maxValue = data[j].axes[i]['value'];
			}
		}
	}
	maxValue = max(cfg.maxValue, maxValue);

	//eslint-disable-next-line
	const allAxis = data[0].axes.map((i, j) => i.alias),	//Names of each axis
		total = allAxis.length,					//The number of different axes
		radius = Math.min(cfg.w / 2, cfg.h / 2), 	//Radius of the outermost circle
		Format = d3.format(cfg.format),			 	//Formatting
		angleSlice = Math.PI * 2 / total;		//The width in radians of each "slice"

	//Scale for the radius
	const rScale = d3.scaleLinear()
		.range([0, radius])
		.domain([0, maxValue]);

	/////////////////////////////////////////////////////////
	//////////// Create the container SVG and g /////////////
	/////////////////////////////////////////////////////////
	const parent = d3.select(parent_selector);

	//Remove whatever chart with the same id/class was present before
	// parent.select("svg").remove();

	//Initiate the radar chart SVG
	let svg = parent
	// .append("svg")
	// 	.attr("width", cfg.w + cfg.margin.left + cfg.margin.right)
	// 	.attr("height", cfg.h + cfg.margin.top + cfg.margin.bottom)
	// 	.attr("class", "radar");

	//Append a g element
	let g = svg.append("g")
		.attr("transform", "translate(" + (cfg.x) + "," + (cfg.y) + ")");

	/////////////////////////////////////////////////////////
	////////// Glow filter for some extra pizzazz ///////////
	/////////////////////////////////////////////////////////

	//Filter for the outside glow
	let filter = g.append('defs').append('filter').attr('id', 'glow'),

		//eslint-disable-next-line
		feGaussianBlur = filter.append('feGaussianBlur').attr('stdDeviation', '1').attr('result', 'coloredBlur'),
		feMerge = filter.append('feMerge'),
		//eslint-disable-next-line
		feMergeNode_1 = feMerge.append('feMergeNode').attr('in', 'coloredBlur'),
		//eslint-disable-next-line
		feMergeNode_2 = feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

	/////////////////////////////////////////////////////////
	/////////////// Draw the Circular grid //////////////////
	/////////////////////////////////////////////////////////

	//Wrapper for the grid & axes
	let axisGrid = g.append("g").attr("class", "axisWrapper");

	axisGrid.append("circle").attr("r", radius+3).attr("fill", "white")
	//Draw the background circles
	axisGrid.selectAll(".levels")
		.data(d3.range(1, (cfg.levels + 1)).reverse())
		.enter()
		.append("circle")
		.attr("class", "gridCircle")
		.attr("r", d => radius / cfg.levels * d)
		.style("fill", "#CDCDCD")
		.style("stroke", "#CDCDCD")
		.style("fill-opacity", cfg.opacityCircles)
		.style("filter", "url(#glow)")
		.on('click', ()=>{
			parent_component.$root.$emit("changeSelectedNode", node_id)
			// console.log(node_id)
			svg.selectAll(".selection").remove()
			svg.append("circle")
				.attr('cx', cfg.x)
				.attr('cy', cfg.y)
				.attr('r', cfg.w/2*1.7)
				.attr('class', "selection")
				.attr('fill', 'none')
				.attr('opacity', 0.5)
				.attr('stroke', 'gold')
				.attr('stroke-width', 2)
		});
	
	// if (selected){
	// 	// console.log(svg)
	// 	svg.selectAll(".selection").remove()
	// 	svg.append("circle")
	// 			.attr('cx', cfg.x)
	// 			.attr('cy', cfg.y)
	// 			.attr('r', cfg.w/2*1.8)
	// 			.attr('class', "selection")
	// 			.attr('fill', 'none')
	// 			.attr('opacity', 0.5)
	// 			.attr('stroke', 'gold')
	// 			.attr('stroke-width', 2)
	// }

	// Text indicating at what % each level is
	// axisGrid.selectAll(".axisLabel")
	// 	.data(d3.range(1, (cfg.levels + 1)).reverse())
	// 	.enter().append("text")
	// 	.attr("class", "axisLabel")
	// 	.attr("x", 4)
	// 	.attr("y", d => -d * radius / cfg.levels)
	// 	.attr("dy", "0.4em")
	// 	.style("font-size", cfg.fontsize)
	// 	.attr("fill", "#737373")
	// 	.text(d => Format(maxValue * d / cfg.levels) + cfg.unit);

	/////////////////////////////////////////////////////////
	//////////////////// Draw the axes //////////////////////
	/////////////////////////////////////////////////////////

	//Create the straight lines radiating outward from the center
	var axis = axisGrid.selectAll(".axis")
		.data(allAxis)
		.enter()
		.append("g")
		.attr("class", "axis");
	//Append the lines
	axis.append("line")
		.attr("x1", 0)
		.attr("y1", 0)
		.attr("x2", (d, i) => rScale(maxValue * 1.1) * cos(angleSlice * i - HALF_PI))
		.attr("y2", (d, i) => rScale(maxValue * 1.1) * sin(angleSlice * i - HALF_PI))
		.attr("class", "line")
		.style("stroke", "white")
		.style("stroke-width", "2px");

	//Append the labels at each axis
	axis.append("text")
		.attr("class", "legend")
		.style("font-size", cfg.fontsize)
		.attr("text-anchor", "middle")
		.attr("dy", "0.35em")
		.attr("x", (d, i) => rScale(maxValue * cfg.labelFactor) * cos(angleSlice * i - HALF_PI + 0.3))
		.attr("y", (d, i) => rScale(maxValue * cfg.labelFactor) * sin(angleSlice * i - HALF_PI + 0.2))
		.text(d => {
			return d
		})
		.call(wrap, cfg.wrapWidth);

	/////////////////////////////////////////////////////////
	//////////////////// Draw error bars ////////////////////
	/////////////////////////////////////////////////////////
	// console.log(data)
	var error_bar = axisGrid.selectAll(".error_bar")
		.data(data[1].axes)
		.enter()
		.append("g")
		.attr("class", "error_bar");
	//Append the lines
	error_bar.append("line")
		.attr("x1", (d, i) => {
			// console.log(d)
			return rScale(d['quantile_25']) * cos(angleSlice * i - HALF_PI)})
		.attr("y1", (d, i) => rScale(d['quantile_25']) * sin(angleSlice * i - HALF_PI))
		.attr("x2", (d, i) => rScale(d['quantile_75']) * cos(angleSlice * i - HALF_PI))
		.attr("y2", (d, i) => rScale(d['quantile_75']) * sin(angleSlice * i - HALF_PI))
		.attr("class", "line")
		.style("stroke", "rgb(100, 100, 100)")
		.style("stroke-width", "2px");
	
	error_bar.append("line")
	.attr("x2", (d, i) => {
		// console.log(d)
		return rScale(d['quantile_75']) * cos(angleSlice * i - HALF_PI) + rScale(0.05) * sin(angleSlice * i + HALF_PI)})
	.attr("y2", (d, i) => rScale(d['quantile_75']) * sin(angleSlice * i - HALF_PI) - rScale(0.05) * cos(angleSlice * i + HALF_PI))
	.attr("x1", (d, i) => rScale(d['quantile_75']) * cos(angleSlice * i - HALF_PI) - rScale(0.05) * sin(angleSlice * i + HALF_PI))
	.attr("y1", (d, i) => rScale(d['quantile_75']) * sin(angleSlice * i - HALF_PI) + rScale(0.05) * cos(angleSlice * i + HALF_PI))
	.attr("class", "line")
	.style("stroke", "rgb(100, 100, 100)")
	.style("stroke-width", "2px")
	.style("stroke-linecap", "square")

	error_bar.append("line")
	.attr("x2", (d, i) => {
		// console.log(d)
		return rScale(d['quantile_25']) * cos(angleSlice * i - HALF_PI) + rScale(0.05) * sin(angleSlice * i + HALF_PI)})
	.attr("y2", (d, i) => rScale(d['quantile_25']) * sin(angleSlice * i - HALF_PI) - rScale(0.05) * cos(angleSlice * i + HALF_PI))
	.attr("x1", (d, i) => rScale(d['quantile_25']) * cos(angleSlice * i - HALF_PI) - rScale(0.05) * sin(angleSlice * i + HALF_PI))
	.attr("y1", (d, i) => rScale(d['quantile_25']) * sin(angleSlice * i - HALF_PI) + rScale(0.05) * cos(angleSlice * i + HALF_PI))
	.attr("class", "line")
	.style("stroke", "rgb(100, 100, 100)")
	.style("stroke-width", "2px")
	.style("stroke-linecap", "square")

	error_bar.append("line")
	.attr("x2", (d, i) => {
		// console.log(d)
		return rScale(d['median']) * cos(angleSlice * i - HALF_PI) + rScale(0.05) * sin(angleSlice * i + HALF_PI)})
	.attr("y2", (d, i) => rScale(d['median']) * sin(angleSlice * i - HALF_PI) - rScale(0.05) * cos(angleSlice * i + HALF_PI))
	.attr("x1", (d, i) => rScale(d['median']) * cos(angleSlice * i - HALF_PI) - rScale(0.05) * sin(angleSlice * i + HALF_PI))
	.attr("y1", (d, i) => rScale(d['median']) * sin(angleSlice * i - HALF_PI) + rScale(0.05) * cos(angleSlice * i + HALF_PI))
	.attr("class", "line")
	.style("stroke", "rgb(100, 100, 100)")
	.style("stroke-width", "2px")
	.style("stroke-linecap", "square")

	// error_bar.append("circle")
	// 	.attr("class", "error_bar_circle")
	// 	.attr("r", cfg.dotRadius)
	// 	.attr("cx", (d, i) => rScale(d['mean']) * cos(angleSlice * i - HALF_PI))
	// 	.attr("cy", (d, i) => rScale(d['mean']) * sin(angleSlice * i - HALF_PI))
	// 	.style("fill", "rgb(59, 119, 176)")
	// 	.style("fill-opacity", 0.8);



	/////////////////////////////////////////////////////////
	///////////// Draw the radar chart blobs ////////////////
	/////////////////////////////////////////////////////////

	//The radial line function
	const radarLine = d3.radialLine()
		.curve(d3.curveLinearClosed)
		.radius(d => rScale(d.value))
		.angle((d, i) => i * angleSlice);

	if (cfg.roundStrokes) {
		radarLine.curve(d3.curveCardinalClosed)
	}

	//Create a wrapper for the blobs
	const blobWrapper = g.selectAll(".radarWrapper")
		.data(data)
		.enter().append("g")
		.attr("class", "radarWrapper");

	//Append the backgrounds
	blobWrapper
		.append("path")
		.attr("class", "radarArea")
		.attr("d", d => radarLine(d.axes))
		//eslint-disable-next-line
		.style("fill", (d, i) => cfg.color(i))
		.style("fill-opacity", d=>{
			if (d['name'] == "Mean"){return 0.3}
			return cfg.opacityArea
		})
		// .on('mouseover', function (d, i) {
		// 	//Dim all blobs
		// 	// parent.selectAll(".radarArea")
		// 	// 	.transition().duration(200)
		// 	// 	.style("fill-opacity", 0.1);
		// 	// //Bring back the hovered over blob
		// 	// d3.select(this)
		// 	// 	.transition().duration(200)
		// 	// 	.style("fill-opacity", 0.7);
		// })
		.on('mouseout', () => {
			//Bring back all blobs
			parent.selectAll(".radarArea")
				.transition().duration(200)
				.style("fill-opacity", cfg.opacityArea);
		});

	//Create the outlines
	blobWrapper.append("path")
		.attr("class", "radarStroke")
		//eslint-disable-next-line
		.attr("d", function (d, i) { return radarLine(d.axes); })
		.style("stroke-width", cfg.strokeWidth + "px")
		.style("stroke", (d, i) => cfg.color(i))
		.style("fill", "none")
		.style("filter", "url(#glow)")
		// .style("stroke-opacity", 0.7)
		.style('stroke-opacity', d=>{
			if (d['name'] == "Mean"){return 0}
			else {return 0.7}
		}
		)

	//Append the circles
	blobWrapper.selectAll(".radarCircle")
		.data(d => d.axes)
		.enter()
		.append("circle")
		.attr("class", "radarCircle")
		.attr("r", cfg.dotRadius)
		.attr("cx", (d, i) => rScale(d.value) * cos(angleSlice * i - HALF_PI))
		.attr("cy", (d, i) => rScale(d.value) * sin(angleSlice * i - HALF_PI))
		.style("fill", (d) => cfg.color(d.id))
		.style("fill-opacity", d=>{
			if (d.id == "Mean"){return 0}
			else {return 0.8}
		});

	/////////////////////////////////////////////////////////
	//////// Append invisible circles for tooltip ///////////
	/////////////////////////////////////////////////////////

	//Wrapper for the invisible circles on top
	const blobCircleWrapper = g.selectAll(".radarCircleWrapper")
		.data(data)
		.enter().append("g")
		.attr("class", "radarCircleWrapper");

	//Append a set of invisible circles on top for the mouseover pop-up
	blobCircleWrapper.selectAll(".radarInvisibleCircle")
		.data(d => d.axes)
		.enter().append("circle")
		.attr("class", "radarInvisibleCircle")
		.attr("r", cfg.dotRadius * 1.5)
		.attr("cx", (d, i) => rScale(d.value) * cos(angleSlice * i - HALF_PI))
		.attr("cy", (d, i) => rScale(d.value) * sin(angleSlice * i - HALF_PI))
		.style("fill", "none")
		.style("pointer-events", "all")
		.on("mouseover", function (d, i) {
			var offset_x = rScale(d.value) * cos(angleSlice * i - HALF_PI) >= 0 ? cfg.w/4 : 0
			var offset_y = rScale(d.value) * cos(angleSlice * i - HALF_PI) >= 0 ? cfg.w/4 : -cfg.w/4
			tooltip
				.attr('x', this.cx.baseVal.value+offset_x)
				.attr('y', this.cy.baseVal.value+offset_y)
				.transition()
				.style("fill",cfg.color(d.id))
				.style('opacity', 1)
				.style('display', 'block')
				.text(Format(d.value) + cfg.unit);
		})
		.on("mouseout", function () {
			tooltip.transition()
				.style('display', 'none').text('');
		});

	const tooltip = g.append("text")
		.attr("class", "r_tooltip")
		.attr('x', 0)
		.attr('y', 0)
		.style("font-size", "10px")
		.style("font-weight", "bold")
		.style('display', 'none')
		.style('opacity', 0)
		.attr("text-anchor", "middle")
		.attr("dy", "0.35em");

	if (cfg.legend !== false && typeof cfg.legend === "object") {
		let legendZone = svg.append('g');
		let names = data.map(el => el.name);
		if (cfg.legend.title) {
			//eslint-disable-next-line
			let title = legendZone.append("text")
				.attr("class", "title")
				.attr('transform', `translate(${cfg.legend.translateX},${cfg.legend.translateY})`)
				.attr("x", cfg.w - 70)
				.attr("y", 10)
				.attr("font-size", "12px")
				.attr("fill", "#404040")
				.text(cfg.legend.title);
		}
		let legend = legendZone.append("g")
			.attr("class", "legend")
			.attr("height", 100)
			.attr("width", 200)
			.attr('transform', `translate(${cfg.legend.translateX},${cfg.legend.translateY + 20})`);
		// Create rectangles markers
		legend.selectAll('rect')
			.data(names)
			.enter()
			.append("rect")
			.attr("x", cfg.w - 65)
			.attr("y", (d, i) => i * 20)
			.attr("width", 10)
			.attr("height", 10)
			.style("fill", (d, i) => cfg.color(i));
		// Create labels
		legend.selectAll('text')
			.data(names)
			.enter()
			.append("text")
			.attr("x", cfg.w - 52)
			.attr("y", (d, i) => i * 20 + 9)
			.attr("font-size", "11px")
			.attr("fill", "#737373")
			.text(d => d);
	}
	return svg;
}

export { RadarChart }