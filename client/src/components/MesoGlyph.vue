<template>
    <div :id="'eg_'+student_id+'_'+question_id" :style="'width:'+(svg.width + 5)+'px; float: left;'">
    </div>
</template>

<script>
    //eslint-disable-next-line
    import * as axios from 'axios'
    //eslint-disable-next-line
    import * as d3 from 'd3'
    // import 'bootstrap/dist/css/bootstrap.css';
    // import 'bootstrap-vue/dist/bootstrap-vue.css';
    // import VueSlider from 'vue-slider-component'
    // import 'vue-slider-component/theme/default.css'

    // import { BCard, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup } from 'bootstrap-vue'

    export default {
        name: 'MesoGlyph',
        props:["student_id", "cheating_instance", "overall_cheating_stat", "result", "z_score_threshold", "weights", "show_risk_in_length"],
        components: {
        },
        data() {
            return {
                question_id: this.cheating_instance['question_id'],
                svg:{
                    width: parseInt((document.getElementsByClassName("meso_card_body")[0].offsetWidth-80)/14 - 5),
                    height: 80
                },
                alias:{
                    'copy_paste': "cp",
                    'blur_focus': "bf",
                    'no_face': 'nf',
                    'headpose': 'hp'
                },
                selected: false
            };
        },
        mounted() {
            this.draw()

            this.$watch("z_score_threshold", (n, o)=>{
                if (n!=o){
                    this.svg.width = parseInt((document.getElementsByClassName("meso_card_body")[0].offsetWidth-80)/14 - 5)
                    this.draw()
                }
            })

            this.$watch("weights", (n, o)=>{
                if (n!=o){
                    this.svg.width = parseInt((document.getElementsByClassName("meso_card_body")[0].offsetWidth-80)/14 - 5)
                    this.draw()
                }
            })

            this.$watch("show_risk_in_length", (n, o)=>{
                if (n!=o){
                    this.svg.width = parseInt((document.getElementsByClassName("meso_card_body")[0].offsetWidth-80)/14 - 5)
                    this.draw()
                }
            })

            this.$root.$on('selectMeso', (s,q)=>{
                if (s==this.student_id&&q!=this.question_id){
                    d3.select(`#svg_eg_${this.student_id}_${this.question_id}`).select("#background_rect").attr('stroke', this.result?'#b3de69':'#b9b9b9').style('stroke-dasharray', this.result?"":"5, 3").attr("stroke-width", "2")
                }
            })

            this.$root.$on('closeMicro', (s)=>{
                if (s==this.student_id){
                    d3.select(`#svg_eg_${this.student_id}_${this.question_id}`).select("#background_rect").attr('stroke', this.result?'#b3de69':'#b9b9b9').style('stroke-dasharray', this.result?"":"5, 3").attr("stroke-width", "2")
                }
            })

            //eslint-disable-next-line
            this.$watch("selected", (n,o)=>{
                if (n){
                    this.$root.$emit('selectMeso', this.student_id, this.question_id)
                    d3.select(`#svg_eg_${this.student_id}_${this.question_id}`).select("#background_rect").attr('stroke', 'gold').attr("stroke-width", "5").style('stroke-dasharray', "")
                }
                else{
                    d3.select(`#svg_eg_${this.student_id}_${this.question_id}`).select("#background_rect").attr('stroke', this.result?'#b3de69':'#b9b9b9').style('stroke-dasharray', this.result?"":"5, 3").attr("stroke-width", "2")
                }
            })
        },
        methods: {
            scale(value, key){
                return (this.overall_cheating_stat[key]['max']-this.overall_cheating_stat[key]['min'])==0?0:(value-this.overall_cheating_stat[key]['min'])/(this.overall_cheating_stat[key]['max']-this.overall_cheating_stat[key]['min'])
            },
            get_risk(){

                return (this.weights.headpose_weight*this.scale(this.cheating_instance['headpose'], 'headpose') + this.weights.blur_focus_weight*this.scale(this.cheating_instance['blur_focus'], 'blur_focus') + 
                this.weights.copy_paste_weight*this.scale(this.cheating_instance['copy_paste'], 'copy_paste') + 
                this.weights.no_face_weight*this.scale(this.cheating_instance['no_face'], 'no_face')) / (this.weights.headpose_weight + this.weights.blur_focus_weight + this.weights.copy_paste_weight + this.weights.no_face_weight)
            },
            draw(){
                d3.select(`#svg_eg_${this.student_id}_${this.question_id}`).remove()
                this.svg.width = this.show_risk_in_length?this.svg.width*this.get_risk()+40:this.svg.width
                //eslint-disable-next-line
                let svg = d3.select(`#eg_${this.student_id}_${this.question_id}`)
                            .append("svg")
                            .attr("width", this.svg.width)
                            .attr("height", this.svg.height)
                            .attr("position", "absolute")
                            .attr("left", "0px")
                            .attr('id',`svg_eg_${this.student_id}_${this.question_id}`)
                            .attr('class', 'meso_glyph')

                let x_scale = d3.scaleBand()
                                .range([12, this.svg.width-12])
                                .domain(Object.keys(this.cheating_instance).filter(d=>d!="question_id"))
                                // .padding(0.05)

                let y_scale = d3.scaleLinear()
                                .range([18, this.svg.height-6])
                                .domain([1, 0])

                let data = Object.entries(this.cheating_instance).filter(d=>d[0]!="question_id").map(d=>{
                    return {
                        type: d[0],
                        value: this.scale(d[1], d[0])
                    }
                })

                let stat = Object.entries(this.overall_cheating_stat).map(d=>{
                    let value = {}

                    for (var k in d[1]){
                        value[k] = this.scale(d[1][k], d[0])
                    }

                    return {
                        type: d[0],
                        value: value
                    }
                })
                // console.log(stat)

                svg.append('rect')
                    .attr("width", this.svg.width-4)
                    .attr("height", this.svg.height-4)
                    .attr('fill', 'white')
                    .attr("rx", 6)
                    .attr("ry", 6)
                    .attr('stroke', this.result?'#b3de69':'#b9b9b9')
                    .style('stroke-dasharray', this.result?"":"5, 3")
                    .attr("stroke-width", "2")
                    .on('click', ()=>{
                        this.$emit('expandMicroView', this.question_id)
                        this.$root.$emit('chooseProblem', [this.question_id, this.student_id])
                        // console.log(this.question_id)
                        
                        this.selected = !this.selected
                    })
                    .attr('transform', 'translate(2, 2)')
                    .attr('id', 'background_rect')
                
                // var line_generator_curve = d3.line().curve(d3.curveBasis)
                // var line_generator_linear = d3.line().curve(d3.curveLinear)

                // svg.append('path')
                //     .attr('d', line_generator_linear([[2, 0], [this.svg.width-10, 0]]) + line_generator_curve([[this.svg.width-10, 0], [this.svg.width, this.svg.height/2], [this.svg.width-10, this.svg.height]]) + line_generator_linear([[this.svg.width-10, this.svg.height], [2, this.svg.height]]) + line_generator_curve([[2, this.svg.height], [12, this.svg.height/2], [2, 0]]))
                //     .attr('fill', 'none')
                //     .attr('stroke', this.result?'#33a02c':'#e31a1c')
                //     .attr('stroke-width', 2)

                // svg.append('path')
                //     .attr('d', line_generator_curve([[2, this.svg.height], [12, this.svg.height/2], [2, 0]]))
                //     .attr('fill', 'none')
                //     .attr('stroke', this.result?'#33a02c':'#e31a1c')
                //     .attr('stroke-width', 2)

                // svg.append('path')
                //     .attr('d', line_generator_linear([[2, 0], [this.svg.width-10, 0]]))
                //     .attr('fill', 'none')
                //     .attr('stroke', this.result?'#33a02c':'#e31a1c')
                //     .attr('stroke-width', 4)

                // svg.append('path')
                //     .attr('d', line_generator_linear([[this.svg.width-10, this.svg.height], [2, this.svg.height]]))
                //     .attr('fill', 'none')
                //     .attr('stroke', this.result?'#33a02c':'#e31a1c')
                //     .attr('stroke-width', 4)


                // svg.append('g').call(d3.axisBottom(x_scale).tickFormat(d => this.alias[d]).tickSize(0).tickSizeOuter(0))
                //     .attr("transform", `translate(0, ${this.svg.height-18})`)

                // svg.selectAll(".domain")
                //     .attr('stroke', 'rgb(120, 120, 120)')
                //     // .remove()
                // svg.selectAll('text')
                //     .attr('font-family', "Avenir, Helvetica, Arial, sans-serif")
                    // .attr('transform', 'translate(0, -2)')
                    // .remove()
                        
                // console.log(data)
                svg.append('g').selectAll('g')
                    .data(data)
                    .enter()
                        .append('rect')
                        .attr('x', d=>x_scale(d['type'])+1)
                        .attr('y', 0)
                        .attr('width', ()=>(this.svg.width-36)/4)
                        .attr('height', this.svg.height-24)
                        .attr('transform', `translate(4,18)`)
                        .attr('fill', 'rgb(200, 200, 200)')
                        .attr('opacity', 0.4)
                        .on('click', ()=>{
                            this.$emit('expandMicroView', this.question_id)
                            this.$root.$emit('chooseProblem', [this.question_id, this.student_id])
                            console.log(this.question_id)
                            // svg.select("#background_rect").attr('stroke', 'gold')
                            this.selected = !this.selected
                        })

                svg.append('g').selectAll('g')
                    .data(data)
                    .enter()
                        .append('rect')
                        .attr('x', d=>x_scale(d['type'])+1)
                        .attr('y', 0)
                        .attr('width', ()=>(this.svg.width-36)/4)
                        .attr('height',d=>(this.svg.height-24)*d['value'])
                        .attr('transform', d=>`translate(4,${(this.svg.height-24)*(1-d['value'])+18})`)
                        .attr('fill', '#fbb4ae')
                        .on('click', ()=>{
                            this.$emit('expandMicroView', this.question_id)
                            this.$root.$emit('chooseProblem', [this.question_id, this.student_id])
                            console.log(this.question_id)
                            // svg.select("#background_rect").attr('stroke', 'gold')
                            this.selected = !this.selected
                        })

                    svg.selectAll('text')
                    .data(Object.keys(this.cheating_instance).filter(d=>d!="question_id"))
                    .enter()
                        .append('text')
                        .text(d=>{
                            if (d=='no_face'){return "f"}
                            else {return d[0]}
                        })
                        .attr("x", d=>{
                            // console.log(d)
                            return this.svg.width >= 50?x_scale(d)+(this.svg.width-32)/8-2:x_scale(d)+(this.svg.width-32)/8})
                        .attr("y", 16)
                        // .attr("font-family", "sans-serif")  
                        .attr("font-size", this.svg.width >= 50?"16px":"10px")
                        .attr("fill", "rgb(160, 160, 160)")
                        .attr("transform", "translate(3,0)");

                // vertical line
                svg.append('g').selectAll('g')
                    .data(stat)
                    .enter()
                        .append('line')
                        .attr('x1', d=>x_scale(d['type'])+(this.svg.width-24)/8)
                        .attr('x2', d=>x_scale(d['type'])+(this.svg.width-24)/8)
                        .attr('y1', d=>y_scale(d['value']['quantile_25']))
                        .attr('y2', d=>y_scale(d['value']['quantile_75']))
                        .attr('stroke-width', 1)
                        .attr('stroke', 'rgb(100, 100, 100)')
                        .attr("transform", "translate(4,0)");

                // quantile_25 line
                svg.append('g').selectAll('g')
                    .data(stat)
                    .enter()
                        .append('line')
                        .attr('x1', d=>x_scale(d['type'])+(this.svg.width-24)/8-2)
                        .attr('x2', d=>x_scale(d['type'])+(this.svg.width-24)/8+2)
                        .attr('y1', d=>y_scale(d['value']['quantile_25']))
                        .attr('y2', d=>y_scale(d['value']['quantile_25']))
                        .attr('stroke-width', 1)
                        .attr('stroke', 'rgb(100, 100, 100)')
                        .attr("transform", "translate(4,0)");
                
                // quantile_75 line
                svg.append('g').selectAll('g')
                    .data(stat)
                    .enter()
                        .append('line')
                        .attr('x1', d=>x_scale(d['type'])+(this.svg.width-24)/8-2)
                        .attr('x2', d=>x_scale(d['type'])+(this.svg.width-24)/8+2)
                        .attr('y1', d=>y_scale(d['value']['quantile_75']))
                        .attr('y2', d=>y_scale(d['value']['quantile_75']))
                        .attr('stroke-width', 1)
                        .attr('stroke', 'rgb(100, 100, 100)')
                        .attr("transform", "translate(4,0)");

                // median line
                svg.append('g').selectAll('g')
                    .data(stat)
                    .enter()
                        .append('line')
                        .attr('x1', d=>x_scale(d['type'])+(this.svg.width-24)/8-2)
                        .attr('x2', d=>x_scale(d['type'])+(this.svg.width-24)/8+2)
                        .attr('y1', d=>y_scale(d['value']['median']))
                        .attr('y2', d=>y_scale(d['value']['median']))
                        .attr('stroke-width', 1)
                        .attr('stroke', 'rgb(100, 100, 100)')
                        .attr("transform", "translate(4,0)");

                // mean ball
                svg.append('g').selectAll('g')
                    .data(stat)
                    .enter()
                        .append('circle')
                        .attr('cx', d=>x_scale(d['type'])+(this.svg.width-24)/8)
                        .attr('cy', d=>y_scale(d['value']['mean']))
                        .attr('r', 2)
                        .attr('stroke-width', 0.5)
                        .attr('stroke', 'rgb(100, 100, 100)')
                        .attr('fill', 'none')
                        .attr("transform", "translate(4,0)");

                svg.append('text')
                    .text(this.question_id)
                    .attr('transform', `translate(12, ${this.svg.height/2}) rotate(270)`)
                    .attr('text-anchor', 'middle')
                    .attr("font-size", '13px')
                    .attr("fill", "rgb(80, 80, 80)")
                    // .attr("transform", "translate(3,0)");
                
                
            }
        },
    };
</script>

<style scoped>

</style>