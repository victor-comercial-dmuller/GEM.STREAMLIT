import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="GEM Tuner",
    page_icon="🎵",
    layout="wide"
)


html = """

<!DOCTYPE html>

<html>

<head>

<style>


body{

margin:0;
background::#f8fafc;
font-family:Arial,Helvetica,sans-serif;
color:white;

}



.container{

max-width:650px;
margin:auto;
padding:30px;

}



.header{

text-align:center;

}



.logo{

font-size:42px;
font-weight:bold;
color:#1e3a8a;

}



.sub{

color:#64748b;
font-size:18px;
margin-bottom:30px;

}



.card{

background:#0f172a;
border-radius:30px;
padding:35px;
box-shadow:
0 20px 50px rgba(0,0,0,.5);

}



.note{

font-size:100px;
text-align:center;
font-weight:800;
margin-top:20px;

}



.freq{

text-align:center;
font-size:28px;
color:#cbd5e1;

}



.cents{

text-align:center;
font-size:22px;
margin-top:10px;

}



.status{

text-align:center;
font-size:32px;
font-weight:bold;
margin:25px;

}




.scale{

height:25px;
background:#334155;
border-radius:20px;
position:relative;
margin-top:40px;

}



.center{

position:absolute;
left:50%;
height:100%;
width:3px;
background:white;

}



.pointer{

position:absolute;
height:40px;
width:14px;
border-radius:20px;
top:-8px;
left:50%;
background:#22c55e;
transition:.15s;

}



.labels{

display:flex;
justify-content:space-between;
margin-top:10px;
color:#94a3b8;

}



button{


margin-top:35px;
width:100%;
padding:18px;
border:none;
border-radius:18px;

background:#2563eb;

color:white;
font-size:22px;

cursor:pointer;

}



button:hover{

background:#1d4ed8;

}



.info{

margin-top:25px;
padding:20px;
background:#172554;
border-radius:20px;
color:#bfdbfe;
font-size:15px;

}



</style>


</head>


<body>


<div class="container">


<div class="header">


<div class="logo">

🎵 GEM TUNER

</div>


<div class="sub">

Afinador Cromático

</div>


</div>



<div class="card">



<div class="note" id="note">

--

</div>



<div class="freq" id="freq">

0 Hz

</div>



<div class="cents" id="cents">

0 cents

</div>



<div class="status" id="status">

Aguardando...

</div>



<div class="scale">


<div class="center"></div>


<div class="pointer" id="pointer"></div>


</div>


<div class="labels">

<span>-50</span>

<span>0</span>

<span>+50</span>

</div>



<button onclick="startTuner()">

🎤 Iniciar Afinador

</button>



<div class="info">

<b>Como usar:</b>

<br><br>

• Toque uma nota longa e limpa<br>
• Aguarde o reconhecimento<br>
• Centro verde = instrumento afinado<br>
• Funciona com qualquer instrumento

</div>


</div>


</div>






<script>


let audioContext;
let analyser;
let microphoneStream;
let running = false;



async function startTuner(){


if(running){

stopTuner();

return;

}


microphoneStream =
await navigator.mediaDevices.getUserMedia(
{
audio:{
echoCancellation:false,
noiseSuppression:false,
autoGainControl:false
}
}
);



audioContext =
new AudioContext();



const source =
audioContext.createMediaStreamSource(
microphoneStream
);



analyser =
audioContext.createAnalyser();



analyser.fftSize=4096;



source.connect(analyser);



running=true;



document.querySelector("button").innerHTML =
"⏹ Parar Afinador";



detect();


}

function stopTuner(){


running=false;



if(microphoneStream){

microphoneStream
.getTracks()
.forEach(
track=>track.stop()
);

}



if(audioContext){

audioContext.close();

}



document.getElementById(
"note"
).innerHTML="--";



document.getElementById(
"freq"
).innerHTML="0 Hz";



document.getElementById(
"cents"
).innerHTML="0 cents";



document.getElementById(
"status"
).innerHTML="Aguardando...";



document.getElementById(
"pointer"
).style.left="50%";



document.querySelector("button").innerHTML =
"🎤 Iniciar Afinador";


}




function detect(){

if(!running)
return;

let buffer =
new Float32Array(
analyser.fftSize
);



analyser.getFloatTimeDomainData(buffer);



let frequency =
autoCorrelate(
buffer,
audioContext.sampleRate
);



if(
frequency &&
frequency>20 &&
frequency<4000
){


let note =
frequencyToNote(frequency);



let cents =
1200 *
Math.log2(
frequency/note.freq
);



document.getElementById(
"note"
).innerHTML =
note.name;



document.getElementById(
"freq"
).innerHTML =
frequency.toFixed(2)+" Hz";



document.getElementById(
"cents"
).innerHTML =
cents.toFixed(1)+" cents";



let pos =
50+(cents);



if(pos<0)
pos=0;


if(pos>100)
pos=100;



document.getElementById(
"pointer"
).style.left =
pos+"%";




let pointer =
document.getElementById(
"pointer"
);



let status =
document.getElementById(
"status"
);



if(
Math.abs(cents)<=5
){


status.innerHTML =
"✓ AFINADO";


pointer.style.background =
"#22c55e";


}


else if(cents<0){


status.innerHTML =
"⬆ Grave";


pointer.style.background =
"#ef4444";


}

else{


status.innerHTML =
"⬇ Agudo";


pointer.style.background =
"#f59e0b";


}



}



requestAnimationFrame(
detect
);


}








function autoCorrelate(buffer,sampleRate){


let size =
buffer.length;


let rms=0;



for(
let i=0;
i<size;
i++
){

rms+=buffer[i]*buffer[i];

}



rms =
Math.sqrt(
rms/size
);



if(rms<0.01)
return null;



let bestOffset=-1;
let bestCorrelation=0;



for(
let offset=20;
offset<size/2;
offset++
){


let correlation=0;



for(
let i=0;
i<size-offset;
i++
){


correlation +=
buffer[i] *
buffer[i+offset];


}



if(
correlation>bestCorrelation
){

bestCorrelation =
correlation;

bestOffset =
offset;

}


}



if(bestOffset>0)

return sampleRate/bestOffset;



return null;


}








function frequencyToNote(freq){



let names=[

"C",
"C#",
"D",
"D#",
"E",
"F",
"F#",
"G",
"G#",
"A",
"A#",
"B"

];



let midi =
Math.round(
69+
12*
Math.log2(
freq/440
)
);



let octave =
Math.floor(
midi/12
)-1;



let name =
names[
midi%12
]+octave;



let noteFreq =
440*
Math.pow(
2,
(midi-69)/12
);



return {

name:name,

freq:noteFreq

};



}



</script>


</body>

</html>

"""


components.html(
    html,
    height=850,
    scrolling=False
)