<template>
    <div>
        <b-card no-body style="">
            <!-- <b-card-header class="large-header" >
                Detailed View
                
                <b-form-checkbox v-model="show_risk_in_length" size="lg" switch style="position:absolute; top:5px; left:180px">
                    Risk in length
                </b-form-checkbox>
            </b-card-header> -->
            <b-card-body v-if='overall_cheating_stat' style="overflow: scroll; height: 1090px">
                <meso-card v-for="student_id in selected_student_list" :key="student_id" :student_id='student_id' :z_score_threshold='z_score_threshold_local' :overall_cheating_stat="overall_cheating_stat" :show_risk_in_length="show_risk_in_length">
                </meso-card>
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

    import { BCard, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormCheckbox } from 'bootstrap-vue'

    import MesoCard from './MesoCard'
    import MouseView from './MouseView'

    export default {
        name: 'MesoView',
        props:["selected_student_list", "z_score_threshold", "selected_exam"],
        components: {
            MouseView,
            BCard,
            BCardHeader,
            BCardBody,
            BNavbar,
            BDropdown,
            BDropdownGroup,
            BDropdownItem,
            BIconGear,
            VueSlider,
            MesoCard,
            BFormCheckbox
        },
        data() {
            return {
                overall_cheating_stat: false,
                z_score_threshold_local: this.z_score_threshold,
                show_risk_in_length:true
            };
        },
        mounted() {
            axios.get(`/api/overall_suspicious_case/question/${this.selected_exam}/${this.z_score_threshold}`).then(response=>{
                this.overall_cheating_stat = response.data
            })

            this.$watch("selected_exam", (n, o)=>{
                 if (n!=o){
                    axios.get(`/api/overall_suspicious_case/question/${this.selected_exam}/${this.z_score_threshold}`).then(response=>{
                        this.overall_cheating_stat = response.data
                    })
                 }
            })

            this.$watch("z_score_threshold", (n, o)=>{
                if (n!=o){
                    axios.get(`/api/overall_suspicious_case/question/${this.selected_exam}/${this.z_score_threshold}`).then(response=>{
                        this.overall_cheating_stat = response.data
                    }).then(()=>{
                        this.z_score_threshold_local = this.z_score_threshold
                    })
                }
            })
        },
        methods: {
            initialize() {
                console.log('hello world');
            },
        },
    };
</script>

<style scoped>

</style>