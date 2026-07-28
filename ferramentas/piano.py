import streamlit as st
import streamlit.components.v1 as components


# =====================================================
# PIANO VIRTUAL 3 OITAVAS
# =====================================================

def renderizar_piano_virtual():

    st.subheader("🎹 Piano Virtual - 3 Oitavas")


    st.write(
        "Clique nas teclas para tocar."
    )


    html = """

<!DOCTYPE html>

<html>

<head>

<style>


body{

background:#f5f5f5;
font-family:Arial;

}


.piano{

display:flex;
justify-content:center;
margin-top:30px;
overflow-x:auto;

}


.key{

cursor:pointer;
position:relative;

}


.white{

width:45px;
height:220px;

background:white;

border:1px solid #333;

display:flex;

align-items:flex-end;

justify-content:center;

padding-bottom:15px;

font-size:13px;

font-weight:bold;

}


.white:active{

background:#ddd;

}



.black{

width:30px;

height:130px;

background:#111;

color:white;

margin-left:-15px;

margin-right:-15px;

z-index:2;

display:flex;

align-items:flex-end;

justify-content:center;

padding-bottom:15px;

font-size:10px;

}



.black:active{

background:#555;

}



</style>

</head>


<body>


<div class="piano">



<script>


let audioContext;



function play(freq){


if(!audioContext){

audioContext =
new(window.AudioContext ||
window.webkitAudioContext)();

}



let osc =
audioContext.createOscillator();


let gain =
audioContext.createGain();



osc.type="triangle";


osc.frequency.value=freq;



osc.connect(gain);

gain.connect(
audioContext.destination
);



gain.gain.setValueAtTime(
0.3,
audioContext.currentTime
);



gain.gain.exponentialRampToValueAtTime(

0.001,

audioContext.currentTime + 1

);



osc.start();


osc.stop(
audioContext.currentTime + 1
);



}



const notas = [


["C2",65.41],
["C#2",69.30],
["D2",73.42],
["D#2",77.78],
["E2",82.41],
["F2",87.31],
["F#2",92.50],
["G2",98.00],
["G#2",103.83],
["A2",110.00],
["A#2",116.54],
["B2",123.47],



["C3",130.81],
["C#3",138.59],
["D3",146.83],
["D#3",155.56],
["E3",164.81],
["F3",174.61],
["F#3",185.00],
["G3",196.00],
["G#3",207.65],
["A3",220.00],
["A#3",233.08],
["B3",246.94],



["C4",261.63],
["C#4",277.18],
["D4",293.66],
["D#4",311.13],
["E4",329.63],
["F4",349.23],
["F#4",369.99],
["G4",392.00],
["G#4",415.30],
["A4",440.00],
["A#4",466.16],
["B4",493.88]


];



let pretas = [

"C#",
"D#",
"F#",
"G#",
"A#"

];



notas.forEach(nota=>{


let div =
document.createElement("div");



if(nota[0].includes("#")){


div.className="key black";


}

else{


div.className="key white";


}



div.innerHTML=nota[0];


div.onclick=function(){

play(nota[1]);

};



document.querySelector(".piano")
.appendChild(div);



});



</script>



</div>


</body>

</html>


"""


    components.html(
        html,
        height=350
    )


    st.divider()


    st.markdown(
        """
### 🎼 Próximas evoluções

✅ Mostrar escalas no teclado  
✅ Destacar notas do acorde  
✅ Controle de oitavas  
✅ Gravar sequência tocada  
✅ Modo aula/professor  
"""
    )