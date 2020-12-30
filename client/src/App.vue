<template>
  <div id="app">
    <!-- <b-navbar variant="dark" type="dark" style="padding: 0 0 0 20px"> 
      <b-navbar-brand style="font-weight: bold; font-size: 28px">
        VisProctor
      </b-navbar-brand>
    </b-navbar> -->
    <b-container style="width: 100vw;">
      <b-row>
        <b-col cols="2" style="padding: 0 0">
          <macro-view v-if="all_result_list" :all_result_list="all_result_list" :selected_exam="selected_exam" :z_score_threshold="z_score_threshold" @changeZScoreThreshold="changeZScoreThreshold" @changeExamSelection="changeExamSelection"/>
        </b-col>
        <b-col cols='8' style="padding: 0 0">
          <meso-view :selected_student_list="selected_student_list" :z_score_threshold="z_score_threshold" :selected_exam="selected_exam"/>
        </b-col>
        <b-col cols="2" style="padding: 0 0">
          <MouseView></MouseView>
          <screenshot-view />
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import * as axios from 'axios'
// import _ from 'lodash'

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import { BContainer, BRow, BCol, BNavbar, BNavbarBrand } from 'bootstrap-vue';


import MacroView from './components/MacroView';
import MesoView from './components/MesoView';
import MouseView from './components/MouseView'
import ScreenshotView from './components/ScreenshotView'

export default {
  name: 'App',
  components: {
    MacroView,
    MesoView,
    BContainer,
    BRow,
    BCol,
    BNavbar,
    BNavbarBrand,
    MouseView,
    ScreenshotView
  },
  data(){
    return{
      all_result_list:false,
      selected_student_list:[],
      selected_exam: "A",
      z_score_threshold: 3,
    }
  },
  mounted(){
      this.$root.$on("changeStudentSelection", (student_id)=>{
        if (this.selected_student_list.includes(student_id)){
          this.selected_student_list = this.selected_student_list.filter(d=>d!=student_id)
        }
        else{
          this.selected_student_list.push(student_id)
        }
      })
      axios.get("/api/all_result_list").then(response=>{
        this.all_result_list = response.data.data.filter(d=>d['student_id'].split("_")[0]!='linjianxia')
      })
  },
  methods:{
    changeExamSelection(selected_exam){
      this.selected_exam = selected_exam
      this.selected_student_list = []
    },
    changeZScoreThreshold(new_z_score_threshold){
      this.z_score_threshold = new_z_score_threshold
    }

  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}


.container, .container-sm, .container-md, .container-lg, .container-xl {
    max-width: 1920px;
}
</style>
