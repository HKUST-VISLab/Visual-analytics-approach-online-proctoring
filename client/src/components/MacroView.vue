<template>
    <div>
        <b-card no-body style="">
            <b-card-header class="large-header" style="height:140px; padding: 5px 20px 0px 20px">
                <span style="font-size: 18px">Student List View</span>
                <div id="legend" style="position:absolute; top:0px; left: 136px"/>
                <b-dropdown size="sm" variant="outline-secondary" toggle-class="text-decoration-none" style="float: right;position: absolute;left: 20px;top: 80px;width: 80px;">
                    <template v-slot:button-content>
                        <b-icon-gear variant='secondary' size='sm'/>
                    </template>
                    <div style="width:250px; margin:5px 5px 5px 5px">
                        Head Pose Z-score Threshold 
                        <vue-slider
                            v-model="z_score_threshold_local"
                            :min="1"
                            :max="4"
                            :interval="0.5"
                            :marks="true"
                            style="margin-left:10px; margin-right:10px; margin-bottom:30px" 
                        ></vue-slider>
                    </div>
                    <div style="width:250px; margin:5px 5px 5px 5px">
                        Weight of Copy/Paste
                        <vue-slider
                            v-model="copy_paste_weight"
                            :min="0"
                            :max="1"
                            :interval="0.1"
                            :marks="true"
                            style="margin-left:10px; margin-right:10px; margin-bottom:30px" 
                        ></vue-slider>
                    </div>
                    <div style="width:250px; margin:5px 5px 5px 5px">
                        Weight of Headpose
                        <vue-slider
                            v-model="headpose_weight"
                            :min="0"
                            :max="1"
                            :interval="0.1"
                            :marks="true"
                            style="margin-left:10px; margin-right:10px; margin-bottom:30px" 
                        ></vue-slider>
                    </div>
                    <div style="width:250px; margin:5px 5px 5px 5px">
                        Weight of Focus/Blur
                        <vue-slider
                            v-model="blur_focus_weight"
                            :min="0"
                            :max="1"
                            :interval="0.1"
                            :marks="true"
                            style="margin-left:10px; margin-right:10px; margin-bottom:30px" 
                        ></vue-slider>
                    </div>
                    <div style="width:250px; margin:5px 5px 5px 5px">
                        Weight of no face
                        <vue-slider
                            v-model="no_face_weight"
                            :min="0"
                            :max="1"
                            :interval="0.1"
                            :marks="true"
                            style="margin-left:10px; margin-right:10px; margin-bottom:30px" 
                        ></vue-slider>
                    </div>
                    <div style="width:250px; margin:5px 5px 5px 5px">
                        Sort
                        <b-form-radio-group
                            v-model="sort"
                            :options="['student_id', 'risk']"
                            class="mb-3"
                            style="margin-left:10px; margin-right:10px; margin-bottom:30px" 
                        ></b-form-radio-group>
                    </div>
                        
                </b-dropdown>
                <b-dropdown :text="'Exam '+selected_exam" size="sm" variant="outline-secondary" toggle-class="text-decoration-none" style="float: right;position: absolute;left: 20px;top: 40px;width: 80px; ">
                    <!-- <template v-slot:button-content>
                        <b-icon-gear variant='secondary' size='sm'/>
                    </template> -->
                        <b-dropdown-item @click="onClick">Exam A</b-dropdown-item>
                        <b-dropdown-item @click="onClick">Exam B</b-dropdown-item>
                </b-dropdown>
            </b-card-header>
            <b-card-body style="overflow: scroll; height: 950px; padding:5px" class="macro_card_body">
                <div v-if="overall_cheating_stat">
                    <macro-glyph v-for="(result, i) in selected_exam_result_list" v-bind:key="result.student_id" :student_id="result.student_id" :z_score_threshold="z_score_threshold" :selected_exam="selected_exam" :overall_cheating_stat="overall_cheating_stat" :overall_average_time="overall_average_time" :headpose_weight="headpose_weight" :copy_paste_weight="copy_paste_weight" :blur_focus_weight="blur_focus_weight" :no_face_weight="no_face_weight" :question_cheating_stat="question_cheating_stat" :score='result.total_score' @risk="risk" :display_id="i"/>
                </div>
            </b-card-body>
        </b-card>
    </div>
</template>

<script>
    import * as axios from 'axios'
    import * as d3 from 'd3'
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap-vue/dist/bootstrap-vue.css';
    import VueSlider from 'vue-slider-component'
    import 'vue-slider-component/theme/default.css'

    import { BCard, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormRadioGroup } from 'bootstrap-vue'

    import MacroGlyph from './MacroGlyph'
    //eslint-disable-next-line
    import {RadarChart} from '../assets/RadarChart'

    export default {
        name: 'MacroView',
        props:['all_result_list', 'selected_exam', 'z_score_threshold'],
        components: {
            BCard,
            BCardHeader,
            BCardBody,
            BNavbar,
            BDropdown,
            BDropdownGroup,
            BDropdownItem,
            BIconGear,
            VueSlider,
            MacroGlyph,
            BFormRadioGroup
        },
        data() {
            return {
                selected_exam_result_list: null,
                // overall_cheating_list: null,
                cheating_instances:null,
                // selected_exam: "A",
                z_score_threshold_local: 3,
                headpose_weight:1,
                copy_paste_weight:1,
                blur_focus_weight:1,
                no_face_weight:1,
                overall_cheating_stat:false,
                overall_average_time:false,
                question_cheating_stat:false,
                svg:{
                    height: 130,
                    width_glyph: 200,
                },
                radar: {
                    height: 60,
                    width: 60
                },
                sort:'student_id',
            };
        },
        mounted() {
            this.selected_exam_result_list = this.all_result_list.filter(d=>this.selected_exam==d['student_id'].split("_")[1][0]).sort(this.compare_function)
            // axios.get(`/api/overall_suspicious_case/overall/${this.selected_exam}/${this.z_score_threshold}`).then(response=>{
            //     this.overall_cheating_list = response.data
            // })
            axios.get(`/api/overall_suspicious_case/overall/${this.selected_exam}/${this.z_score_threshold}`).then(response=>{
                this.overall_cheating_stat = response.data
            })
            axios.get(`/api/average_question_time_length/${this.selected_exam}`).then(response=>{
                this.overall_average_time = response.data.data
            })
            axios.get(`/api/overall_suspicious_case/question/${this.selected_exam}/${this.z_score_threshold}`).then(response=>{
                this.question_cheating_stat = response.data
            })
            this.$watch('z_score_threshold_local', (n, o)=>{
                if (n!=o){
                    axios.get(`/api/overall_suspicious_case/overall/${this.selected_exam}/${this.z_score_threshold_local}`).then(response=>{
                        // console.log(this.z_score_threshold)
                        this.overall_cheating_stat = response.data
                    }).then(()=>{
                        axios.get(`/api/overall_suspicious_case/question/${this.selected_exam}/${this.z_score_threshold_local}`).then(response=>{
                            this.question_cheating_stat = response.data
                        })
                    }).then(()=>{
                        this.$emit("changeZScoreThreshold", this.z_score_threshold_local)
                    })
                }
            })
            this.$watch('headpose_weight', (n,o)=>{
                if (n!=o){
                    if (this.copy_paste_weight + this.blur_focus_weight + this.no_face_weight + n == 0){
                        window.alert("Please do not set all weights to 0!")
                        this.headpose_weight = o
                        return
                    }
                }
            })
            this.$watch('copy_paste_weight', (n,o)=>{
                if (n!=o){
                    if (this.headpose_weight + this.blur_focus_weight + this.no_face_weight + n == 0){
                        window.alert("Please do not set all weights to 0!")
                        this.copy_paste_weight = o
                        return
                    }
                }
            })
            this.$watch('blur_focus_weight', (n,o)=>{
                if (n!=o){
                    if (this.headpose_weight + this.copy_paste_weight + this.no_face_weight + n == 0){
                        window.alert("Please do not set all weights to 0!")
                        this.blur_focus_weight = o
                        return
                    }
                }
            })
            this.$watch('no_face_weight', (n,o)=>{
                if (n!=o){
                    if (this.headpose_weight + this.copy_paste_weight + this.blur_focus_weight + n == 0){
                        window.alert("Please do not set all weights to 0!")
                        this.no_face_weight = o
                        return
                    }
                }
            })

            this.$watch('sort', (n,o)=>{
                if (n!=o){
                    this.selected_exam_result_list = this.all_result_list.filter(d=>this.selected_exam==d['student_id'].split("_")[1][0]).sort(this.compare_function)
                }
            })

            this.draw_legend()
        },

        methods: {
            compare_function(a, b){
                if (this.sort == 'student_id'){
                            if (a['student_id']<b['student_id']){
                                return -1
                            }
                            else{
                                return 1
                            }
                        }
                        else{
                            if (a['risk']<b['risk']){
                                return 1
                            }
                            else{
                                return -1
                            }
                        }
            },
            onClick(event){
                // this.selected_exam = event.target.textContent.split(" ")[1]
                this.selected_exam_result_list = this.all_result_list.filter(d=>event.target.textContent.split(" ")[1]==d['student_id'].split("_")[1][0]).sort(this.compare_function)
                axios.get(`/api/overall_suspicious_case/overall/${event.target.textContent.split(" ")[1]}/${this.z_score_threshold}`).then(response=>{
                    this.overall_cheating_stat = response.data
                }).then(()=>{
                    axios.get(`/api/overall_suspicious_case/question/${event.target.textContent.split(" ")[1]}/${this.z_score_threshold}`).then(response=>{
                        this.question_cheating_stat = response.data
                    })
                }).then(()=>{
                    axios.get(`/api/average_question_time_length/${event.target.textContent.split(" ")[1]}`).then(response=>{
                        this.overall_average_time = response.data.data
                    })
                }).then(()=>{
                    this.$emit('changeExamSelection', event.target.textContent.split(" ")[1])
                })
            },
            risk(student_id, value){
                this.selected_exam_result_list.filter(d=>d['student_id']==student_id)[0]['risk'] = value
            },
            draw_legend(){
                //eslint-disable-next-line
                d3.select(`#legend`)
                    .append("svg")
                    .attr("width", this.svg.width_glyph)
                    .attr("height", this.svg.height)
                    .attr('id',`svg_legend`)
                var radarChartOptions = {
                    w: this.radar.width,//Width of the circle
                    h: this.radar.height,
                    x: this.svg.height/2 - 20,
                    y: this.svg.height/2 - 18,
                    levels: 1,
                    maxValue: 1,
                    roundStrokes: false,
                    dotRadius: 2,
                    strokeWidth: 1,
                    opacityArea: 0.25,
                    labelFactor: 0.8,
                    fontsize: '8px',
                    color: d3.scaleOrdinal().range(['rgb(80, 80, 80)', "rgb(59, 119, 176)"]),
                };
                var data = [
                    {"name":"Mean","axes":[{"axis":"blur_focus","alias":"b","value":0.6,"quantile_25":0,"quantile_75":0,"mean":0,"median":0},{"axis":"copy_paste","alias":"c","value":0.33122762148337594,"quantile_25":0,"quantile_75":0,"mean":0,"median":0},{"axis":"no_face","alias":"f","value":0.38745436442084302,"quantile_25":0,"quantile_75":0,"mean":0,"median":0},{"axis":"headpose","alias":"h","value":0.43788819875776397,"quantile_25":0,"quantile_75":0,"mean":0,"median":0}],"color":"rgb(255, 127, 14)"},
                    {"name":"Cheating","axes":[{"axis":"blur_focus","alias":"bf","value":0.5,"quantile_25":0.3,"quantile_75":0.9233333333333334,"mean":0.6,"median":0.55},{"axis":"copy_paste","alias":"cp","value":0.60588235294117646,"quantile_25":0.1,"quantile_75":0.5582352941176471,"mean":0.33122762148337594,"median":0.39411764705882353},{"axis":"no_face","alias":"nf","value":0.7,"quantile_25":0.157251908396946565,"quantile_75":0.8587786259541985,"mean":0.38745436442084302,"median":0.6717557251908396},{"axis":"headpose","alias":"hp","value":0.1,"quantile_25":0.24107142857142858,"quantile_75":0.5654761904761905,"mean":0.43788819875776397,"median":0.4226190476190476}],"color":"rgb(255, 127, 14)"}
                    
                ]
                //eslint-disable-next-line
                var glyph = RadarChart(`#svg_legend`, data, radarChartOptions, this, "")

                var arc = d3.arc()

                d3.select(`#svg_legend`).append('path')
                    .attr('transform', 'translate('+[this.svg.height/2-20, this.svg.height/2-18]+')')
                    .attr('d', ()=>arc({
                            innerRadius: this.radar.width/2,
                            outerRadius: this.radar.width/2+5,
                            startAngle: 0,
                            endAngle: Math.PI*2*0.7
                        }))
                    .style('fill', '#8dd3c7')
                    .style('opacity', 0.8)
                    // .style('stroke', 'pink')
                    // .style('stroke-width', 1)
                
                d3.select(`#svg_legend`).append('path')
                    .attr('transform', 'translate('+[this.svg.height/2-20, this.svg.height/2-18]+')')
                    .attr('d', ()=>arc({
                            innerRadius: this.radar.width/2+6,
                            outerRadius: this.radar.width/2+11,
                            startAngle: 0,
                            endAngle: Math.PI*2*8/14
                        }))
                    .style('fill', '#fdb462')
                    .style('opacity', 0.8)

                var g_legend = d3.select(`#svg_legend`).append('g')
                                .attr('transform', 'translate('+[this.svg.height/2-20, this.svg.height/2-18]+')')
                
                // Legend of error bar
                g_legend.append('path')
                    .attr('d', "M0, -27.8L60, -27.8")
                    .attr('stroke', "rgb(100,100,100)")

                g_legend.append("text")
                    .text('Quartile')
                    .attr('x', 63)
                    .attr('y', -25.5)
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(100,100,100)");

                g_legend.append('path')
                    .attr('d', "M0, -16.5L60, -16.5")
                    .attr('stroke', "rgb(100,100,100)")

                g_legend.append("text")
                    .text('Median')
                    .attr('x', 63)
                    .attr('y', -12.5)
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(100,100,100)");

                g_legend.append('path')
                    .attr('d', "M0, -9L60, -9")
                    .attr('stroke', "rgb(100,100,100)")

                g_legend.append("text")
                    .text('Quartile')
                    .attr('x', 63)
                    .attr('y', 0)
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(100,100,100)");

                g_legend.append('path')
                    .attr('d', "M2, 18L60, 18")
                    .attr('stroke', "rgb(59, 119, 176)")

                g_legend.append("text")
                    .text('Current Student')
                    .attr('x', 63)
                    .attr('y', 23)
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(59, 119, 176)");

                g_legend.append('path')
                    .attr('d', "M-6, 5L60, 5")
                    .attr('stroke', "rgb(100,100,100)")

                g_legend.append("text")
                    .text('Mean')
                    .attr('x', 63)
                    .attr('y', 11)
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(100,100,100)");

                g_legend.append('path')
                    .attr('d', "M0, 32L60, 32")
                    .attr('stroke', '#8dd3c7')

                g_legend.append("text")
                    .text('Time Length')
                    .attr('x', 63)
                    .attr('y', 34)
                    .attr("font-size", "10px")
                    .attr("fill", '#8dd3c7');

                g_legend.append('path')
                    .attr('d', "M0, 39L60, 39")
                    .attr('stroke', '#fdb462')

                g_legend.append("text")
                    .text('Score')
                    .attr('x', 63)
                    .attr('y', 45)
                    .attr("font-size", "10px")
                    .attr("fill", '#fdb462');

                g_legend.append("rect")
                    .attr("x", -12)
                    .attr("y", 18.5215978681898)
                    .attr("width", 10)
                    .attr("height", 10)
                    .attr("fill", "none")
                    .attr("stroke", "rgb(60,60,60)")

                g_legend.append('path')
                    .attr('d', "M-7, 28.52L-7, 47")
                    .attr('stroke', "rgb(60,60,60)")

                g_legend.append("text")
                    .text('Suspicious Type: b (blur & focus), ')
                    .attr('x', -40)
                    .attr('y', 57)
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(60,60,60)");
                g_legend.append("text")
                    .text("c (copy & paste), h (abnormal head")
                    .attr('x', -40)
                    .attr('y', 57)
                    .attr('dy', '1.1em')
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(60,60,60)");
                g_legend.append("text")
                    .text(" pose), f (face disappearance)")
                    .attr('x', -40)
                    .attr('y', 57)
                    .attr('dy', '2.2em')
                    .attr("font-size", "10px")
                    .attr("fill", "rgb(60,60,60)");

            }
        },
    };
</script>

<style>
.large-header{
    padding: 10px 20px 0px 20px;
    height: 45px;
    font-size: 18px
}

.small-header{
    padding: 5px 20px 0px 20px;
    /* height: 33px */
}

</style>