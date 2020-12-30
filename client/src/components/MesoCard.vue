<template>
    <div>
        <b-card no-body style="border: 0px">
            <!-- <b-card-header class="small-header" style="background-color: rgb(0, 0, 0, 0); border-bottom: 0">
                {{student_id}}
            </b-card-header> -->
            <b-card-body class="meso_card_body" style="padding: 5px 0px 5px 0px">
                <!-- <span>{{student_id}}</span> -->
                <div style="padding: 30px 0; width: 80px;float: left">
                <!-- {{(student_id[0].charCodeAt(0)+20).toString()+(student_id[1].charCodeAt(0)+20).toString()}} -->
                {{student_id.slice(0,6)}}
                </div>
                <div v-if='cheating_instance&&result' style="float: left">
                    <meso-glyph v-for="question_instance in cheating_instance" :key="question_instance['question_id']" :student_id='student_id' :cheating_instance='question_instance' :overall_cheating_stat="overall_cheating_stat[question_instance['question_id']]" :result="get_result(question_instance['question_id'])" :z_score_threshold='z_score_threshold_local' :weights="weights" :show_risk_in_length="show_risk_in_length" @expandMicroView='expand_micro_view'/>
                </div>
                
            </b-card-body>
            <b-card-body v-if='cheating_instance&&result' style="padding: 0 20px 10px 20px">
                <b-collapse id="collapse-4" v-model="micro_view_visible" class="mt-2">
                    <b-card >
                        <b-card-header style="background: rgb(255,255,255); border-bottom:0px">
                            <b-icon-x scale="2" @click="close_micro_view" style="position:absolute; left:1150px; top:15px"/>
                            <b-icon-camera scale="2" @click="take_screenshot" style="position:absolute; left:1100px; top:15px"/>
                        </b-card-header>
                        <micro-view :expand_question_id="expand_question_id" :student_id='student_id' :z_score_threshold="z_score_threshold_local" @expandMicroView='expand_micro_view'/>
                    </b-card>
                </b-collapse>
            </b-card-body>
        </b-card>

    </div>
</template>

<script>
    //eslint-disable-next-line
    import * as axios from 'axios'
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap-vue/dist/bootstrap-vue.css';
    import VueSlider from 'vue-slider-component'
    import 'vue-slider-component/theme/default.css'

    import { BCard, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BCollapse, BIconX, BIconCamera } from 'bootstrap-vue'

    import MesoGlyph from './MesoGlyph'
    import MicroView from './MicroView'

    export default {
        name: 'MesoCard',
        props:["student_id", "z_score_threshold", "overall_cheating_stat", "show_risk_in_length"],
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
            MesoGlyph,
            MicroView,
            BCollapse,
            BIconX,
            BIconCamera
        },
        data() {
            return {
                cheating_instance: false,
                result: false,
                micro_view_visible:false,
                expand_question_id:"",
                z_score_threshold_local: this.z_score_threshold,
                weights: {
                        'headpose_weight': 1,
                        'copy_paste_weight': 1,
                        'blur_focus_weight': 1,
                        'no_face_weight': 1
                }
            };
        },
        mounted() {
            axios.get(`/api/student_suspicious_case/${this.student_id}?threshold=${this.z_score_threshold}&instance=0`).then(response=>{
                this.cheating_instance = Object.values(response.data).sort((a, b)=>{
                    if (a['question_id'].slice(0, 2)==b['question_id'].slice(0, 2)){
                        return parseInt(a['question_id'].split("_")[1]) < parseInt(b['question_id'].split("_")[1])? -1 : 1
                    }
                    else{
                        return a['question_id'].slice(0, 2) - b['question_id'].slice(0, 2)
                    }
                })
            })
            axios.get(`/api/student_result_list/${this.student_id}`).then(response=>{
                // console.log(response)
                this.result = response.data.data
            })

            this.$root.$on('changeWeight', data=>{
                this.weights = data
            })

            this.$watch("z_score_threshold", (n, o)=>{
                if (n!=o){
                    axios.get(`/api/student_suspicious_case/${this.student_id}?threshold=${this.z_score_threshold}&instance=0`).then(response=>{
                        this.cheating_instance = Object.values(response.data).sort((a, b)=>{
                            if (a['question_id'].slice(0, 2)==b['question_id'].slice(0, 2)){
                                return parseInt(a['question_id'].split("_")[1]) < parseInt(b['question_id'].split("_")[1])? -1 : 1
                            }
                            else{
                                return a['question_id'].slice(0, 2) - b['question_id'].slice(0, 2)
                            }
                        })
                    }).then(()=>{
                        this.z_score_threshold_local = this.z_score_threshold
                    })
                }
            })
        },
        methods: {
            get_result(question_id){
                return this.result[`${question_id.slice(0, 2)}_answer`][question_id.slice(3)]=="true"?true:false
            },
            expand_micro_view(question_id){
                if (this.micro_view_visible && question_id == this.expand_question_id){
                    this.micro_view_visible = false
                    this.expand_question_id = ""
                }
                else{
                    this.micro_view_visible = true
                    this.expand_question_id = question_id
                }
                // else if (!this.micro_view_visible){
                //     this.micro_view_visible = true
                //     this.expand_question_id = question_id
                // }
            },
            close_micro_view(){
                this.micro_view_visible = false
                this.expand_question_id = ""
                this.$root.$emit('pauseVideo')
                this.$root.$emit('closeMicro', this.student_id)
            },
            take_screenshot(){
                console.log("screenshot")
                this.$root.$emit('takeScreenshot')
            }

        },
    };
</script>

<style scoped>

</style>