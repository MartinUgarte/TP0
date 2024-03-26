# TP0: Docker + Comunicaciones + Concurrencia

Alumno: Ugarte, Ricardo Martín

Padrón: 107870

## ¿Cómo está organizado el trabajo práctico?

Cada ejercicio está resuelto en una rama distinta. Si se quiere ver la diferencia entre uno y el anterior, se pueden visualizar los Pull Requests. El código se ejecuta con el comando `make docker-compose-up` salvo para los siguientes apartados:

* Ejercicio 1.1: `python3 ej11.py` (pedirá ingresar cantidad de clientes)
* Ejercicio 3: `make ej3`

## Protocolo de comunicación implementado

El flujo de la lotería es el siguiente:

### 1. Envío de apuestas

El `cliente` (la agencia) va leyendo linea por linea desde su correspondiente archivo de apuestas. De esta forma las va acumulando en un mensaje hasta llegar a la cantidad máxima de apuestas por batch establecida en una constante, para luego enviarlo al `servidor`. Adicionalmente, se agrega en un header la cantidad de bytes a leer y un flag si se trata del último batch o no.

Si por ejemplo `BETS_PER_BATCH = 2` y la agencia $1$ lee las siguientes lineas, suponiendo que aún no llegó al final del archivo:

> Martin,Ugarte,44096365,11-04-2002,1000\
> Daniel,Degarbo,44125682,17-04-2003,7232

Enviará el siguiente mensaje:

> 78-0#Martin,Ugarte,44096365,11-04-2002,1000\tDaniel,Degarbo,44125682,17-04-2003,7232

Como se puede observar, el header y el payload están separados por un `#`, donde se indica que el payload es de 78 bytes y el flag 0 refiere a que aún quedan batchs por recibir. Al mismo tiempo, las apuestas se separan por el caracter especial `\t`

### 2. Recepción de apuestas

El `servidor` (la central) recibirá los batchs y por cada uno se ocupará de decodificarlos, transformándolos a objetos `Bet` y generando una lista para luego usar la función provista por la cátedra `store_bets()` y almacenar las apuestas en el archivo `bets.csv`. Cabe destacar que por cada batch recibido, el servidor manda un `ACK` al cliente para confirmar la recepción y esperar el siguiente batch. La razón es porque el tamaño de los paquetes es variable entonces el servidor no sabrá de antemano cuantos bytes fijos recibir.

### 3. Envío de ganadores

Al recibir completamente todas las apuestas de los 5 clientes, el servidor reconoce las ganadoras leyendo el archivo y envía los DNIs ganadores correspondientes a cada agencia. Por ejemplo a la agencia 1 se le mandarán:

> 8#44096365\
> 8#44125682

Finalmente, el servidor envia un ACK a cada cliente para indicar que se han mandado todos los ganadores con éxito y termina el programa.

## Mecanismos de sincronización utilizados

Para permitir al servidor aceptar conexioens y procesar mensajes en paralelo opté por el uso de procesos de Python con la librería multiprocessing. Por cada cliente entrante se crea un proceso nuevo, el cual recibe un lock y un extremo de escritura de un Pipe

### Lock de escritura

Al momento de escribir en el archivo las apuestas, los procesos comparten un lock para acceder a dicha sección crítica y evitar condiciones de carrera y resultados indeterminísticos.

### Pipes

Por cada proceso que se crea también se crea un Pipe para establecer una comunicación entre el proceso padre y el proceso hijo, que se encarga de toda la conexión con el cliente. El proceso padre se quedará esperando a que el hijo le mande por este canal el número de agencia que representa, que se obtiene luego de haber recibido todas las apuestas de esa agencia. Una vez recibido el quinto número de agencia, querrá decir que todas las agencias han enviado sus jugadas y será el momento del sorteo.