
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Metrônomo", page_icon="🎵", layout="centered")

st.title("🎵 Metrônomo")
st.caption("Metrônomo em HTML + JavaScript embutido no Streamlit")

html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body{font-family:Arial;text-align:center;background:#f5f7fb}
#bpm{font-size:60px;font-weight:bold;margin:10px}
.row{display:flex;justify-content:center;gap:10px;margin:10px}
button{padding:10px 18px;border:none;border-radius:8px;background:#2563eb;color:white;font-size:16px;cursor:pointer}
button:hover{background:#1d4ed8}
.circle{width:28px;height:28px;border-radius:50%;border:2px solid #888;background:white;display:inline-flex;align-items:center;justify-content:center;margin:4px}
.active-main{background:#ef4444;color:white}
.active-sec{background:#f59e0b;color:white}
.active{background:#3b82f6;color:white}
</style>
</head>
<body>

<div id="bpm">120</div>

<input id="slider" type="range" min="40" max="240" value="120" style="width:80%">
<br><br>

<select id="compasso">
<option value="2">2/4</option>
<option value="3">3/4</option>
<option value="4" selected>4/4</option>
<option value="6">6/8</option>
<option value="9">9/8</option>
<option value="12">12/8</option>
</select>

<div id="beats" style="margin:20px"></div>

<div class="row">
<button onclick="play()">▶ Iniciar</button>
<button onclick="pauseM()">⏸ Pausar</button>
<button onclick="stopM()">⏹ Parar</button>
</div>

<script>

const accents={
2:[0],
3:[0],
4:[0],
6:[0,3],
9:[0,3,6],
12:[0,3,6,9]
}

let bpm=120;
let beat=0;
let timer=null;
let ctx=null;

function audio(){
 if(!ctx) ctx=new(window.AudioContext||window.webkitAudioContext)();
 return ctx;
}

function click(main,sec){
 const c=audio();
 const osc=c.createOscillator();
 const g=c.createGain();
 osc.connect(g);
 g.connect(c.destination);

 osc.frequency.value=main?1000:(sec?900:800);
 g.gain.value=main?0.4:(sec?0.3:0.2);

 g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.1);

 osc.start();
 osc.stop(c.currentTime+0.1);
}

function draw(){
 const beats=parseInt(document.getElementById("compasso").value);
 const div=document.getElementById("beats");
 div.innerHTML="";
 for(let i=0;i<beats;i++){
   const d=document.createElement("div");
   d.className="circle";
   if(i==beat){
      if(i==0)d.classList.add("active-main");
      else if(accents[beats].includes(i))d.classList.add("active-sec");
      else d.classList.add("active");
   }
   d.innerHTML=i+1;
   div.appendChild(d);
 }
}

function tick(){
 const beats=parseInt(document.getElementById("compasso").value);
 const main=(beat==0);
 const sec=accents[beats].includes(beat)&&beat!=0;
 click(main,sec);
 draw();
 beat=(beat+1)%beats;
}

function play(){
 if(timer) return;
 tick();
 timer=setInterval(tick,60000/bpm);
}

function pauseM(){
 clearInterval(timer);
 timer=null;
}

function stopM(){
 pauseM();
 beat=0;
 draw();
}

document.getElementById("slider").oninput=function(){
 bpm=parseInt(this.value);
 document.getElementById("bpm").innerHTML=bpm;
 if(timer){
   pauseM();
   play();
 }
}

document.getElementById("compasso").onchange=function(){
 beat=0;
 draw();
}

draw();
</script>

</body>
</html>
"""

components.html(html,height=520,scrolling=False)
