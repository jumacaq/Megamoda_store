
import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Cargar variables de entorno
load_dotenv()
#api_key = os.getenv("OPENAI_API_KEY")
api_key = st.secrets["OPENAI_API_KEY"]  # Prioriza el secreto de Streamlit si está disponible

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY no está definido. Verifica tu archivo .env.")

client = OpenAI(api_key=api_key)

def generar_recomendacion(producto, catalogo):
    prompt = f"""
Eres un asesor de moda para una tienda online de ropa.
Un cliente acaba de agregar el siguiente producto a su carrito:
- Nombre: {producto['name']}
- Descripción: {producto['description']}
- Categoría: {producto['category']}

Tu tarea es recomendar un único producto adicional del siguiente catálogo que combine con este producto y mejore su look. Solo debes recomendar productos diferentes al seleccionado.

⚠️ Importante: Si algún producto ya se encuentra en el carrito del cliente, no debes considerarlo en la recomendación.

Catálogo:
{[
    {"name": p['name'], "description": p['description'], "category": p['category']} 
    for p in catalogo if p['name'] != producto['name']
]}

Ahora, genera una recomendación con el siguiente formato amistoso, breve y persuasivo:

¡Excelente elección! 👌  
Para completar tu look, te sugerimos agregar [nombre del producto recomendado], que combina a la perfección con lo que ya elegiste.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Error al generar recomendación: {str(e)}"
