import streamlit as st
#import stripe
import paypalrestsdk
import os
from datetime import datetime
import time

# Verificar si el usuario está logueado
if 'login' not in st.session_state:
    st.switch_page('app.py')

# Configuración de Stripe
#stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

paypalrestsdk.configure({
    "mode": "sandbox",
    #"client_id": os.environ.get("PAYPAL_CLIENT_ID"),
    #"client_secret": os.environ.get("PAYPAL_SECRET_KEY"),
    "client_id": st.secrets["PAYPAL_CLIENT_ID"],
    "client_secret": st.secrets["PAYPAL_SECRET_KEY"]
})

# CSS personalizado para el diseño de lujo
with open("estilos/css_compra.html", "r") as file:
    html_content = file.read()
st.markdown(html_content, unsafe_allow_html=True)

def save_order_to_firestore(payment_id, user_id, items, total):
    """Guarda la orden en Firestore"""
    try:
        order_data = {
            'user_id': user_id,
            'user_name': st.session_state['usuario']['nombre'],
            'user_email': st.session_state['usuario']['email'],
            'items': items,
            'total': total,
            'payment_id': payment_id,
            'status': 'completed',
            'created_at': datetime.now(),
            'order_number': f"ORD-{int(time.time())}"
        }
        
        # Guardar en la colección 'orders'
        doc_ref = st.session_state.db.collection('orders').add(order_data)
        
        return order_data['order_number']
        
    except Exception as e:
        st.error(f"Error al guardar la orden: {str(e)}")
        return None

def clear_user_cart(user_id):
    """Limpia el carrito del usuario después de la compra"""
    try:
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_ref.delete()
        # También limpiar carrito en session_state
        st.session_state.cart = []
        
    except Exception as e:
        st.error(f"Error al limpiar carrito: {str(e)}")

#def get_stripe_session_details(session_id):
    #"""Obtiene los detalles de la sesión de Stripe"""
    #try:
        #session = stripe.checkout.Session.retrieve(session_id)
        #return session
    #except Exception as e:
        #st.error(f"Error al obtener detalles de Stripe: {str(e)}")
        #return None

def update_product_stock(items):
    """Actualiza el stock de los productos comprados"""
    try:
        for item in items:
            # Buscar el producto por nombre (en un sistema real usarías ID)
            products_ref = st.session_state.db.collection('products')
            query = products_ref.where('name', '==', item['name'])
            docs = query.stream()
            
            for doc in docs:
                product_data = doc.to_dict()
                new_stock = product_data.get('stock', 0) - item['quantity']
                
                # Actualizar stock
                doc.reference.update({'stock': max(0, new_stock)})
                
    except Exception as e:
        st.error(f"Error al actualizar stock: {str(e)}")
        
def execute_paypal_payment(payment_id, payer_id):
    """
    Ejecuta el pago con PayPal usando el payment_id y el payer_id
    """
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            st.success("✅ Pago exitoso con PayPal!")
            return True
        else:
            st.error(f"❌ Error al ejecutar el pago: {payment.error['message']}")
            return False
    except Exception as e:
        st.error(f"Error de conexión con PayPal: {str(e)}")
        return False

def get_cart_from_firestore(user_id):
    """Obtiene el carrito desde Firestore para el usuario actual"""
    try:
        # Primero intentar desde la colección 'carts'
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_doc = cart_ref.get()
        
        if cart_doc.exists:
            cart_data = cart_doc.to_dict()
            return cart_data.get('items', [])
        else:
            return []
            
    except Exception as e:
        st.error(f"Error al obtener carrito de Firestore: {str(e)}")
        return []

# --- LÓGICA PRINCIPAL ---
st.markdown('''
<div class="success-container">
    <div class="success-icon">🎉</div>
    <h1>¡Compra Realizada!</h1>
    <p>Gracias por tu compra. Tu pedido ya ha sido procesado.</p>
</div>
''', unsafe_allow_html=True)

# Obtener los IDs de PayPal de session_state (vienen de la URL de redirección)
payment_id = st.session_state.get('paypal_payment_id') # Asegúrate de que este se guarde en catalogo.py
payer_id = st.session_state.get('paypal_payer_id')

if not payment_id or not payer_id:
    st.error("❌ No se encontró información del pago de PayPal.")
    if st.button("🔙 Volver al Catálogo"):
        st.switch_page('pages/catalogo.py')
    st.stop()

# Si tenemos los IDs, ejecutamos el pago
with st.spinner('Confirmando el pago con PayPal...'):
    payment_successful = execute_paypal_payment(payment_id, payer_id)
    if not payment_successful:
        st.error("❌ El pago no pudo ser confirmado. Por favor, inténtalo de nuevo.")
        if st.button("🔙 Volver al Catálogo"):
            st.switch_page('pages/catalogo.py')
        st.stop()
        
    # Obtener el carrito desde Firestore
    items_to_save = get_cart_from_firestore(st.session_state['usuario']['uid'])
    if not items_to_save:
        st.error("❌ No se pudieron recuperar los productos del carrito.")
        if st.button("🔙 Volver al Catálogo"):
            st.switch_page('pages/catalogo.py')
        st.stop()
    # Mantener sincronizado session_state
    st.session_state.cart = items_to_save

    # Restaurar el carrito del usuario desde Firestore
    #if not st.session_state.get('cart') or len(st.session_state.cart) == 0:
        #st.session_state.cart = get_cart_from_firestore(st.session_state['usuario']['uid'])
    
    #if not st.session_state.cart:
        #st.error("❌ No se pudieron recuperar los productos del carrito.")
        #if st.button("🔙 Volver al Catálogo"):
            #st.switch_page('pages/catalogo.py')
        #st.stop()
  


#### Obtener detalles de la sesión de Stripe####
# Obtener session_id de session_state (viene desde app.py) o query_params
#session_id = None

# Primer intento: desde session_state (redirección desde app.py)
#if 'stripe_session_id' in st.session_state and st.session_state.get('payment_success', False):
    #session_id = st.session_state['stripe_session_id']

    # Limpiar session_state después de usar
    #del st.session_state['stripe_session_id']
    #del st.session_state['payment_success']

# Segundo intento: desde query_params (acceso directo)
#else:
    #query_params = st.query_params
    #session_id = query_params.get('session_id')

# Verificar si tenemos session_id para proceder
#if not session_id:
    #st.error("❌ No se encontró información del pago.")
    #if st.button("🔙 Volver al Catálogo"):
        #st.switch_page('pages/catalogo.py')
    #st.stop()

# Obtener detalles de la sesión de Stripe
#session = get_stripe_session_details(session_id)

#if not session:
    #st.error("❌ No se pudieron obtener los detalles del pago.")
    #if st.button("🔙 Volver al Catálogo"):
        #st.switch_page('pages/catalogo.py')
    #st.stop()

# Mostrar detalles del pedido
#st.markdown(f'''
#<div class="order-details">
    #<h2>📋 Detalles del Pedido</h2>
    #<div class="order-summary">
        #<strong>Cliente:</strong> {st.session_state['usuario']['nombre']}<br>
        #<strong>Email:</strong> {st.session_state['usuario']['email']}<br>
#<strong>Estado del Pago:</strong> ✅ Completado<br>
        #<strong>ID de Sesión:</strong> {session_id}
    #</div>
#</div>
#''', unsafe_allow_html=True)

# Restaurar carrito si no está en session_state o está vacío
#if not st.session_state.get('cart') or len(st.session_state.cart) == 0:
    #st.session_state.cart = restore_cart_from_firestore(session_id)

# Verificar si tenemos productos para mostrar
#if not st.session_state.cart or len(st.session_state.cart) == 0:
    #st.error("❌ No se pudieron recuperar los productos del carrito.")
    #st.info("💡 Esto puede ocurrir si el carrito se vació antes de completar el pago.")
    #if st.button("🔙 Volver al Catálogo"):
        #st.switch_page('catalogo.py')
    #st.stop()

# Mostrar productos comprados
st.markdown('<h3>🛍️ Productos Comprados</h3>', unsafe_allow_html=True)

# Construir HTML de productos
products_html = ""
total = 0
for item in items_to_save:
    products_html += f'''
    <div class="order-item">
        <div>
            <strong>{item['name']}</strong><br>
            <small>Cantidad: {item['quantity']}</small>
        </div>
        <div>${item['price']:.2f}</div>
    </div>
    '''
    total += item['price'] * item['quantity']

# Mostrar productos y total
st.markdown(products_html, unsafe_allow_html=True)
st.markdown(f'<div class="total-amount">Total: ${total:.2f}</div>', unsafe_allow_html=True)

# Guardar orden en Firestore
order_number = save_order_to_firestore(
    payment_id, 
    st.session_state['usuario']['uid'], 
    items_to_save, 
    total
)

if order_number:
    st.success(f"📝 Número de orden: {order_number}")
    
    # Actualizar stock de productos
    update_product_stock(items_to_save)

    # Limpiar carrito después de guardar la orden
    clear_user_cart(st.session_state['usuario']['uid'])

    # Mostrar mensaje de confirmación
    st.info("📧 Se ha enviado un email de confirmación a tu dirección de correo.")
    
else:
    st.error("❌ Hubo un problema al guardar la orden. Por favor, contacta al soporte.")


# Botón para continuar comprando
st.markdown('''
<div style="text-align: center; margin: 2rem 0;">
</div>
''', unsafe_allow_html=True)
if st.button("🛍️ Continuar Comprando", key="continue_shopping"):
    # Limpiar parámetros de la URL
    st.query_params.clear()
    st.switch_page('pages/catalogo.py')

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem;">
    <p>🛍️ Fashion Store - Gracias por confiar en nosotros</p>
</div>
""", unsafe_allow_html=True)