# 🛍️ Fashion Store

Una aplicación de e-commerce moderna y elegante desarrollada con Streamlit, que ofrece una experiencia de compra premium con autenticación OAuth, gestión de carrito y procesamiento de pagos seguro.

Interactúa con el proyecto desplegado aquí:
https://xperience-ecommerce.streamlit.app/

## ✨ Características Principales

- **🔐 Autenticación OAuth con Google**: Inicio de sesión seguro y sin fricciones
- **🛒 Carrito de Compras Inteligente**: Gestión de productos con persistencia en tiempo real
- **💳 Procesamiento de Pagos**: Integración completa con Stripe para pagos seguros
- **📱 Diseño Responsive**: Interfaz moderna y adaptada para todos los dispositivos
- **🔥 Base de Datos Firebase**: Almacenamiento seguro de usuarios, productos y órdenes
- **📊 Gestión de Inventario**: Control automático de stock tras cada compra
- **🎨 UI/UX Premium**: Diseño elegante con CSS personalizado

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Streamlit, HTML/CSS personalizado
- **Backend**: Python
- **Base de Datos**: Firebase Firestore
- **Autenticación**: Google OAuth 2.0
- **Pagos**: Stripe API
- **Almacenamiento**: Firebase Storage
- **Deployment**: Streamlit Cloud

## 📋 Requisitos Previos

- Python 3.8+
- Cuenta de Google Cloud Platform
- Cuenta de Firebase
- Cuenta de Stripe
- Node.js (opcional, para desarrollo frontend)

## ⚙️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/BootcampXperience/DS_Ecommerce_Web_Platform.git
   cd fashion-store
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   
   Crear un archivo `.env` en la raíz del proyecto:
   ```env
   GOOGLE_CLIENT_ID=tu_google_client_id
   GOOGLE_SECRET_ID=tu_google_secret_id
   STRIPE_SECRET_KEY=tu_stripe_secret_key
   ```

4. **Configurar Firebase**
   - Descargar `serviceAccountKey.json` desde Google Console
   - Colocar el archivo en la raíz del proyecto
   - Configurar las reglas de Firestore

5. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

## 📁 Estructura del Proyecto

```
fashion-store/
├── app.py                 # Página principal y autenticación
├── pages/
│   ├── catalogo.py       # Catálogo de productos
│   └── compraok.py       # Confirmación de compra
├── estilos/
│   ├── css_login.html    # Estilos para login
│   ├── css_catalogo.html # Estilos para catálogo
│   └── css_compra.html   # Estilos para compra
├── serviceAccountKey.json # Credenciales Firebase
├── requirements.txt      # Dependencias Python
├── .env                  # Variables de entorno
└── README.md            # Este archivo
```

## 🔧 Configuración Detallada

### Firebase Setup
1. Crear proyecto en Firebase Console
2. Habilitar Authentication (Google)
3. Configurar Firestore Database
4. Crear las siguientes colecciones:
   - `usuarios`: Información de usuarios
   - `products`: Catálogo de productos
   - `carts`: Carritos de compra
   - `orders`: Órdenes completadas

### Google OAuth Setup
1. Ir a Google Cloud Console
2. Crear credenciales OAuth 2.0
3. Configurar URIs de redirección:
   - `http://localhost:8501`
   - Tu dominio de producción

### Stripe Setup
1. Crear cuenta en Stripe
2. Obtener API keys (test/live)

## 🎯 Funcionalidades

### Autenticación
- Login con Google OAuth 2.0
- Creación automática de usuarios
- Gestión de sesiones segura

### Catálogo
- Visualización de productos con imágenes
- Filtrado por categorías
- Información detallada de stock

### Carrito de Compras
- Agregar/quitar productos
- Persistencia en Firebase
- Cálculo automático de totales

### Procesamiento de Pagos
- Integración con Stripe Checkout
- Manejo de pagos exitosos/cancelados

### Gestión de Órdenes
- Guardado automático en Firebase
- Actualización de inventario
- Número de orden único

## 🚀 Deployment

### Streamlit Cloud
1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Subir archivos de configuración
4. Desplegar aplicación

## 🛡️ Seguridad

- ✅ Autenticación OAuth 2.0
- ✅ Validación de datos server-side
- ✅ Encriptación de datos sensibles
- ✅ Manejo seguro de tokens
- ✅ Validación de pagos con Stripe

## 📈 Próximas Mejoras

- [ ] Sistema de reseñas y calificaciones
- [ ] Wishlist de productos
- [ ] Notificaciones push
- [ ] Dashboard de administración
- [ ] Análisis de ventas
- [ ] Múltiples métodos de pago
- [ ] Sistema de cupones y descuentos
- [ ] Chat en vivo con soporte

---

⭐ Si te gusta este proyecto, no olvides darle una estrella en GitHub!
