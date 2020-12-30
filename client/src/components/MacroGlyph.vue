<template>
    <b-card no-body>
        <b-card-header class='small-header' style="font-size:18px; padding:2px 20px 0px">
            <!-- {{(student_id[0].charCodeAt(0)+20).toString()+(student_id[1].charCodeAt(0)+20).toString()}} -->
            {{student_id.slice(0,6)}}
            <b-button v-if="!selected" size="sm" variant='outline' style="float: right; padding: 0" @click="onClick">
                <b-icon-plus-square />
            </b-button>
            <b-button v-if="selected" size="sm" variant='outline' style="float: right; padding: 0" @click="onClick">
                <b-icon-dash-square />
            </b-button>
        </b-card-header>
        <b-card-body :id="'mg_'+student_id" style="padding: 5px"/>
    </b-card>
</template>

<script>
    import * as axios from 'axios'
    import * as d3 from 'd3'
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap-vue/dist/bootstrap-vue.css';
    import { BCard, BCardBody, BCardHeader, BIconPlusSquare, BIconDashSquare, BButton } from 'bootstrap-vue'
    //eslint-disable-next-line
    import { RadarChart } from '../assets/RadarChart'


    export default {
        name: 'MacroGlyph',
        props: ["student_id", "z_score_threshold", "selected_exam", "overall_cheating_stat", "overall_average_time", "headpose_weight", "copy_paste_weight", "blur_focus_weight", "no_face_weight", "question_cheating_stat", "score", "display_id"],
        components: {
            BCard,
            BCardBody,
            BCardHeader,
            BIconPlusSquare, 
            BIconDashSquare, 
            BButton
        },
        data() {
            return {
                cheating_instance: null,
                total_data:{
                    blur_focus: null,
                    copy_paste: null,
                    no_face: null,
                    headpose: null,
                },
                alias:{
                    'copy_paste': "c",
                    'blur_focus': "b",
                    'no_face': 'f',
                    'headpose': 'h'
                },
                svg:{
                    height: parseInt((document.getElementsByClassName('macro_card_body')[0].offsetWidth-30)/2),
                    width_glyph: parseInt((document.getElementsByClassName('macro_card_body')[0].offsetWidth-30)/2),
                    width_time: parseInt((document.getElementsByClassName('macro_card_body')[0].offsetWidth-30)/4),
                    width_risk: parseInt((document.getElementsByClassName('macro_card_body')[0].offsetWidth-30)/4)
                },
                radar: {
                    height: parseInt((document.getElementsByClassName('macro_card_body')[0].offsetWidth-30)/2-30),
                    width: parseInt((document.getElementsByClassName('macro_card_body')[0].offsetWidth-30)/2-30)
                },
                student_time_length: null,
                selected: false
            };
        },
        mounted() {
            axios.get(`/api/student_suspicious_case/${this.student_id}?threshold=${this.z_score_threshold}&instance=0`).then(response=>{
                this.cheating_instance = Object.values(response.data)
                
            }).then(()=>{
                Object.keys(this.total_data).map(d=>{
                    this.total_data[d] = this.scale(this.cheating_instance.reduce((p, c)=>p+c[d], 0), d)
                })

                this.overall_cheating_stat['average_time_length'] = {
                    min: this.overall_average_time.filter(d=>d.question_id=='min')[0]['average_time_length'],
                    max: this.overall_average_time.filter(d=>d.question_id=='max')[0]['average_time_length'],
                }
            }).then(()=>{
                 axios.get(`/api/question_time_length/${this.student_id}`).then(response=>{
                    this.student_time_length = response.data.data
                }).then(()=>{
                    this.draw()
                })
                
            })
            this.$watch('z_score_threshold', (n, o)=>{
                if (n!=o){
                    axios.get(`/api/student_suspicious_case/${this.student_id}?threshold=${this.z_score_threshold}&instance=0`).then(response=>{
                        this.cheating_instance = Object.values(response.data)
                    }).then(()=>{
                        Object.keys(this.total_data).map(d=>{
                            this.total_data[d] = this.scale(this.cheating_instance.reduce((p, c)=>p+c[d], 0), d)
                        })
                        // d3.select(`#svg_mg_${this.student_id}_r`).remove()
                        d3.select(`#svg_mg_${this.student_id}_tr`).remove()
                        d3.select(`#svg_mg_${this.student_id}_g`).remove()
                        this.overall_cheating_stat['average_time_length'] = {
                            min: this.overall_average_time.filter(d=>d.question_id=='min')[0]['average_time_length'],
                            max: this.overall_average_time.filter(d=>d.question_id=='max')[0]['average_time_length'],
                        }
                    }).then(()=>{
                       this.draw()
                    })
                }
            })
            this.$watch('headpose_weight', (n,o)=>{
                d3.select(`#svg_mg_${this.student_id}_tr`).remove()
                if (n!=o){
                    this.draw_time_risk()
                    this.$root.$emit('changeWeight', {
                        'headpose_weight': n,
                        'copy_paste_weight': this.copy_paste_weight,
                        'blur_focus_weight': this.blur_focus_weight,
                        'no_face_weight': this.no_face_weight
                    })
                }
            })
            this.$watch('copy_paste_weight', (n,o)=>{
                d3.select(`#svg_mg_${this.student_id}_tr`).remove()
                if (n!=o){
                    this.draw_time_risk()
                    this.$root.$emit('changeWeight', {
                        'headpose_weight': this.headpose_weight,
                        'copy_paste_weight': n,
                        'blur_focus_weight': this.blur_focus_weight,
                        'no_face_weight': this.no_face_weight
                    })
                }
            })
            this.$watch('blur_focus_weight', (n,o)=>{
                d3.select(`#svg_mg_${this.student_id}_tr`).remove()
                if (n!=o){
                    this.draw_time_risk()
                    this.$root.$emit('changeWeight', {
                        'headpose_weight': this.headpose_weight,
                        'copy_paste_weight': this.copy_paste_weight,
                        'blur_focus_weight': n,
                        'no_face_weight': this.no_face_weight
                    })
                }
            })
            this.$watch('no_face_weight', (n,o)=>{
                d3.select(`#svg_mg_${this.student_id}_tr`).remove()
                if (n!=o){
                    this.draw_time_risk()
                    this.$root.$emit('changeWeight', {
                        'headpose_weight': this.headpose_weight,
                        'copy_paste_weight': this.copy_paste_weight,
                        'blur_focus_weight': this.blur_focus_weight,
                        'no_face_weight': n
                    })
                }
            })
        },
        methods: {
            scale(value, key){
                if ((value-this.overall_cheating_stat[key]['min'])/(this.overall_cheating_stat[key]['max']-this.overall_cheating_stat[key]['min'])<0){
                    console.log(value, key, this.student_id)
                    return 0
                }
                else{
                return (value-this.overall_cheating_stat[key]['min'])/(this.overall_cheating_stat[key]['max']-this.overall_cheating_stat[key]['min'])}
            },
            scale_question(value, question_id, key){
                return this.question_cheating_stat[question_id][key]['max']-this.question_cheating_stat[question_id][key]['min']==0?0:(value-this.question_cheating_stat[question_id][key]['min'])/(this.question_cheating_stat[question_id][key]['max']-this.question_cheating_stat[question_id][key]['min'])
            },
            onClick(){
                this.selected = !this.selected
                this.$root.$emit("changeStudentSelection", this.student_id)
            },
            draw(){
                this.draw_glyph(),
                // this.draw_time(),
                // this.draw_risk()
                this.draw_time_risk()
            },
            draw_glyph(){
                d3.select(`#mg_${this.student_id}`)
                            .append("svg")
                            .attr("width", this.svg.width_glyph)
                            .attr("height", this.svg.height)
                            .attr("position", "absolute")
                            .attr("left", "0px")
                            .attr('id',`svg_mg_${this.student_id}_g`)
                var radarChartOptions = {
                    w: this.radar.width,//Width of the circle
                    h: this.radar.height,
                    x: this.svg.height/2,
                    y: this.svg.height/2,
                    levels: 1,
                    maxValue: 1,
                    roundStrokes: false,
                    dotRadius: 2,
                    strokeWidth: 1,
                    opacityArea: 0.25,
                    labelFactor: 0.8,
                    fontsize: '16px',
                    color: d3.scaleOrdinal().range(['rgb(80, 80, 80)', "rgb(59, 119, 176)"]),
                };
                let data = {
                        name: "Cheating",
                        axes: Object.keys(this.total_data).map(d=>{
                            return {
                                axis: d,
                                alias: this.alias[d],
                                value: this.total_data[d],
                                quantile_25: this.scale(this.overall_cheating_stat[d]["quantile_25"], d),
                                quantile_75: this.scale(this.overall_cheating_stat[d]["quantile_75"], d),
                                mean: this.scale(this.overall_cheating_stat[d]["mean"], d),
                                median: this.scale(this.overall_cheating_stat[d]["median"], d),
                            }
                        }),
                        color: 'rgb(255, 127, 14)'
                    }

                this.$emit('risk', this.student_id, (this.headpose_weight * this.total_data['headpose'] + this.blur_focus_weight * this.total_data['blur_focus'] + this.copy_paste_weight * this.total_data['copy_paste'] + this.no_face_weight * this.total_data['no_face']) / (this.headpose_weight + this.blur_focus_weight + this.copy_paste_weight + this.no_face_weight))

                let mean = {
                        name: "Mean",
                        axes: Object.keys(this.total_data).map(d=>{
                            return {
                                axis: d,
                                alias: this.alias[d],
                                value: this.scale(this.overall_cheating_stat[d]["mean"], d),
                                quantile_25: 0,
                                quantile_75: 0,
                                mean: 0,
                                median: 0,
                            }
                        }),
                        color: 'rgb(255, 127, 14)'
                    }

                // console.log(JSON.stringify(mean))
                //eslint-disable-next-line
                var glyph = RadarChart(`#svg_mg_${this.student_id}_g`, [mean, data], radarChartOptions, this, this.student_id)

                var arc = d3.arc()

                d3.select(`#svg_mg_${this.student_id}_g`).append('path')
                    .attr('transform', 'translate('+[this.svg.height/2, this.svg.height/2]+')')
                    .attr('d', ()=>arc({
                            innerRadius: this.radar.width/2,
                            outerRadius: this.radar.width/2+5,
                            startAngle: 0,
                            endAngle: Math.PI*2*this.student_time_length.reduce((p, c)=>p+c['time_length'], 0)/(25*60)
                        }))
                    .style('fill', '#8dd3c7')
                    .style('opacity', 0.8)
                    // .style('stroke', 'pink')
                    // .style('stroke-width', 1)
                
                d3.select(`#svg_mg_${this.student_id}_g`).append('path')
                    .attr('transform', 'translate('+[this.svg.height/2, this.svg.height/2]+')')
                    .attr('d', ()=>arc({
                            innerRadius: this.radar.width/2+6,
                            outerRadius: this.radar.width/2+11,
                            startAngle: 0,
                            endAngle: Math.PI*2*this.score/14
                        }))
                    .style('fill', '#fdb462')
                    .style('opacity', 0.8)
                    // .style('stroke', 'pink')
                    // .style('stroke-width', 1)

            },
            draw_time(){
                let svg = d3.select(`#mg_${this.student_id}`)
                            .append("svg")
                            .attr("width", this.svg.width_time)
                            .attr("height", this.svg.height)
                            .attr("position", "absolute")
                            .attr("left", `${this.svg.width_glyph}px`)
                            .attr('id',`svg_mg_${this.student_id}_t`)
                
                var y_scale = d3.scaleBand()
                        .range([0, this.svg.height])
                        .domain(['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4'])
                        .padding(0)

                let g_time = svg.append("g")
                    .attr("transform", `translate(${this.svg.width_time/2}, 0)`)

                g_time.append("g").selectAll('g')
                    .data(this.overall_average_time.filter(d=>d['question_id']!='min'&&d['question_id']!='max' ))
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>(this.scale(d['average_time_length'], 'average_time_length')*30))
                        .attr('fill', '#8dd3c7')
                        .style('opacity', 0.8)
        
                g_time.append("g").selectAll('g')
                    .data(this.student_time_length)
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>(this.scale(d['time_length'], 'average_time_length')*30))
                        .attr('fill', '#8dd3c7')
                        .style('opacity', 0.8)
                        .attr('transform', d=>`translate(${-(this.scale(d['time_length'], 'average_time_length')*30)},0)`)

                g_time.call(d3.axisLeft(y_scale).tickSize(0))

                g_time.selectAll(".domain")
                    .attr('stroke', 'rgb(120, 120, 120)')
                g_time.selectAll('text')
                    .attr('font-family', "Avenir, Helvetica, Arial, sans-serif")
                    .attr('font-color', 'rgb(120, 120, 120)')
            },
            draw_risk(){
                let svg = d3.select(`#mg_${this.student_id}`)
                            .append("svg")
                            .attr("width", this.svg.width_risk)
                            .attr("height", this.svg.height)
                            .attr("position", "absolute")
                            .attr("left", `${this.svg.width_glyph+this.svg.width_time}px`)
                            .attr('id',`svg_mg_${this.student_id}_r`)
                
                var y_scale = d3.scaleBand()
                        .range([0, this.svg.height])
                        .domain(['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4'])
                        .padding(0)

                let g_risk = svg.append("g")
                    .attr("transform", `translate(${this.svg.width_risk/2}, 0)`)

                let data = this.cheating_instance.map(d=>{
                    let risk = (this.headpose_weight * this.scale_question(d['headpose'], d['question_id'],'headpose') + this.blur_focus_weight * this.scale_question(d['blur_focus'], d['question_id'], 'blur_focus') + this.copy_paste_weight * this.scale_question(d['copy_paste'], d['question_id'], 'copy_paste') + this.no_face_weight * this.scale_question(d["no_face"], d['question_id'], "no_face")) / (this.headpose_weight + this.blur_focus_weight + this.copy_paste_weight + this.no_face_weight)
                    
                    return {
                        question_id: d['question_id'],
                        risk: risk
                    }
                })

                let mean_data = Object.entries(this.question_cheating_stat).map(d=>{
                    // console.log(d)

                    let risk = (this.headpose_weight * this.scale_question(d[1]['headpose']['mean'], d[0],'headpose') + this.blur_focus_weight * this.scale_question(d[1]['blur_focus']['mean'], d[0], 'blur_focus') + this.copy_paste_weight * this.scale_question(d[1]['copy_paste']['mean'], d[0], 'copy_paste') + this.no_face_weight * this.scale_question(d[1]["no_face"]['mean'], d[0], "no_face")) / (this.headpose_weight + this.blur_focus_weight + this.copy_paste_weight + this.no_face_weight)
                    return {
                        question_id: d[0],
                        risk: risk
                    }
                })

                g_risk.append("g").selectAll('g')
                    .data(mean_data)
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>d.risk*30)
                        .attr('fill', '#fbb4ae')
        
                g_risk.append("g").selectAll('g')
                    .data(data)
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>{
                            // console.log(d)
                            return d.risk*30
                        })
                        .attr('fill', '#fbb4ae')
                        .attr('transform', d=>`translate(${-d.risk*30},0)`)

                g_risk.call(d3.axisLeft(y_scale).tickSize(0))

                g_risk.selectAll(".domain")
                    .attr('stroke', 'rgb(120, 120, 120)')
                g_risk.selectAll('text')
                    .attr('font-family', "Avenir, Helvetica, Arial, sans-serif")
                    .attr('font-color', 'rgb(120, 120, 120)')
            },
            draw_time_risk(){
                let svg = d3.select(`#mg_${this.student_id}`)
                            .append("svg")
                            .attr("width", this.svg.width_time+this.svg.width_risk)
                            .attr("height", this.svg.height)
                            .attr("position", "absolute")
                            .attr("left", `${this.svg.width_glyph}px`)
                            .attr('id',`svg_mg_${this.student_id}_tr`)
                
                var y_scale = d3.scaleBand()
                        .range([0, this.svg.height])
                        .domain(['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4'])
                        .padding(0)

                let g_time = svg.append("g")
                    .attr("transform", `translate(${this.svg.width_time/2}, 0)`)

                g_time.append("g").selectAll('g')
                    .data(this.overall_average_time.filter(d=>d['question_id']!='min'&&d['question_id']!='max' ))
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>(this.scale(d['average_time_length'], 'average_time_length')*30))
                        .attr('fill', '#8dd3c7')
                        .style('opacity', 0.8)
        
                g_time.append("g").selectAll('g')
                    .data(this.student_time_length)
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>(this.scale(d['time_length'], 'average_time_length')*30))
                        .attr('fill', '#8dd3c7')
                        .style('opacity', 0.8)
                        .attr('transform', d=>`translate(${-(this.scale(d['time_length'], 'average_time_length')*30)},0)`)

                g_time.call(d3.axisLeft(y_scale).tickSize(0).tickFormat(""))

                g_time.selectAll(".domain")
                    .attr('stroke', 'rgb(120, 120, 120)')
                

                
                // var y_scale = d3.scaleBand()
                //         .range([0, this.svg.height])
                //         .domain(['mc_1', 'mc_2', 'mc_3', 'mc_4', 'mc_5', 'mc_6', 'mc_7', 'mc_8', 'mc_9', 'mc_10', 'sa_1', 'sa_2','sa_3', 'sa_4'])
                //         .padding(0)

                let g_risk = svg.append("g")
                    .attr("transform", `translate(${this.svg.width_risk/2+this.svg.width_time}, 0)`)

                let data = this.cheating_instance.map(d=>{
                    let risk = (this.headpose_weight * this.scale_question(d['headpose'], d['question_id'],'headpose') + this.blur_focus_weight * this.scale_question(d['blur_focus'], d['question_id'], 'blur_focus') + this.copy_paste_weight * this.scale_question(d['copy_paste'], d['question_id'], 'copy_paste') + this.no_face_weight * this.scale_question(d["no_face"], d['question_id'], "no_face")) / (this.headpose_weight + this.blur_focus_weight + this.copy_paste_weight + this.no_face_weight)
                    
                    return {
                        question_id: d['question_id'],
                        risk: risk
                    }
                })

                let mean_data = Object.entries(this.question_cheating_stat).map(d=>{
                    // console.log(d)

                    let risk = (this.headpose_weight * this.scale_question(d[1]['headpose']['mean'], d[0],'headpose') + this.blur_focus_weight * this.scale_question(d[1]['blur_focus']['mean'], d[0], 'blur_focus') + this.copy_paste_weight * this.scale_question(d[1]['copy_paste']['mean'], d[0], 'copy_paste') + this.no_face_weight * this.scale_question(d[1]["no_face"]['mean'], d[0], "no_face")) / (this.headpose_weight + this.blur_focus_weight + this.copy_paste_weight + this.no_face_weight)
                    return {
                        question_id: d[0],
                        risk: risk
                    }
                })

                g_risk.append("g").selectAll('g')
                    .data(mean_data)
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>d.risk*30)
                        .attr('fill', '#fbb4ae')
        
                g_risk.append("g").selectAll('g')
                    .data(data)
                    .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d=>y_scale(d['question_id']))
                        .attr('height', this.svg.height/14)
                        .attr('width', d=>{
                            // console.log(d)
                            return d.risk*30
                        })
                        .attr('fill', '#fbb4ae')
                        .attr('transform', d=>`translate(${-d.risk*30},0)`)

                g_risk.call(d3.axisLeft(y_scale).tickSize(0))

                g_risk.selectAll(".domain")
                    .attr('stroke', 'rgb(120, 120, 120)')
                g_risk.selectAll('text')
                    .attr('font-family', "Avenir, Helvetica, Arial, sans-serif")
                    .attr('font-color', 'rgb(120, 120, 120)')

                d3.selectAll(".tick text")
                    .attr('transform', `translate(-${this.svg.width_time/2*0.9}, 0)`)
                    .attr("text-anchor", "middle")
                    .attr("font-size", 12)


                g_time.append("text")
                    .text("Time Length")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("text-anchor", "middle")
                    .attr("transform", `translate(-${this.svg.width_time/2-10}, ${this.svg.height/2}) rotate(270)`)
                    .attr("fill", "black")
                    .attr('font-family', "Avenir, Helvetica, Arial, sans-serif")
                    .attr('font-size', 14)

                g_risk.append("text")
                    .text("Overall Risk")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("text-anchor", "middle")
                    .attr("transform", `translate(${this.svg.width_time/2-10}, ${this.svg.height/2}) rotate(90)`)
                    .attr("fill", "black")
                    .attr('font-family', "Avenir, Helvetica, Arial, sans-serif")
                    .attr('font-size', 14)
            }

        },
        
    };
</script>

<style scoped>

</style>