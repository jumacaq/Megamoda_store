import streamlit as st
import stripe
import os
from datetime import datetime
import time
from modules.recomendador import generar_recomendacion


if 'login' not in st.session_state:
    st.switch_page('app.py')

# CSS personalizado para el diseño de lujo
with open("estilos/css_catalogo.html", "r") as file:
    html_content = file.read()
st.markdown(html_content, unsafe_allow_html=True)

# Configuración de Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Funciones de Firestore
def get_products():
    """Obtiene productos desde Firestore"""
    try:
        products_ref = st.session_state.db.collection('products')
        docs = products_ref.stream()
        
        products = []
        for doc in docs:
            product = doc.to_dict()
            product['id'] = doc.id
            products.append(product)
        
        # Si no hay productos, crear algunos de ejemplo
        if not products:
            sample_products = [
                {
                    "name": "Vestido Elegante",
                    "price": 89.99,
                    "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
                    "description": "Vestido elegante perfecto",
                    "category": "vestidos",
                    "stock": 15
                },
                {
                    "name": "Blusa Casual",
                    "price": 45.99,
                    "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400",
                    "description": "Blusa cómoda y versátil para el día a día",
                    "category": "blusas",
                    "stock": 25
                },
                {
                    "name": "Jeans Premium",
                    "price": 79.99,
                    "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
                    "description": "Jeans de alta calidad con corte moderno",
                    "category": "pantalones",
                    "stock": 20
                },
                {
                    "name": "Chaqueta de Cuero",
                    "price": 129.99,
                    "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
                    "description": "Chaqueta de cuero auténtico, estilo urbano",
                    "category": "chaquetas",
                    "stock": 8
                },
                {
                    "name": "Zapatos Elegantes",
                    "price": 95.99,
                    "image": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400",
                    "description": "Zapatos elegantes para completar tu look",
                    "category": "zapatos",
                    "stock": 12
                },
                {
                    "name": "Bolso de Mano",
                    "price": 65.99,
                    "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
                    "description": "Bolso de mano versátil y elegante",
                    "category": "accesorios",
                    "stock": 18
                }
            ]
            
            # Agregar productos de ejemplo a Firestore
            for product in sample_products:
                st.session_state.db.collection('products').add(product)
            
            return sample_products
        
        return products
    
    except Exception as e:
        st.error(f"Error al obtener productos: {str(e)}")
        return []

def add_to_cart(product_id, product_name, product_price, user_id):
    """Agrega producto al carrito"""
    try:
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_doc = cart_ref.get()
        cart_items = []
        
        if cart_doc.exists:
            cart_items = cart_doc.to_dict().get('items', [])

        # Buscar si ya está en el carrito
        product_found = False
        for item in cart_items:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                product_found = True
                break
        if not product_found:
            cart_items.append({
                'product_id': product_id,
                'name': product_name,
                'price': product_price,
                'quantity': 1,
                'added_at': datetime.now()
            })
            
            
        # Guardar el carrito actualizado en Firestore
        # Eliminamos 'session_id' y 'created_at' porque 'updated_at' es más relevante aquí
        # y 'status' de carrito no es necesario, es un carrito no una orden
        cart_ref.set({
            'user_id': user_id,
            'items': cart_items,
            'updated_at': datetime.now() # Campo para saber cuándo fue la última modificación
        })

        return True

          
    except Exception as e:
        st.error(f"Error al agregar al carrito: {str(e)}")
        return False

def remove_from_cart(product_name, user_id):
    """Elimina un producto del carrito"""
    try:
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_doc = cart_ref.get()

        if not cart_doc.exists:
            return

        cart_items = cart_doc.to_dict().get('items', [])
        # Filtrar fuera el producto a eliminar
        updated_items = [item for item in cart_items if item['name'] != product_name]

        # Actualizar en Firestore
        cart_ref.set({
            'user_id': user_id,
            'items': updated_items,
            'updated_at': datetime.now()
        })

        # También actualizar session_state
        st.session_state.cart = updated_items
        
        # 🚨 Marcar recomendación como inactiva tras cualquier modificación
        st.session_state.recomendacion_activa = False
        

    except Exception as e:
        st.error(f"Error al eliminar producto del carrito: {str(e)}")

def get_cart(user_id):
    """Obtiene el carrito del usuario"""
    try:
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_doc = cart_ref.get()
        
        if cart_doc.exists:
            return cart_doc.to_dict().get('items', [])
        return []
    
    except Exception as e:
        st.error(f"Error al obtener carrito: {str(e)}")
        return []

# NUEVA FUNCIÓN: Para simular la creación de la orden y limpieza de carrito
def process_order(user_id, cart_items):
    """Procesa la orden: guarda en 'orders' y limpia 'carts'."""
    try:
        if not cart_items:
            st.warning("El carrito está vacío, no se puede procesar la orden.")
            return False

        total = sum(item['price'] * item['quantity'] for item in cart_items)
        order_data = {
            'user_id': user_id,
            'user_name': st.session_state['usuario']['nombre'],
            'user_email': st.session_state['usuario']['email'],
            'items': cart_items,
            'total': total,
            'status': 'completed', # O 'pending' si quieres un estado intermedio
            'created_at': datetime.now(),
            'order_number': f"ORD-{int(time.time())}-{user_id[:4]}" # Genera un número de orden único
        }

        # Guardar la orden en la colección 'orders'
        st.session_state.db.collection('orders').add(order_data)
        st.success("🎉 ¡Pedido realizado con éxito!")

        # Actualizar stock de productos (opcional aquí, pero recomendado)
        update_product_stock(cart_items)

        # Limpiar el carrito del usuario en Firestore
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_ref.delete()
        
        # Limpiar también el carrito en la sesión de Streamlit
        st.session_state.cart = []

        return True

    except Exception as e:
        st.error(f"Error al procesar la orden: {str(e)}")
        return False

def update_product_stock(items):
    """Actualiza el stock de los productos comprados en Firestore"""
    try:
        for item in items:
            product_ref = st.session_state.db.collection('products').document(item['product_id'])
            product_doc = product_ref.get()

            if product_doc.exists:
                product_data = product_doc.to_dict()
                current_stock = product_data.get('stock', 0)
                new_stock = max(0, current_stock - item['quantity'])

                product_ref.update({'stock': new_stock})
            else:
                st.warning(f"Producto con ID {item['product_id']} no encontrado para actualizar stock.")

    except Exception as e:
        st.error(f"Error al actualizar stock: {str(e)}")

# Funciones de Stripe
#def create_checkout_session(items, user_email):
    #"""Crea una sesión de pago con Stripe"""
    #try:
        #line_items = []
        #for item in items:
           # line_items.append({
                #'price_data': {
                    #'currency': 'usd',
                    #'product_data': {
                        #'name': item['name'],
                        #'images': [item['image']],
                   # },
                    #'unit_amount': int(item['price'] * 100),
               # },
                #'quantity': item['quantity'],
            #})
        
        #checkout_session = stripe.checkout.Session.create(
            #payment_method_types=['card'],
           # line_items=line_items,
            #mode='payment',
            #success_url='http://localhost:8501?payment=success&session_id={CHECKOUT_SESSION_ID}',
            #cancel_url='http://localhost:8501?payment=cancelled',
            #customer_email=user_email,
            #metadata={
                #'user_id': st.session_state['usuario']['uid'],
                #'user_name': st.session_state['usuario']['nombre']
            #}
        #)
        
        #return checkout_session.url, checkout_session.id
    
    #except Exception as e:
        #st.error(f"Error al crear sesión de pago: {str(e)}")
        #return None

# Función para guardar carrito en Firestore
#def save_cart_to_firestore(session_id, user_id, cart_items):
    #"""Guarda el carrito en Firestore antes de ir a Stripe"""
    #try:
        #cart_data = {
            #'session_id': session_id,
            #'user_id': user_id,
            #'items': cart_items,
            #'created_at': datetime.now(),
            #'status': 'pending_payment'
        #}
        
        # Guardar en la colección 'temp_carts' para recuperar después
        #st.session_state.db.collection('carts').document(session_id).set(cart_data)
        
    #except Exception as e:
        #st.error(f"Error al guardar carrito: {str(e)}")

# --- LÓGICA PRINCIPAL DE LA PÁGINA ---
st.markdown('<div class="main-header"><h1>🛍️ Megamoda Store</h1><p>Bienvenido/a a tu tienda de moda</p></div>', unsafe_allow_html=True)

# Sidebar con información del usuario y carrito
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['usuario']['nombre']}")
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
    
    
    st.markdown("---")
    
    # Carrito de compras
    st.markdown("### 🛒 Carrito")
    # NUEVO: Lógica para cargar el carrito desde Firestore una vez por sesión
    if 'cart_loaded' not in st.session_state or not st.session_state.cart_loaded:
        if st.session_state.get('usuario') and st.session_state['usuario'].get('uid'):
            st.session_state.cart = get_cart(st.session_state['usuario']['uid'])
            st.session_state.cart_loaded = True
        else:
            st.session_state.cart = [] # Inicializa como vacío si no hay usuario o UID
            st.session_state.cart_loaded = True # Para evitar intentos repetidos
    # ✅ Mostrar recomendación solo si está activa 
    if st.session_state.get('recomendacion') and st.session_state.get('recomendacion_activa', False):
        st.markdown("---")
        st.markdown("### 🤖 Recomendación personalizada")
        st.info(st.session_state.recomendacion)       
   
    
    if st.session_state.cart:
        total = 0
        for item in st.session_state.cart:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="cart-item">
                    <strong>{item['name']}</strong><br>
                    ${item['price']:.2f} x {item['quantity']}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"remove_{item['name']}"):
                    remove_from_cart(item['name'], st.session_state['usuario']['uid'])
                    st.rerun()  # Recargar para reflejar cambios
            total += item['price'] * item['quantity']
        
        st.markdown(f"**Total: ${total:.2f}**")
        
        # Se asegura que solo exista UN botón de acción final y sin Stripe
        if st.button("✅ Realizar Pedido", key="process_order_button"): # Cambiado key para evitar conflicto
            if process_order(st.session_state['usuario']['uid'], st.session_state.cart):
                st.session_state.recomendacion_activa = False  # Desactivar recomendación tras el pedido
                st.switch_page('pages/compraok.py')
            else:
                st.error("Hubo un problema al finalizar el pedido. Por favor, inténtelo de nuevo.")
                
    

    else:
        st.info("Tu carrito está vacío")

# Contenido principal - Catálogo de productos
st.markdown("## 🛍️ Catálogo de Productos")

# Filtros
col1, col2 = st.columns([1, 3])
with col1:
    categories = ["todos", "vestidos", "blusas", "pantalones", "chaquetas", "zapatos", "accesorios"]
    selected_category = st.selectbox("Categoría", categories)

# Obtener productos
products = get_products()

# Filtrar por categoría
if selected_category != "todos":
    products = [p for p in products if p.get('category') == selected_category]

# Mostrar productos en grid
if products:
    # Crear grid de productos
    cols = st.columns(3)
    
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{product['image']}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 10px;">
                <h3 style="margin: 1rem 0 0.5rem 0; color: #333;">{product['name']}</h3>
                <p style="color: #666; margin-bottom: 1rem;">{product['description']}</p>
                <div class="price-tag">${product['price']:.2f}</div>
                <p style="color: #999; font-size: 0.9rem;">Stock: {product['stock']} unidades</p>
            </div>
            """, unsafe_allow_html=True)
            
            col4, col5, col6 = st.columns([0.5,2,0.5])
            with col5:
                if st.button(f"🛒 Agregar al Carrito", key=f"add_{product.get('id', idx)}"):
                    # Agregar al carrito en memoria (para demo)
                    cart_item = {
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': 1,
                        'image': product['image']
                    }
                    
                    # Verificar si ya existe en el carrito
                    existing_item = next((item for item in st.session_state.cart if item['name'] == product['name']), None)
                    if existing_item:
                        existing_item['quantity'] += 1
                    else:
                        st.session_state.cart.append(cart_item)
                    
                    
                    add_to_cart(product['id'], product['name'], product['price'], st.session_state['usuario']['uid'])
                    # Generar recomendación solo si aún no está en el carrito
                    all_products = get_products()
                    st.session_state.recomendacion = generar_recomendacion(product, all_products)
                    st.session_state.recomendacion_activa = True
                    
                    st.success(f"✅ {product['name']} agregado al carrito!")

                    st.rerun()
  

   
else:
    st.info("No se encontraron productos en esta categoría.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <p>🛍️ Megamoda Store - Tu estilo, nuestra pasión</p>
    <p>Desarrollado con ❤️ usando Streamlit, Firebase y Stripe</p>
</div>
""", unsafe_allow_html=True)



