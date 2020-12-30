<template>
    <svg :id="'svg_micro_' + student_id + '_' + expand_question_id" style="height: 380px; width:100%; overflow:hidden"/>
</template>

<script>
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap-vue/dist/bootstrap-vue.css';
    import * as d3 from 'd3';
    import * as axios from 'axios'
    export default {
        name: 'MicroView',
        components: {
        },
        props:["student_id", "expand_question_id" ,"z_score_threshold"],
        data() {
            return {
                userID: [this.student_id],
                probID: [this.expand_question_id],
                window_width: parseInt(document.getElementsByClassName("meso_card_body")[0].offsetWidth)-80,
                lineChart_height:270,
                lineChart_width: parseInt(document.getElementsByClassName("meso_card_body")[0].offsetWidth)-500,
                legend_width: 0,
                legend_height: 30,
                margin:{
                    left: 0,
                    top: 10,
                    bottom: 20
                },
                userGap: 50,
                keyColor: {
                    bbox: '#084177',
                    mouse: '#cd8d7b',//'#3e0877',
                    headpose: '#687466',//'#773e08',
                    axis: '#fbc490',
                    barbgm: '#d2c6b2'
                },
                yAxisWidth:18,
                timePeriod: {}
            };
        },
        mounted() {
            this.$watch("expand_question_id", (n, o)=>{
                if(n != o && n != "") {
                    d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id).selectAll('*').remove()
                    d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id).selectAll('.xAxis').remove()
                    this.probID = [n]
                    this.drawChart(this.userID, this.probID);
                }
            })
            this.$watch("z_score_threshold", (n, o)=>{
                if(n != o && n != ""&&this.expand_question_id!="") {
                    d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id).selectAll('*').remove()
                    // this.probID = [n]
                    this.drawChart(this.userID, this.probID);
                }
            })
            this.$root.$on('pause',()=>{
                d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id)
                    .select('.selectedTime').transition()
            })

            this.$root.$on('play',(time)=>{
                var x_axis = d3.scaleLinear().domain(this.timePeriod[this.student_id])
                        .range([0, this.lineChart_width])
                var vm = this
                // var coords = d3.mouse(this)
                d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id).select('.lineChart').select('.selectedTime').remove()
                d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id).select('.lineChart').append('path')
                    .attr('class', 'selectedTime')
                    .attr('d','M'+ x_axis(vm.timePeriod[this.student_id][0]+time*1000)+ ',0L'+ x_axis(vm.timePeriod[this.student_id][0]+time*1000)+ ','+ (vm.lineChart_height + vm.margin.top + vm.margin.bottom))
                    .style('stroke', vm.keyColor.bbox)
                    .style('stroke-width', 1.5)
                    .transition()
                    .ease(d3.easeLinear)
                    .duration(vm.timePeriod[this.student_id][1] - (vm.timePeriod[this.student_id][0]+time*1000))
                    .attr('d','M'+ x_axis(vm.timePeriod[this.student_id][1])+ ',0L'+ x_axis(vm.timePeriod[this.student_id][1])+ ','+ (vm.lineChart_height + vm.margin.top + vm.margin.bottom))
            })

        },
        methods: {
            drawChart(userID, probID){
                // console.log(this.window_width, this.lineChart_width)
                for(let i in userID){
                    var user_meso = d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id)
                        .append('g')
                        .attr('id', userID[i] + '_' + probID[i])
                        .attr('height', this.lineChart_height)
                        .attr('width', this.lineChart_width)
                        .attr('transform', 'translate(' + this.legend_width+',' + (this.legend_height + this.margin.top + (this.margin.bottom + this.lineChart_height + this.margin.top + this.userGap)*i) + ')'),
                        g_lineChart = user_meso.append('g')
                        .attr('class', 'lineChart')
                        .attr('transform', 'translate('+ (this.window_width - this.lineChart_width)/2 + ',0)'),
                        g_glyphChart = user_meso.append('g')
                        .attr('class', 'glyphChart')
                        .attr('transform', 'translate('+ (this.window_width - this.lineChart_width)/2 + ',' + this.lineChart_height/2 +')'),
                        g_heatmapLChart = user_meso.append('g')
                        .attr('class', 'heatmapChart')
                        .attr('transform', 'translate('+ ((this.window_width - this.lineChart_width)/2 - this.lineChart_height/2) + ',0)'),
                        g_heatmapRChart = user_meso.append('g')
                        .attr('class', 'heatmapChart')
                        .attr('transform', 'translate('+ (this.window_width + this.lineChart_width)/2 + ',0)'),
                        g_legend = d3.select('#svg_micro_' + this.student_id + '_' + this.expand_question_id)
                        .append('g')
                        .attr('id', userID[i] + '_' + probID[i] + '_legend')
                        .attr('transform', 'translate(0,' + (this.margin.top + (this.margin.bottom + this.lineChart_height + this.margin.top + this.userGap)*i) + ')')
                    this.drawLineChart(userID[i],probID[i], g_lineChart, g_glyphChart,g_heatmapLChart, g_heatmapRChart)
                    this.appendLegend(g_legend)              
                }
            },
            appendLegend(svg){
                var rectWidth = 25, rectHeight = this.lineChart_height/2, colorBlock = 12, blockGap = 80*1.3, fontSize= 12;
                var Ylabel = ['X/Yaw', 'Y/Pitch'], Xlabel = ['Peers on This Question', 'Current Student on Other Questions'], Clabel_New =['Mouse Position', 'Head Pose', 'Head Position (Bbox)'], Clabel = ['mouse', 'headpose', 'bbox'],
                    Eventlabel = [
                        'blur_focus',
                        'copy_paste',
                        'headpose',
                        'no_face'
                    ],
                    Eventlabel_text = [
                        'Blur & Focus',
                        'Copy & Paste',
                        'Abnormal Head Pose',
                        'Face Disappearance'
                    ];
                for(let i in Ylabel) {
                    svg.append('rect')
                    .attr('width', rectWidth)
                    .attr('height', rectHeight)
                    .style('stroke', 'none')
                    .style('fill', this.keyColor.barbgm)
                    .style('opacity', 0.2)
                    .attr('transform', 'translate('+ (this.window_width/2 - this.lineChart_width/2 - rectHeight - this.yAxisWidth-rectWidth) + ',' + (this.legend_height + (rectHeight + this.margin.top + this.margin.bottom)*i) + ')')
                    svg.append('text')
                    .text(Ylabel[i])
                    .style('text-anchor', 'middle')
                    .attr('transform', 'translate(' + (this.window_width/2 - this.lineChart_width/2 - rectHeight - this.yAxisWidth-rectWidth/2 + rectWidth/5) + ',' + (this.legend_height + rectHeight/2 + (rectHeight + this.margin.top + this.margin.bottom)*i) + '),rotate(-90)')
                    svg.append('rect')
                    .attr('width', rectWidth)
                    .attr('height', rectHeight)
                    .style('stroke', 'none')
                    .style('fill', this.keyColor.barbgm)
                    .style('opacity', 0.2)
                    .attr('transform', 'translate('+ (this.window_width/2 + this.lineChart_width/2 + this.yAxisWidth + rectHeight) + ',' + (this.legend_height + (rectHeight + this.margin.top + this.margin.bottom)*i) + ')')
                    svg.append('text')
                    .text(Ylabel[i])
                    .style('text-anchor', 'middle')
                    .attr('transform', 'translate(' + (this.window_width/2 + this.lineChart_width/2 + this.yAxisWidth + rectHeight*1.05) + ',' + (this.legend_height + rectHeight/2 + (rectHeight + this.margin.top + this.margin.bottom)*i) + '),rotate(90)')
                }
                for(let i in Xlabel){
                    svg.append('rect')
                    .attr('width', rectHeight + rectWidth *1.5)
                    .attr('height', rectWidth)
                    .style('stroke', 'none')
                    .style('fill', this.keyColor.barbgm)
                    .style('opacity', 0.2)
                    .attr('transform', 'translate('+ (this.legend_width + this.window_width/2 - this.lineChart_width/2 - rectHeight - this.yAxisWidth - rectWidth*0.75 + i*(this.lineChart_width + 2*this.yAxisWidth + rectHeight)) + ',' + (this.legend_height - rectWidth*1.4) + ')')
                    svg.append('text')
                    .text(Xlabel[i])
                    .style('text-anchor', 'middle')
                    .style('font-size', 10)
                    .attr('transform', 'translate(' + (this.legend_width + this.window_width/2 - this.lineChart_width/2 - rectHeight/2 - this.yAxisWidth + i*(this.lineChart_width + 2*this.yAxisWidth + rectHeight)) + ',' + (this.legend_height - rectWidth*0.8) + ')')
                }
                for(let i in Clabel) {
                    if(Clabel[i] == "bbox") {
                        svg.append('rect')
                        .attr('width', colorBlock)
                        .attr('height', colorBlock)
                        .style('fill', this.keyColor[Clabel[i]])
                        .attr('transform', 'translate(' + (rectHeight*1.7 + i* blockGap) + ','+ (-colorBlock/1.5)+')' )
                    } else if (Clabel[i] == 'headpose') {
                        svg.append('path')
                        .attr('d', 'M' + (rectHeight*1.7 + i* blockGap) + ',' + (-colorBlock/3) + 'L' + (rectHeight*1.7 + colorBlock + i* blockGap) + ',' + (-colorBlock/3))
                        .style('stroke', this.keyColor[Clabel[i]])
                        .style('stroke-width', 2)
                    } else {
                        svg.append('path')
                        .attr('d', 'M' + (rectHeight*1.7 + i* blockGap) + ',' + (-colorBlock/3) + 'L' + (rectHeight*1.7 + colorBlock + i* blockGap) + ',' + (-colorBlock/3))
                        .style('stroke', this.keyColor[Clabel[i]])
                        .style('stroke-dasharray', ("4, 2"))
                        .style('stroke-width', 3)
                    }
                    
                    svg.append('text')
                    .text(Clabel_New[i])
                    .style('font-size', fontSize)
                    .attr('transform', 'translate(' + (rectHeight*1.7 + 2 + i* blockGap + colorBlock) + ',' + (colorBlock - colorBlock/1.1)+')')
                }
                for(let i in Eventlabel) {

                    if (i != 3){
                        svg.append('svg:image')
                            .attr('xlink:href', require('../../static/images/'+Eventlabel[i]+'.svg'))
                            .attr('transform', 'translate(' + (rectHeight*1.7 + i* blockGap) + ',' + colorBlock/1.5+ ')')
                            .attr('width', colorBlock)
                            .attr('height', colorBlock)

                        
                        svg.append('text')
                        .text(Eventlabel_text[i])
                        .style('font-size', fontSize)
                        .attr('transform', 'translate(' + (rectHeight*1.7 + i* blockGap + colorBlock + 2) + ',' + (colorBlock + colorBlock/2.2)+')')
                        }
                    else{
                        svg.append('svg:image')
                            .attr('xlink:href', require('../../static/images/'+Eventlabel[i]+'.svg'))
                            .attr('transform', 'translate(' + (rectHeight*1.7 + i* blockGap +33) + ',' + colorBlock/1.5+ ')')
                            .attr('width', colorBlock)
                            .attr('height', colorBlock)

                        
                        svg.append('text')
                        .text(Eventlabel_text[i])
                        .style('font-size', fontSize)
                        .attr('transform', 'translate(' + (rectHeight*1.7 + i* blockGap + colorBlock + 35) + ',' + (colorBlock + colorBlock/2.2)+')')
                        }
                }
                svg.append('text')
                .text('Cost Time/ms')
                .attr('transform', 'translate(' + this.window_width/2 + ',' + (this.lineChart_height + this.margin.top*2.5 + this.margin.bottom*2 + this.legend_height)+ ')')
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
            },
            appendEventCover(g_lineChart, userID){
                var vm = this
                var x_axis = d3.scaleLinear().domain(this.timePeriod[userID])
                        .range([0, this.lineChart_width])
                var g_event = g_lineChart.append('rect')
                    .attr('class', 'eventCover')
                    .attr('width', this.lineChart_width)
                    .attr('height', this.lineChart_height+this.margin.top+this.margin.bottom)
                    .attr('fill', 'white')
                    .attr('stroke', 'white')
                    .attr('opacity', 0.01)
                g_event.on('click', function(){
                        var coords = d3.mouse(this)
                        g_lineChart.select('.selectedTime').remove()
                        // console.log(x_axis.invert(coords[0]))
                        g_lineChart.append('path')
                            .attr('class', 'selectedTime')
                            .attr('d','M'+ coords[0]+ ',0L'+ coords[0]+ ','+ (vm.lineChart_height + vm.margin.top + vm.margin.bottom))
                            .style('stroke', vm.keyColor.bbox)
                            .style('stroke-width', 1.5)
                            .transition()
                            .ease(d3.easeLinear)
                            .duration(vm.timePeriod[userID][1] - x_axis.invert(coords[0]))
                            .attr('d','M'+ x_axis(vm.timePeriod[userID][1])+ ',0L'+ x_axis(vm.timePeriod[userID][1])+ ','+ (vm.lineChart_height + vm.margin.top + vm.margin.bottom))
                        
                        vm.$root.$emit("chooseTimestamp", [vm.userID[0], vm.probID[0], x_axis.invert(coords[0])])
                    })
                g_event.on("dblclick", ()=>{
                    this.$root.$emit("takeScreenshot")
                })
            },
            drawLineChart(userID,probID, svg_micro, g_glyphChart, g_heatmapLChart, g_heatmapRChart) {
                let x_mouse, yaw_head,x_bbox, y_mouse, y_bbox,  pitch_head;
                axios.get("/api/mouse_raw_data/" + userID + "/"+ probID + "/X").then(response=>{
                    // x_mouse = JSON.parse(response.data.replace(/'/g, '"')).data
                    x_mouse = response.data.data
                    x_mouse.sort((a,b)=>a['timestamp']-b['timestamp'])
                    this.timePeriod[userID] = [x_mouse[0]['timestamp'], x_mouse[x_mouse.length-1]['timestamp']]
                    this._drawLine(x_mouse,0,svg_micro, this.keyColor.mouse, 'X', userID)
                    this.drawGlyphChart(userID,probID, g_glyphChart)
                    // console.log(x_mouse)
                    axios.get("/api/bbox_raw_data/" + userID + "/"+ probID + "/X").then(response=>{
                        // x_bbox = JSON.parse(response.data.replace(/'/g, '"')).data
                        x_bbox = response.data.data
                        x_bbox.sort((a,b)=>a['timestamp']-b['timestamp'])
                        this._drawRiver(x_bbox,0,svg_micro, this.keyColor.bbox, 'X',userID) 
                        // console.log(x_bbox)                 
                    })
                    axios.get("/api/bbox_raw_data/" + userID + "/"+ probID + "/Y").then(response=>{
                        // y_bbox = JSON.parse(response.data.replace(/'/g, '"')).data 
                        y_bbox = response.data.data
                        y_bbox.sort((a,b)=>a['timestamp']-b['timestamp'])
                        this._drawRiver(y_bbox,1,svg_micro, this.keyColor.bbox, 'Y', userID) 
                    })
                    axios.get("/api/headpose_raw_data/" + userID + "/"+ probID + "/yaw").then(response=>{
                        // yaw_head = JSON.parse(response.data.replace(/'/g, '"')).data
                        yaw_head = response.data.data
                        yaw_head.sort((a,b)=>a['timestamp']-b['timestamp'])
                        this._drawLine(yaw_head,0,svg_micro, this.keyColor.headpose, 'yaw', userID)                    
                    })
                    axios.get("/api/headpose_raw_data/" + userID + "/"+ probID + "/pitch").then(response=>{
                        // pitch_head = JSON.parse(response.data.replace(/'/g, '"')).data
                        pitch_head = response.data.data
                        pitch_head.sort((a,b)=>a['timestamp']-b['timestamp'])
                        // console.log(pitch_head)
                        this._drawLine(pitch_head,1,svg_micro, this.keyColor.headpose, 'pitch', userID)  
                        this.appendEventCover(svg_micro, userID)                     
                    })
                    axios.get("/api/mouse_raw_data/" + userID + "/"+ probID + "/Y").then(response=>{
                        // y_mouse = JSON.parse(response.data.replace(/'/g, '"')).data
                        y_mouse = response.data.data
                        y_mouse.sort((a,b)=>a['timestamp']-b['timestamp'])
                        this._drawLine(y_mouse,1,svg_micro, this.keyColor.mouse, 'Y', userID)       
                        // console.log(y_mouse)      
                    })
                    this.drawheatmapLChart(userID,probID, g_heatmapLChart)
                    this.drawheatmapRChart(userID,probID, g_heatmapRChart)

                })
                
            },
            _drawLine(data, loc, svg, lineColor, label, userID) {
                let g = svg.append('g').attr('transform','translate(0,' + (this.lineChart_height/2*loc + (this.margin.top+ this.margin.bottom)*loc) + ')')
                let x_axis;
                if(label == 'X'){
                    x_axis = d3.scaleLinear().domain([data[0].timestamp, data[data.length-1].timestamp])
                        .range([0, this.lineChart_width])
                } else {
                    x_axis = d3.scaleLinear().domain(this.timePeriod[userID])
                    .range([0, this.lineChart_width])
                }
                var sliceF = 0;
                if(label != 'X') {
                    for(let i in data) {
                        if(data[i]['timestamp'] < this.timePeriod[userID][0]){
                            sliceF = i
                        }
                    }
                    // console.log(sliceF, data.length)
                    if(sliceF != 0) {
                        data.splice(0, Number(sliceF)+1);
                    }
                    // console.log(data.length)
                    for(let i in data) {
                        if(data[i]['timestamp'] > this.timePeriod[userID][1]){
                            data.splice(i,data.length-i)
                            break;
                        }
                    }
                    // console.log(data.length)
                }
                let y_axis = d3.scaleLinear().domain([-1, 1])
                    .range([this.lineChart_height/2, 0])
                let line = d3.line().x(function(d) {
                            return x_axis(Number(d['timestamp']))
                        }).y(function(d) {
                            return y_axis(Number(d[label]))
                        });
                if(label == 'pitch' || label == 'yaw'){
                    g.append('path')
                    .datum(data)
                    .attr('class', label + '_path')
                    .attr('d', line)
                    .style('fill', 'none')
                    .style('stroke', lineColor)
                    .attr('opacity', 0.5)
                    .style('stroke-width', 2)
                } else {
                    g.append('path')
                    .datum(data)
                    .attr('class', label + '_path')
                    .attr('d', line)
                    .style('fill', 'none')
                    .style('stroke', lineColor)
                    .attr('opacity', 0.7)
                    .style('stroke-width', 3)
                    .style('stroke-dasharray', ('3, 2'))
                }
                
                if(loc==1 && label == 'Y'){
                    let xAxis = g.append('g').attr('class', 'xAxis').attr('transform', 'translate(0,' + this.lineChart_height/2 + ')').call(d3.axisBottom(x_axis))
                    xAxis.selectAll('.tick').select('text').text(d=>(d - this.timePeriod[userID][0]).toFixed(0))
                }
                if(label == 'X' || label == 'Y') {
                    let yAxis = g.append('g').attr('class', 'yAxis').attr('transform', 'translate(0,0)').call(d3.axisLeft(y_axis).ticks(2))
                    yAxis.select('path').attr('stroke-width', this.yAxisWidth).style('stroke', this.keyColor.axis).style('opacity', 0.8).attr('transform', 'translate(' + (-this.yAxisWidth/2)+',0)')
                    yAxis.selectAll('.tick').select('line').style('opacity', 0.7).style('stroke-width', 1).attr('transform', 'translate(0,0)').attr('x2', -this.yAxisWidth).style('stroke-dasharray', "2,2")
                    yAxis.selectAll('.tick').select('text').attr('transform', 'translate(2,0)').attr('x', -this.yAxisWidth/2).attr('dy', 0).style('text-anchor', 'middle').style('font-weight', 'bold')
                }
                
            },
            _drawRiver(data, loc, svg, lineColor, label, userID) {
                let g = svg.append('g').attr('transform','translate(0,' + (this.lineChart_height/2*loc + (this.margin.top+ this.margin.bottom)*loc) + ')')
                // console.log(this.timePeriod)
                let x_axis = d3.scaleLinear().domain(this.timePeriod[userID])
                    .range([0, this.lineChart_width]),
                    y_axis = d3.scaleLinear().domain([-1, 1])
                    .range([this.lineChart_height/2, 0])
                let line = d3.line().x(function(d) {
                            return x_axis(Number(d['timestamp']))
                        }).y(function(d) {
                            return y_axis(Number(d['Y']))
                        });
                let themeData = []
                for(let i in data){
                    themeData.push({timestamp: data[i].timestamp, Y: data[i][label + '_min']})
                }
                for(let i in data) {
                    themeData.push({timestamp: data[data.length - 1 - i].timestamp, Y: data[data.length - 1 - i][label + '_max']})
                }
                var sliceF = 0;
                for(let i in themeData) {
                    if(themeData[i]['timestamp'] < this.timePeriod[userID][0] && i < themeData.length/2){
                        sliceF = i
                    }
                }
                if(sliceF != 0) {
                    themeData.splice(0, Number(sliceF) +1);
                    themeData.splice(themeData.length - Number(sliceF)-1, Number(sliceF)+1)
                }
                for(let i in themeData) {
                    if(themeData[i]['timestamp'] > this.timePeriod[userID][1] && i < themeData.length/2){
                        themeData.splice(i,(themeData.length/2-i)*2)
                        break;
                    }
                }
                g.append('path')
                    .datum(themeData)
                    .attr('class', 'theme_path')
                    .attr('d', line)
                    .style('fill', lineColor)
                    .style('stroke', lineColor)
                    .attr('opacity', 0.2)
                    .style('stroke-width', 2)


                let yAxis = g.append('g').attr('class', 'yAxis').attr('transform', 'translate(' + this.lineChart_width + ',0)').call(d3.axisRight(y_axis).ticks(2))
                yAxis.select('path').attr('stroke-width', this.yAxisWidth).style('stroke', this.keyColor.axis).style('opacity', 0.8).attr('transform', 'translate(' + this.yAxisWidth/2+',0)')
                yAxis.selectAll('.tick').select('line').style('opacity', 0.7).style('stroke-width', 1).attr('transform', 'translate(0,0)').attr('x2', this.yAxisWidth).style('stroke-dasharray', "2,2")
                yAxis.selectAll('.tick').select('text').attr('transform', 'translate(-2,0)').attr('x', this.yAxisWidth/2).attr('dy', 0).style('text-anchor', 'middle').style('font-weight', 'bold')
            },
            drawheatmapLChart(userID,probID, svg){
                let x_mouse, y_mouse,
                keyOrder_origin = ['bbox_min', 'headpose', 'bbox_max'],//, 'mouse'
                keyOrder = ['Bbox_lower', 'Head pose', 'Bbox_upper'],
                g_0 = svg.append('g'),
                g_1 = svg.append('g').attr('transform', 'translate(0, ' + (this.lineChart_height/2 + this.margin.top + this.margin.bottom) + ')');
                for(let i in keyOrder) {
                    svg.append('text')
                    .attr('transform', 'translate(' + ((this.lineChart_height/2/keyOrder.length)*i + this.lineChart_height/2/keyOrder.length/2 - this.yAxisWidth) + ','+ (this.lineChart_height/2 + (this.margin.top*2 + this.margin.bottom)/2.3) + ')')
                    .text(function(){
                        // let shortT = "", originT = keyOrder[i].split('_')
                        
                        // for(let i in originT){
                        //     if(i > 0) {
                        //         shortT = shortT + originT[i]
                        //     } else {
                        //         shortT = shortT + originT[i][0].toUpperCase()
                        //     }
                        // }
                        // return shortT
                        return keyOrder[i]
                    })
                    .style('fill', this.keyColor[keyOrder_origin[i]])
                    .style('font-size', 8)
                    .style('font-weight', 'bold')
                    .style('text-anchor', 'middle')
                }
                svg.append('rect')
                .attr('transform', 'translate('+ -this.yAxisWidth +',' + this.lineChart_height/2 + ')')
                .attr('width', this.lineChart_height/2 + 3)
                .attr('height', 8)
                .style('fill', this.keyColor.axis)
                .style('opacity', 0.8)
                svg.append('rect')
                .attr('transform', 'translate('+ -this.yAxisWidth +',' + (this.lineChart_height/2 + this.margin.bottom + 2) + ')')
                .attr('width', this.lineChart_height/2 + 3)
                .attr('height', 8)
                .style('fill', this.keyColor.axis)
                .style('opacity', 0.8)
                
                
                axios.get("/api/peer_aggregate_data/" + userID + "/"+ probID + "/X").then(response=>{
                    // x_mouse = JSON.parse(response.data.replace(/'/g, '"'))
                    x_mouse = response.data
                    this._drawHeatmap(x_mouse,g_0, keyOrder_origin, -1)            
                })
                axios.get("/api/peer_aggregate_data/" + userID + "/"+ probID + "/Y").then(response=>{
                    // y_mouse = JSON.parse(response.data.replace(/'/g, '"'))
                    y_mouse = response.data
                    this._drawHeatmap(y_mouse,g_1, keyOrder_origin, -1)              
                })
            },
            drawheatmapRChart(userID,probID, svg){
                let x_mouse, y_mouse,
                keyOrder_origin = ['bbox_min', 'headpose', 'bbox_max'],//, 'mouse'
                keyOrder = ['Bbox_lower', 'Head pose', 'Bbox_upper'],
                g_0 = svg.append('g'),
                g_1 = svg.append('g').attr('transform', 'translate(0, ' + (this.lineChart_height/2 + this.margin.top + this.margin.bottom) + ')')
                
                for(let i in keyOrder) {
                    svg.append('text')
                    .attr('transform', 'translate(' + ((this.lineChart_height/2/keyOrder.length)*i + this.lineChart_height/2/keyOrder.length/2 + this.yAxisWidth) + ','+ (this.lineChart_height/2 + (this.margin.top*2 + this.margin.bottom)/2.3) + ')')
                    .text(function(){
                        // let shortT = "", originT = keyOrder[i].split('_')
                        
                        // for(let i in originT){
                        //     if(i > 0) {
                        //         shortT = shortT + originT[i]
                        //     } else {
                        //         shortT = shortT + originT[i][0].toUpperCase()
                        //     }
                        // }
                        // return shortT
                        return keyOrder[i]
                    })
                    .style('fill', this.keyColor[keyOrder_origin[i]])
                    .style('font-size', 8)
                    .style('font-weight', 'bold')
                    .style('text-anchor', 'middle')
                }
                svg.append('rect')
                .attr('transform', 'translate('+ (this.yAxisWidth-3) +',' + this.lineChart_height/2 + ')')
                .attr('width', this.lineChart_height/2 + 3)
                .attr('height', 8)
                .style('fill', this.keyColor.axis)
                .style('opacity', 0.8)
                svg.append('rect')
                .attr('transform', 'translate('+ (this.yAxisWidth-3) +',' + (this.lineChart_height/2 + this.margin.bottom + 2) + ')')
                .attr('width', this.lineChart_height/2 + 3)
                .attr('height', 8)
                .style('fill', this.keyColor.axis)
                .style('opacity', 0.8)
                axios.get("/api/other_question_aggregate_data/" + userID + "/"+ probID + "/X").then(response=>{
                    // x_mouse = JSON.parse(response.data.replace(/'/g, '"'))
                    x_mouse = response.data
                    this._drawHeatmap(x_mouse,g_0, keyOrder_origin, 1)            
                })
                axios.get("/api/other_question_aggregate_data/" + userID + "/"+ probID + "/Y").then(response=>{
                    // y_mouse = JSON.parse(response.data.replace(/'/g, '"'))
                    y_mouse = response.data
                    this._drawHeatmap(y_mouse,g_1, keyOrder_origin, 1)              
                })
            },
            _drawHeatmap(data, svg, keyOrder, loc) {
                for(let i=0; i<keyOrder.length; i++) {
                    for(let j=0; j < data[keyOrder[i]].length; j++){
                        svg.append('rect')
                        .attr('x', this.lineChart_height/2/keyOrder.length*i + loc * this.yAxisWidth)
                        .attr('y', this.lineChart_height/2 - this.lineChart_height/2/data[keyOrder[i]].length*(j + 1))
                        .attr('width', this.lineChart_height/2/keyOrder.length)
                        .attr('height', this.lineChart_height/2/data[keyOrder[i]].length)
                        .style('fill', this.keyColor[keyOrder[i].split('_')[0]])
                        .style('opacity', data[keyOrder[i]][j])
                    }
                }
            },
            drawGlyphChart(userID,probID, svg){
                let glyphData
                axios.get("/api/student_suspicious_case/" + userID + "?question_id="+ probID + "&threshold=" + this.z_score_threshold +"&instance=1").then(response=>{
                    // glyphData = JSON.parse(response.data.replace(/'/g, '"'))
                    glyphData = response.data
                    this._appendGlyph(glyphData, svg, userID)            
                })
            },
            _appendGlyph(glyphData, svg, userID){
                svg.append('rect')
                .style('fill', this.keyColor.barbgm)
                .style('opacity', 0.2)
                .style('stroke', 'none')
                .attr('width', this.lineChart_width)
                .attr('height', this.margin.top + this.margin.bottom)
                let strokeColor = {
                    blur_focus: '#a47062', // red
                    copy_paste: '#d7a395', // lightred
                    no_face: '#084177',//'#687466', // blue
                    headpose: '#687466' // green
                }
                let x_axis = d3.scaleLinear().domain(this.timePeriod[userID])
                    .range([0, this.lineChart_width])
                for(let key in glyphData) {
                    let contFlag = 0, contResp = [], threshold = x_axis(this.timePeriod[userID][0] + 1000) - x_axis(this.timePeriod[userID][0]);
                    if(glyphData[key].length != 0) {
                        for(let i in glyphData[key]) {
                            if(glyphData[key][i].d_timestamp >= this.timePeriod[userID][0] && glyphData[key][i].d_timestamp <= this.timePeriod[userID][1]){
                                svg.append('ellipse')
                                .attr('cx', x_axis(glyphData[key][i].d_timestamp))
                                .attr('cy', (this.margin.top + this.margin.bottom)/2)
                                .attr("rx", 1)
                                .attr("ry", (this.margin.top + this.margin.bottom)/2)
                                .style('stroke-width', 1)
                                .style('stroke', strokeColor[key])
                                .style('fill', strokeColor[key])
                                .style('opacity', 0.2)

                                if(i < glyphData[key].length - 1) {
                                    if((x_axis(glyphData[key][Number(i)+Number(1)].d_timestamp) - x_axis(glyphData[key][i].d_timestamp)) < threshold && contFlag == 0) {
                                        contFlag = 1;
                                        contResp.push(x_axis(glyphData[key][i].d_timestamp))
                                    } else if((x_axis(glyphData[key][Number(i)+Number(1)].d_timestamp) - x_axis(glyphData[key][i].d_timestamp)) >= threshold && contFlag == 1) {
                                        contResp.push(x_axis(glyphData[key][i].d_timestamp))

                                        svg.append('svg:image')
                                            .attr('xlink:href', require('../../static/images/'+key+'.svg'))
                                            .attr('transform', 'translate(' + ((contResp[0] + contResp[1])/2 - (this.margin.top + this.margin.bottom)/6) + ','+ (this.margin.top + this.margin.bottom)/3 +')')
                                            .attr('width', (this.margin.top + this.margin.bottom)/3)
                                            .attr('height', (this.margin.top + this.margin.bottom)/3)
                                            .style('fill', strokeColor[key])

                                        contResp = []
                                        contFlag = 0
                                    }else if((x_axis(glyphData[key][Number(i)+Number(1)].d_timestamp) - x_axis(glyphData[key][i].d_timestamp)) >= threshold && contFlag == 0) {
                                        svg.append('svg:image')
                                            .attr('xlink:href', require('../../static/images/'+key+'.svg'))
                                            .attr('transform', 'translate(' + (x_axis(glyphData[key][i].d_timestamp) - (this.margin.top + this.margin.bottom)/6) + ','+ (this.margin.top + this.margin.bottom)/3 +')')
                                            .attr('width', (this.margin.top + this.margin.bottom)/3)
                                            .attr('height', (this.margin.top + this.margin.bottom)/3)
                                            .style('fill', strokeColor[key])
                                    }
                                } else {
                                    if(contFlag) {
                                        contResp.push(x_axis(glyphData[key][i].d_timestamp))

                                        svg.append('svg:image')
                                            .attr('xlink:href', require('../../static/images/'+key+'.svg'))
                                            .attr('transform', 'translate(' + ((contResp[0] + contResp[1])/2 - (this.margin.top + this.margin.bottom)/6) + ','+ (this.margin.top + this.margin.bottom)/3 +')')
                                            .attr('width', (this.margin.top + this.margin.bottom)/3)
                                            .attr('height', (this.margin.top + this.margin.bottom)/3)
                                            .style('fill', strokeColor[key])

                                        contResp = []
                                        contFlag = 0
                                    } else {
                                        svg.append('svg:image')
                                            .attr('xlink:href', require('../../static/images/'+key+'.svg'))
                                            .attr('transform', 'translate(' + (x_axis(glyphData[key][i].d_timestamp) - (this.margin.top + this.margin.bottom)/6) + ','+ (this.margin.top + this.margin.bottom)/3 +')')
                                            .attr('width', (this.margin.top + this.margin.bottom)/3)
                                            .attr('height', (this.margin.top + this.margin.bottom)/3)
                                            .style('fill', strokeColor[key])

                                        contResp = []
                                        contFlag = 0
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    };
</script>

<style scoped>
</style>