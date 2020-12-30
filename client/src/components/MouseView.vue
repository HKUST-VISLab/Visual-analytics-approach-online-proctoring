<template>
    <b-card no-body style="width:250px">
            <b-card-header  class="large-header" >Playback View</b-card-header>
            <b-card-body style="padding: 5px 5px 0px 5px;border:0px;height:150px">
                <iframe id="id_iframe" src="frame.html" style="border-width: 0px; width:240px"></iframe>
            </b-card-body>
            <b-card-body style="padding: 0 5px 0px 5px">
                <video id="id_video" style="width:240px; height:180px" poster="default.png" controls>
                    <source :src="vlink +'.avi.mp4'" type="video/mp4" />
                    <!-- <source src="/compressed/yuzhe_B1_mc_1.avi.mp4" type="video/mp4" /> -->
                </video>
            </b-card-body>
        </b-card>
</template>

<script>
    import * as axios from 'axios'
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap-vue/dist/bootstrap-vue.css';
    import { Simpleheat } from '../assets/simpleheat';
    import { BCard, BCardHeader, BCardBody} from 'bootstrap-vue'
    export default {
        name: 'MouseView',
        props: [],
        components: {
            BCard, 
            BCardHeader, 
            BCardBody
        },
        data() {
            return {
                vlink: "",
                maxHei: 0,
                maxWid: 0,
                xspeed: 1,
                vsplition: null,
                pausemouse: false,
            };
        },
        mounted() {
            let that = this;
            axios.get("/splition_anony.json").then(response => {
                that.vsplition = response.data
            })
            this.$root.$on("chooseProblem", (param) => {
                that.vlink = param[1] + "_" + param[0];
                document.getElementById("id_video").load();
                if ((param[1] + "_" + param[0]) == "136125_A_sa_4" || (param[1] + "_" + param[0]) == "142121_B_mc_6" || (param[1] + "_" + param[0]) == "142124_A_mc_6"){
                    document.getElementById("id_video").setAttribute("poster", null)
                }
                else{
                    document.getElementById("id_video").setAttribute("poster", "default.png")
                }
            })
            this.$root.$on("chooseTimestamp", (param) => {
                let userID = param[0];
                let probID = param[1];
                let timeclick = param[2];
                let vpoint = that.vsplition[userID].filter(item => {
                    return item["d_timestamp"] < timeclick
                })
                let current = (timeclick - vpoint[vpoint.length-1]["d_timestamp"])/1000
                document.getElementById("id_video").currentTime = current;
                document.getElementById("id_video").play();
                document.getElementById("id_video").onpause = function() {
                    that.pausemouse = true
                    that.$root.$emit('pause')
                };
                document.getElementById("id_video").onplay = function(){
                    that.pausemouse = false
                    that.$root.$emit('play', document.getElementById("id_video").currentTime)
                };
                document.getElementById("id_video").onseeked = function() {
                    let skip = document.getElementById("id_video").currentTime * 1000;
                    skip += vpoint[vpoint.length-1]["d_timestamp"]
                    that.dataProcess(that.mousedata, skip)
                    // console.log(that.mousedata)
                };
                axios.get("/api/mouse_raw_data_replay/" + userID + "/"+ probID).then(response => {
                    that.pausemouse = false
                    that.mousedata = response.data.data
                    that.dataProcess(response.data.data, timeclick)
                })

            })
            
            this.$root.$on('pauseVideo', ()=>{
                document.getElementById("id_video").pause()
            })

            // document.getElementById("id_video").onpause = () => {
            //     this.$root.$emit('pause')
            // };
            
            // document.getElementById("id_video").onplay = () => {
            //     this.$root.$emit('play', document.getElementById("id_video").currentTime)
            // };

        },
        methods:{
            dataProcess(data, timeclick){
                function compare(a, b) {
                    if (a[2] < b[2]) {
                        return -1;
                    }
                    if (a[2] > b[2]) {
                        return 1;
                    }
                    return 0;
                }
                data.sort(compare);
                let cutindex = 0;
                for (let index = 0; index < data.length; index++) {
                    const element = data[index];
                    if(element[2] > timeclick){
                        cutindex = index;
                        break;
                    }
                }
                data = data.slice(cutindex-1)
                let localdata = data.map(item => {
                    return [item[0]/4.8, item[1], 0, item[2], item[3]/4.8, item[4]]
                })
                localdata[0][2] = 1
                for(let i=0;i<localdata.length-2;){
                    let t=i+1;
                    for(;t<localdata.length;t++){
                        if((localdata[t][3] - localdata[i][3]) > 100){
                            localdata[i][2] = 1
                            i = t
                            break
                        }
                    }
                    if(t == localdata.length){
                        break
                    }
                }
                let docu = document.getElementById("id_iframe").contentWindow.document
                this.maxWid = 240;
                this.maxHei = docu.getElementsByTagName("html")[0].scrollHeight;
                this.localdata = localdata;
                this.drawHeatmap()
            },
            drawHeatmap () {
                let localdata = this.localdata;
                let canvas = document.getElementById("id_iframe").contentWindow.document.getElementById("id_heatmap");
                canvas.width = this.maxWid;
                canvas.height = this.maxHei;
                this.heatmap = Simpleheat(canvas)
                this.heatmap.data([localdata[0]])
                this.heatmap._max = 20
                this.heatmap.radius(5, 2)
                this.heatmap.draw();
                this.addrecord(0)
            },
            addrecord(index){
                let that = this
                if(index >= this.localdata.length-1){
                    // console.log((new Date()).getTime())
                    return;
                }
                if(this.pausemouse){
                    setTimeout(function(){
                        that.addrecord(index)
                    }, 200)
                    return;
                }
                let initIndex = index;
                this.heatmap.add(this.localdata[index++])
                while(index < this.localdata.length-1 && !this.localdata[index][2]){
                    this.heatmap.add(this.localdata[index++])
                }
                setTimeout(function(){
                    let docu = document.getElementById("id_iframe").contentWindow.document
                    let wind = document.getElementById("id_iframe").contentWindow.window
                    wind.scrollTo(that.localdata[index][0] - that.localdata[index][3], that.localdata[index][1] - that.localdata[index][4]);
                    docu.getElementById("id_heatmap").style.top = docu.getElementById("id_bgimg").y + "px";
                    docu.getElementById("id_mouse").style.top = (that.localdata[index][1]) + "px"
                    docu.getElementById("id_mouse").style.left = that.localdata[index][0] +  "px"
                    that.heatmap.draw();
                    that.addrecord(index)
                }, (that.localdata[index][3] - that.localdata[initIndex][3])/that.xspeed)
            },
        }
    };
</script>

<style scoped>

</style>