# Especificación del sistema web: Qfai — Buscador de Panoramas

## 1. Nombre del sistema

**Qfai — Descubre panoramas en tu ciudad**

---

## 2. Objetivo general

Aplicación web simple para descubrir, publicar y unirse a actividades o panoramas en la ciudad.

El sistema debe permitir:

- Publicar un panorama con título, descripción, categoría, lugar y fecha.
- Ver los panoramas disponibles en una lista y en un mapa.
- Unirse a un panorama.
- Buscar y filtrar panoramas por categoría.

---

## 3. Alcance del sistema

Aplicación web de una sola página, sin servidor, sin build, sin dependencias externas instaladas.

Incluye:

- Un archivo `index.html`.
- Un archivo `styles.css`.
- Un archivo `app.js`.
- Mapa interactivo con Leaflet.js via CDN.
- Datos guardados en localStorage del navegador.
- Diseño minimalista, limpio y mobile-friendly.

No incluye:

- Backend ni base de datos real.
- Autenticación de usuarios.
- Chat ni notificaciones.

---

## 4. Tipo de aplicación

Aplicación web estática monousuario.

Se ejecuta abriendo `src/index.html` en cualquier navegador moderno. No requiere servidor, Node.js, Python ni instalación de ningún tipo.

Tecnologías:

- HTML5.
- CSS3.
- JavaScript vanilla.
- Leaflet.js via CDN para el mapa.
- localStorage para persistencia de datos.

---

## 5. Funcionalidades principales

### 5.1 Ver panoramas

La pantalla principal muestra todos los panoramas publicados.

Cada panorama muestra:

- Título.
- Categoría (con ícono o badge de color).
- Lugar de referencia.
- Fecha y hora.
- Número de personas anotadas.
- Botón "Unirme" o "Ya anotado".

Los panoramas se ordenan por fecha ascendente (próximos primero).

---

### 5.2 Publicar un panorama

El usuario puede publicar un nuevo panorama desde un formulario.

Campos requeridos:

- Título (obligatorio, mínimo 5 caracteres).
- Descripción (opcional).
- Categoría (lista: Deporte, Música, Arte, Gastronomía, Naturaleza, Social, Otro).
- Ciudad y lugar de referencia (texto libre).
- Fecha y hora (debe ser futura).

Al publicar, el panorama aparece en la lista y en el mapa.

---

### 5.3 Mapa de panoramas

La pantalla principal incluye un mapa con marcadores por cada panorama.

- Mapa con OpenStreetMap via Leaflet.js.
- Al hacer clic en un marcador se muestra el título y la fecha del panorama.
- La ubicación en el mapa se asigna de forma aproximada según la ciudad ingresada (coordenadas predefinidas por ciudad o ingresadas manualmente).

---

### 5.4 Filtrar por categoría

El usuario puede filtrar panoramas por categoría mediante botones o un selector.

Filtros disponibles:

- Todos.
- Deporte.
- Música.
- Arte.
- Gastronomía.
- Naturaleza.
- Social.
- Otro.

---

### 5.5 Unirse a un panorama

El usuario puede marcar que se une a un panorama.

- El botón cambia a "Ya anotado" al unirse.
- El contador de personas anotadas aumenta en 1.
- El estado persiste en localStorage.
- El usuario puede desanotarse haciendo clic nuevamente.

---

## 6. Requisitos no funcionales

### RNF-01 Sin instalación
La app se abre directo desde `src/index.html` en el navegador.

### RNF-02 Diseño minimalista
Interfaz limpia, espaciada, con colores suaves y tipografía clara. Paleta: blanco, gris claro y un color de acento (violeta o coral).

### RNF-03 Mobile-friendly
Debe verse bien en pantalla de celular y en escritorio.

### RNF-04 Persistencia
Los panoramas publicados y los "me uno" persisten al recargar usando localStorage.

### RNF-05 Compatibilidad
Funciona en Chrome, Firefox, Edge y Safari modernos.

---

## 7. Flujo principal del usuario

1. El usuario abre `index.html` en el navegador.
2. Ve la lista de panoramas disponibles y el mapa.
3. Filtra por categoría si quiere.
4. Hace clic en "Publicar panorama" y completa el formulario.
5. El panorama aparece en la lista y en el mapa.
6. El usuario hace clic en "Unirme" en un panorama que le interesa.
7. El contador sube y el botón cambia a "Ya anotado".

---

## 8. Casos de uso

### Caso de uso 1: Publicar un panorama

Flujo:

1. Usuario presiona "Publicar panorama".
2. Completa título, categoría, lugar y fecha.
3. Presiona "Publicar".
4. Sistema valida que el título no esté vacío y la fecha sea futura.
5. Sistema guarda en localStorage y muestra el panorama en la lista y el mapa.

Resultado: El panorama queda visible para todos.

---

### Caso de uso 2: Unirse a un panorama

Flujo:

1. Usuario ve un panorama en la lista.
2. Presiona "Unirme".
3. El botón cambia a "Ya anotado".
4. El contador de personas sube en 1.
5. El estado se guarda en localStorage.

Resultado: El usuario queda anotado y persiste al recargar.

---

### Caso de uso 3: Filtrar por categoría

Flujo:

1. Usuario presiona el botón de una categoría (ej: "Deporte").
2. La lista muestra solo los panoramas de esa categoría.
3. El mapa actualiza los marcadores visibles.

Resultado: El usuario ve solo los panoramas relevantes.

---

## 9. Criterios de aceptación

El sistema se considera terminado cuando:

- Se abre `src/index.html` sin errores en el navegador.
- Se muestran los panoramas de ejemplo al cargar.
- Se puede publicar un nuevo panorama.
- No se puede publicar sin título.
- No se puede publicar con fecha pasada.
- El panorama nuevo aparece en la lista.
- El panorama nuevo aparece en el mapa.
- Se puede filtrar por categoría.
- El filtro "Todos" muestra todos los panoramas.
- Se puede hacer clic en "Unirme".
- El contador de anotados sube al unirse.
- El estado persiste al recargar la página.
- La interfaz se ve bien en móvil y en escritorio.

---

## 10. Checklist de pruebas

```text
[ ] index.html abre sin errores.
[ ] Se muestran panoramas de ejemplo al cargar.
[ ] El mapa carga con Leaflet.js.
[ ] Los marcadores aparecen en el mapa.
[ ] Al hacer clic en un marcador se muestra el título.
[ ] Se puede abrir el formulario de publicación.
[ ] No se puede publicar sin título.
[ ] No se puede publicar con fecha pasada.
[ ] El panorama nuevo aparece en la lista.
[ ] El panorama nuevo aparece en el mapa.
[ ] El filtro por categoría funciona.
[ ] El filtro "Todos" funciona.
[ ] El botón "Unirme" cambia a "Ya anotado".
[ ] El contador de anotados aumenta.
[ ] Los datos persisten al recargar la página.
[ ] La interfaz se adapta a pantalla de móvil.
[ ] La interfaz se adapta a pantalla de escritorio.
```

---

## 11. Estructura de archivos

```text
src/
  index.html
  styles.css
  app.js
README.md
```

---

## 12. Datos de ejemplo iniciales

Al cargar por primera vez, el sistema debe mostrar al menos 3 panoramas de ejemplo con datos realistas, distintas categorías y ubicaciones distintas en el mapa.

---

## 13. Definición final del producto mínimo viable

El producto mínimo viable es una aplicación web estática llamada **Qfai**, desarrollada en HTML, CSS y JavaScript vanilla, con mapa Leaflet.js y persistencia en localStorage.

Permite publicar panoramas, verlos en lista y mapa, filtrar por categoría y anotarse. No requiere instalación, servidor ni dependencias. Se abre directamente en el navegador.
