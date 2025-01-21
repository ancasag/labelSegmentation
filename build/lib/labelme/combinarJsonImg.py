import json
from PIL import Image, ImageDraw
import base64
import os


# Función para cargar el archivo JSON
def cargar_json(json_path):
    with open(json_path, 'r') as json_file:
        return json.load(json_file)


# Función para ajustar las coordenadas a las dimensiones de la imagen actual
def ajustar_coordenadas(puntos, tamaño_original, tamaño_actual, desplazamiento_x=0):
    ancho_original, alto_original = tamaño_original
    ancho_actual, alto_actual = tamaño_actual

    # Calcular los factores de escala
    factor_x = ancho_actual / ancho_original
    factor_y = alto_actual / alto_original

    # Ajustar cada punto según el factor de escala y aplicar el desplazamiento en X
    puntos_ajustados = [((p[0] - desplazamiento_x) * factor_x, p[1] * factor_y) for p in puntos]
    return puntos_ajustados


# Función para crear una máscara a partir de los puntos ajustados
def crear_mascara(imagen_size, puntos_ajustados):
    mascara = Image.new('L', imagen_size, 0)  # Imagen en escala de grises (L), fondo negro
    draw = ImageDraw.Draw(mascara)
    draw.polygon(puntos_ajustados, outline=255, fill=255)  # Dibuja la máscara en blanco
    return mascara


# Función principal para combinar imagen y JSON
def combinar_imagen_y_json(imagen_path, json_path, tamaño_original, salida_imagen_path, salida_json_path,
                           desplazamiento_x):
    # Cargar la imagen
    imagen = Image.open(imagen_path)
    tamaño_actual = imagen.size

    # Cargar el archivo JSON
    data_json = cargar_json(json_path)

    # Extraer las coordenadas de los puntos del primer "shape"
    puntos = data_json['shapes'][0]['points']

    # Ajustar las coordenadas a las dimensiones actuales de la imagen
    puntos_ajustados = ajustar_coordenadas(puntos, tamaño_original, tamaño_actual, desplazamiento_x)

    # Crear una máscara a partir de los puntos ajustados
    mascara = crear_mascara(tamaño_actual, puntos_ajustados)

    # Aplicar la máscara a la imagen original
    imagen_recortada = Image.new("RGBA", tamaño_actual)
    imagen_recortada.paste(imagen, mask=mascara)

    # Guardar la imagen recortada
    imagen_recortada.save(salida_imagen_path)

    # Convertir la imagen recortada a base64
    imagen_base64 = imagen_a_base64(salida_imagen_path)

    # Crear un nuevo JSON con la imagen recortada en base64 y las coordenadas ajustadas
    resultado_json = {
        "imageData": imagen_base64,
        "mask": [puntos_ajustados],  # Guardar la máscara ajustada
    }

    # Guardar el JSON con los datos
    with open(salida_json_path, 'w') as json_file:
        json.dump(resultado_json, json_file, indent=4)

    print(f"Imagen recortada guardada en: {salida_imagen_path}")
    print(f"JSON guardado en: {salida_json_path}")


# Función para convertir la imagen a base64
def imagen_a_base64(imagen_path):
    with open(imagen_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


# Procesar todas las imágenes y archivos JSON en una carpeta
def procesar_carpeta(carpeta, tamaño_original, desplazamiento_x=0):
    # Crear carpeta de salida
    carpeta_salida = os.path.join(carpeta, 'procesados')
    os.makedirs(carpeta_salida, exist_ok=True)
    print("hola")
    # Iterar sobre los archivos de la carpeta
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.JPG'):  # Cambia esto si usas otro formato de imagen
            imagen_path = os.path.join(carpeta, archivo)
            json_path = os.path.join(carpeta, archivo.replace('.JPG', '_D.json'))

            if not os.path.exists(json_path):
                print(f"No se encontró JSON para {archivo}. Saltando...")
                continue

            # Rutas de salida
            salida_imagen_path = os.path.join(carpeta_salida, archivo.replace('.JPG', '_recortada.tif'))
            salida_json_path = os.path.join(carpeta_salida, archivo.replace('.JPG', '_resultado.json'))

            # Procesar imagen y JSON
            combinar_imagen_y_json(
                imagen_path,
                json_path,
                tamaño_original,
                salida_imagen_path,
                salida_json_path,
                desplazamiento_x
            )


# Parámetros de la carpeta y tamaño original
carpeta = 'DJI_202407191107_014/output_ndvi/'  # Cambia esto a la ruta de tu carpeta
tamaño_original = (5280, 3956)  # Tamaño original usado para el JSON
desplazamiento_x = 0  # Ajusta este valor si es necesario

# Ejecutar el procesamiento para la carpeta
procesar_carpeta(carpeta, tamaño_original, desplazamiento_x)
