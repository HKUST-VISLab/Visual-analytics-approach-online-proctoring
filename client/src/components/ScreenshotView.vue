<template>
    <b-card no-body style="width: 250px">
        <b-card-header  class="large-header" >
            Screenshots
            <b-icon-trash scale="1" @click="delete_all" style="position:absolute; left:210px; top:10px"/>
            </b-card-header>
        <b-card-body style="height: 660px; padding: 10px 5px 0 5px">
            <div id='screenshot'/>
        </b-card-body>
    </b-card>
</template>

<script>
    // import * as axios from 'axios'
    import 'bootstrap/dist/css/bootstrap.css';
    import 'bootstrap-vue/dist/bootstrap-vue.css';
    import { BCard, BCardHeader, BCardBody, BIconTrash } from 'bootstrap-vue'
    export default {
        name: 'ScreenshotView',
        props: [],
        components: {
            BCard, 
            BCardHeader, 
            BCardBody,
            BIconTrash
        },
        data(){
            return{
                count: 0,
                ratio: false,
                w: 240,
                h: 180
            }
        },
        mounted(){
            this.$root.$on('takeScreenshot', ()=>{
                console.log(this.count)
                this.addScreenshot()
                this.count+=1
            })
            this.video = document.getElementById("id_video")
            // this.video.addEventListener('loadedmetadata', ()=>{
            //         // this.ratio = video.videoWidth / video.videoHeight;
            //         this.w = this.video.videoWidth;
            //         this.h = this.video.videoHeight;
            //     }, false);

        },
        methods:{
            addScreenshot(){
                var canvas = document.createElement('CANVAS');
                var context = canvas.getContext('2d');
                // var w, h, ratio;

                canvas.id = 'screenshot_'+this.count
                canvas.style = "margin: 5px 0"
                
                canvas.width = this.w;
                canvas.height = this.h;

                context.fillRect(0, 0, this.w, this.h);
                context.drawImage(this.video, 0, 0, this.w, this.h);
                document.getElementById("screenshot").appendChild(canvas)
            },
            delete_all(){
                document.getElementById("screenshot").innerHTML = ""
            }
        }
    };
</script>