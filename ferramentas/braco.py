import streamlit as st
import streamlit.components.v1 as components


# =====================================================
# BANCO DE ACORDES
# =====================================================

ACORDES = {

    "C Maior": {
        "E": "X",
        "A": "3",
        "D": "2",
        "G": "0",
        "B": "1",
        "e": "0",
        "dedos": {
            "A": "3",
            "D": "2",
            "B": "1"
        }
    },


    "G Maior": {
        "E": "3",
        "A": "2",
        "D": "0",
        "G": "0",
        "B": "0",
        "e": "3",
        "dedos": {
            "E": "2",
            "A": "1",
            "e": "3"
        }
    },


    "D Maior": {
        "E": "X",
        "A": "X",
        "D": "0",
        "G": "2",
        "B": "3",
        "e": "2",
        "dedos": {
            "G": "1",
            "B": "3",
            "e": "2"
        }
    },


    "A Maior": {
        "E": "X",
        "A": "0",
        "D": "2",
        "G": "2",
        "B": "2",
        "e": "0",
        "dedos": {
            "D": "1",
            "G": "2",
            "B": "3"
        }
    },


    "E Maior": {
        "E": "0",
        "A": "2",
        "D": "2",
        "G": "1",
        "B": "0",
        "e": "0",
        "dedos": {
            "A": "2",
            "D": "3",
            "G": "1"
        }
    },


    "Am (Lá menor)": {
        "E": "X",
        "A": "0",
        "D": "2",
        "G": "2",
        "B": "1",
        "e": "0",
        "dedos": {
            "D": "2",
            "G": "3",
            "B": "1"
        }
    },


    "Em (Mi menor)": {
        "E": "0",
        "A": "2",
        "D": "2",
        "G": "0",
        "B": "0",
        "e": "0",
        "dedos": {
            "A": "2",
            "D": "3"
        }
    },


    "F Maior": {
        "E": "1",
        "A": "3",
        "D": "3",
        "G": "2",
        "B": "1",
        "e": "1",
        "dedos": {
            "E": "1",
            "A": "3",
            "D": "4",
            "G": "2",
            "B": "1",
            "e": "1"
        }
    }

}



# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================

def renderizar_braco_violao():


    st.subheader("🎸 Braço do Violão")


    acorde = st.selectbox(
        "Escolha o acorde",
        list(ACORDES.keys())
    )


    dados = ACORDES[acorde]



    html = f"""

<style>


body {{

font-family: Arial;

}}



.area {{

display:flex;

justify-content:center;

}}



.container {{

background:#eeeeee;

padding:30px;

border-radius:20px;

width:900px;

}}



.titulo {{

text-align:center;

font-size:28px;

font-weight:bold;

color:#333;

margin-bottom:25px;

}}



.linha {{

display:flex;

align-items:center;

height:65px;

}}



.corda_nome {{

width:90px;

font-size:15px;

font-weight:bold;

color:#333;

}}



.casa {{

width:90px;

height:55px;

border-right:3px dashed #222;

display:flex;

align-items:center;

justify-content:center;

position:relative;

}}



.casa::before {{

content:"";

position:absolute;

top:50%;

left:0;

width:100%;

height:3px;

background:#111;

}}



.numero_casa {{

font-size:13px;

font-weight:bold;

color:#555;

height:35px;

}}



.dedo {{

width:42px;

height:42px;

background:#1976d2;

border-radius:50%;

display:flex;

align-items:center;

justify-content:center;

color:white;

font-weight:bold;

font-size:18px;

z-index:2;

}}



.solta {{

font-size:30px;

font-weight:bold;

color:#333;

width:90px;

text-align:center;

}}



.x {{

font-size:25px;

font-weight:bold;

color:#c62828;

width:90px;

text-align:center;

}}



</style>



<div class="area">

<div class="container">


<div class="titulo">

🎸 {acorde}

</div>


"""


    # Cabeçalho das casas

    html += """

<div class="linha">

<div class="corda_nome">

</div>

"""


    for i in range(1,5):

        html += f"""

<div class="casa numero_casa">

{i}

</div>

"""


    html += "</div>"



    # Cordas

    cordas = [
        ("6ª", "E"),
        ("5ª", "A"),
        ("4ª", "D"),
        ("3ª", "G"),
        ("2ª", "B"),
        ("1ª", "e")
    ]



    for numero, corda in cordas:


        html += f"""

<div class="linha">


<div class="corda_nome">

{numero} {corda}

</div>

"""


        valor = dados[corda]



        if valor == "X":

            html += """

<div class="x">

X

</div>

"""


        elif valor == "0":

            html += """

<div class="solta">

○

</div>

"""


        else:


            for casa in range(1,5):


                if casa == int(valor):

                    dedo = dados["dedos"].get(
                        corda,
                        ""
                    )


                    html += f"""

<div class="casa">

<div class="dedo">

{dedo}

</div>

</div>

"""


                else:


                    html += """

<div class="casa">

</div>

"""



        html += "</div>"



    html += """

</div>

</div>

"""



    components.html(
        html,
        height=520
    )


    st.caption(
        """
🔵 Número azul = dedo utilizado

○ = corda solta

X = corda abafada

1 = indicador
2 = médio
3 = anelar
4 = mínimo
"""
    )