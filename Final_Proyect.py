from machine import Pin, ADC, I2C
from ssd1306 import SSD1306_I2C
from hcsr04 import HCSR04
from time import sleep, sleep_ms
import network
import time
import urequests
import gc


# Infrarojo = Pin(33, Pin.IN)
reed = Pin(33, Pin.IN)
led_rojo = Pin(5, Pin.OUT)
led_amarrillo = Pin(18, Pin.OUT)
led_verde = Pin(19, Pin.OUT)
i2c = I2C(scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128,64,i2c,0x3c)
sensor = HCSR04(trigger_pin=15, echo_pin=4)
buzzer = Pin(12, Pin.OUT)

# instancia el objeto -sta_if- para controlar la interfaz STA
sta_if = network.WLAN(network.STA_IF);    
# activa la interfaz STA del ESP32
sta_if.active(True)                       
# inicia la conexión con el AP
#reemplazar valores con el nombre y contraseña de la red wifi personal
sta_if.connect("TIGO-EEDD", "2NB112103548")      


"""
IMPORTANTE: esta variable sería para facilitar la modificación del 
            tiempo (en segundo) de espera en cada envío de mensaje a Telegram.
"""
tiempo_espera_mensaje = 5

# Función para hacer sonar el buzzer durante un tiempo específico (en segundos)
def sonar_buzzer(duracion):
    # Hacer que el pin del buzzer esté en estado alto
    buzzer.value(1)  
    # Esperar la duración especificada (en segundos)
    time.sleep(duracion)    
    # Hacer que el pin del buzzer esté en estado bajo
    buzzer.value(0)   


# Función para enviar mensaje a la persona objetiva, desde el Bot
# de Telegram.
def enviar_mensaje(msg: str):
  # El token del Bot que quiere utilizar
  token_bot = "6696026247:AAGY4bSiwDqGEvb_CNfih68nw666ckKnyhA"

  # Aquí es donde se almacena el mensaje que llega del
  # parametro msg
  mensaje = msg

  # Este es el ID objetivo del usuario que recibirá el mensaje
  # para obtener el ID de la cuenta objetivo, puede hacer lo
  # siguiente.

  """
  Una vez creado el bot lo que hacemos es identificar el ID
  del numero objeto donde se enviaran las alertas - este numero 
  sera el de la persona que va manejando el montacargas, lo identificamos
  haciendo que la persona interactue con el bot.

  """
  id_user_objetivo = "6081562648"
  urequests.get(f"https://api.telegram.org/bot{token_bot}/sendMessage?chat_id={id_user_objetivo}&parse_mode=HTML&text={mensaje}")



# Función para modificar la pantalla
def modificar_pantalla(seguir, detente, distancia):
  sleep_ms(50)
  oled.fill(0)
  if seguir:
    oled.text("SIGA",50,10)
  if detente:
    oled.text("STOP",50,10)
  if distancia:
    oled.text("Distancia",30,20)
    oled.text(str(distance),30,35)
    oled.text("cm",30,45)
  oled.show()



print("Estableciendo conexión")
# Bucle infinito hasta que se establezca una conexión, finaliza.
while not sta_if.isconnected():
  print("*", end="")
  time.sleep(0.50)
print("\nConexión con exito")

# Bucle infinito. Este buble nunca finaliza una vez
# entra en ejecución
while True:
  # Leer la distancia en cm
  distance = sensor.distance_cm()

  # Leer valor del infrarojo, donde 1 es cuando se detecta 
  # movimiento y 0 cuando no.
  valor_reed = reed.value()

  # Si la distancia es mayor que 15 cm y menor que 50 cm
  # entonces tiene que escribir en pantalla STOP
  if distance > 15 and distance < 50:
    modificar_pantalla(seguir=False, detente=True, distancia=False)

  # Si la distancia es igual o mayor que 10 cm y menor que 35 cm,
  # entonces deberá de colocar el semáforo en rojo, apagar los otros,
  # colocar en la pantalla STOP y enviar mensaje con ayuda del bot de Telegram
  if distance >= 10 and distance < 35:
    led_rojo.value(1)
    led_amarrillo.value(0)
    led_verde.value(0)
    modificar_pantalla(seguir=False, detente=True, distancia=False)
    enviar_mensaje("<b>Detente\U0000203C, persona pasando  \U0000203C</b>")
    # print("<b>¡¡Detente!!, persona pasando</b>")
    sleep(tiempo_espera_mensaje)
    # Liberar memoria no utilizada utilizando gc.collect()
    gc.collect()

  # Si la distancia es mayor o igual a 35 cm y menor que 43 cm,
  # entonces tendrá que colocar el semáforo en amarillo, apagar los otros,
  # mostrar en pantalla STOP y enviar mensaje con ayuda del bot de Telegram
  if distance >= 35 and distance < 43:
    led_rojo.value(0)
    led_amarrillo.value(1)
    led_verde.value(0)
    modificar_pantalla(seguir=False, detente=True, distancia=False)
    enviar_mensaje("<b> \U0001f300 Persona acercándose</b>")
    # print("<b>Persona acercándose</b>")
    sleep(tiempo_espera_mensaje)
    # Liberar memoria no utilizada utilizando gc.collect()
    gc.collect()

  # Si la distancia es mayor o igual a 43 cm y menor que 50, deberá de colocar
  # el semáforo en Verde, apagar los otros, mostrar en pantalla SIGA y
  # enviar mensaje con ayuda del bot de Telegram.
  if distance >= 43 and distance <50:
    led_rojo.value(0)
    led_amarrillo.value(0)
    led_verde.value(1)
    modificar_pantalla(seguir=True, detente=False, distancia=False)
    enviar_mensaje("<b>\U00002728 Pasillo libre, puede pasar montacargas \U00002714 </b>")
    # print("<b>Pasillo libre, puede pasar montacargas</b>")
    sleep(tiempo_espera_mensaje)
    # Liberar memoria no utilizada utilizando gc.collect()
    gc.collect()

  # Si la distancia es mayor o igual a 50, apagar todo los LED 
  # No mostrar nada en la pantalla
  if distance >= 50:
    led_amarrillo.value(0)
    led_rojo.value(0)
    led_verde.value(0)
    modificar_pantalla(seguir=False, detente=False, distancia=False)

 
  if reed.value() == 0:
    buzzer.on()
    print("IR Sensor Detected!")
    sleep(0.1)
    buzzer.off()

  # mantener bocina apagada si no detecta movimiento
  #if reed.value() == 1:
 # print("¡SIN Movimiento!")
 #   sonar_buzzer(0)
 
    
